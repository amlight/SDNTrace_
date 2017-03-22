"""
    Tracer main class
"""
from datetime import datetime
from ryu.lib import hub
from libs.tracing.trace_pkt import generate_trace_pkt, prepare_next_packet


class TracePath(object):
    """
        Tracer main class - responsible for everything once a user
        requests a tracer. It is composed of two parts:
         1) Sending PacketOut messages to switches
         2) Reading the obj.trace_pktIn queue with PacketIn received

        There are a few possibilities of result (not counting errors):
        - Timeouts ({'trace': 'completed'}) - even positive results end w/
            timeouts.
        - Loops ({'trace': 'loop'}) - everytime an entry is seem twice
            in the trace_result queue, we stop

        Some things to take into consideration:
        - we can have parallel traces
        - we can have flow rewrite along the path (vlan translation, f.i)
    """

    def __init__(self, sdntrace_class, r_id, initial_entries):
        self.obj = sdntrace_class
        self.switches = self.obj.switches
        self.id = r_id
        self.init_entries = initial_entries
        self.trace_result = []
        self.trace_ended = False
        self.init_switch = None
        self.start_time = self.current_time()

    def initial_validation(self):
        dpid = self.init_entries['trace']['switch']['dpid']
        self.init_switch = self.obj.get_switch(dpid, by_name=True)
        if not isinstance(self.init_switch, bool):
            return True
        return 'Error: DPID provided was not found'

    def current_time(self):
        return datetime.now()

    def get_time(self, to_str=True):
        time_diff = self.current_time() - self.start_time
        return str(time_diff) if to_str else time_diff

    def add_trace_step(self, trace_type, reason=None, dpid=None, port=None, msg=None):
        """
            Used to define the new REST interface. Use docs/trace_results.txt for
                examples. Only this method should write to self.trace_result
            Args:
                trace_type: type of trace
                reason: reason in case trace_type == last
                dpid: switch's dpid
                port: switch's OpenFlow port_no
                msg: message in case of reason == error
        """
        step = dict()
        step['type'] = trace_type
        # Get port name instead of port_no
        if dpid:
            new_switch = self.obj.get_switch(dpid, by_name=True)
            port_name = new_switch.ports[port]['name']

        if trace_type == 'starting':
            step['dpid'] = new_switch.name
            step['port'] = port_name
            step['time'] = str(self.start_time)
        elif trace_type == 'trace':
            step['dpid'] = new_switch.name
            step['port'] = port_name
            step['time'] = self.get_time()
        elif trace_type == 'last':
            step['reason'] = reason
            step['msg'] = msg
            step['time'] = self.get_time()
        elif trace_type == 'intertrace':
            pass
        # Add to trace_result array
        self.trace_result.append(step)

    def tracepath(self):
        """
            Do the trace path
        """
        print("Starting Trace Path for ID %s" % self.id)
        entries = self.init_entries
        color = self.init_switch.color
        switch = self.init_switch
        # Add initial trace step
        self.add_trace_step(trace_type='starting', dpid=switch.datapath_id,
                            port=entries['trace']['switch']['in_port'])

        # A loop waiting for trace_ended. It changes to True when reaches timeout
        while not self.trace_ended:
            """
                The logic is very simple:
                1 - Generate the probe packet using entries provided
                2 - Results a result and the packet_in (used to generate new probe)
                    Possible results: 'timeout' meaning the end of trace
                                      or the trace step {'dpid', 'port'}
                    Some networks do vlan rewrite, so it is important to get the
                    packetIn msg with the header
                3 - If result is a trace step, send PacketOut to the switch that
                    originated the PacketIn. Repeat till reaching timeout
            """
            # Generate the probe packet
            in_port, probe_pkt = generate_trace_pkt(entries, color, self.id)
            # Send Packet out and try to get a PacketIn
            result, packet_in = self.send_trace_probe(switch, in_port, probe_pkt)
            # If timeout
            if result == 'timeout':
                # Add last trace step
                self.add_trace_step(trace_type='last', reason='done')
                print("Trace Completed!")
                self.trace_ended = True
            # If not timeout
            else:
                self.add_trace_step(trace_type='trace', dpid=result['dpid'], port=result['port'])
                is_loop = self.check_loop()
                if is_loop:
                    # If loop, add the loop trace step
                    self.add_trace_step(trace_type='last', reason='loop')
                    self.trace_ended = True
                    break
                # If we got here, that means we need to keep going.
                # Prepare next packet
                prepare = prepare_next_packet
                entries, color, switch = prepare(self.obj, entries, result, packet_in)

        # Identify next hop to confirm if inter-domain
        # If so, get the contract file
        is_inter_domain = False

        if is_inter_domain:
            self.trace_interdomain()

        # Add final result to trace_results_queue
        self.obj.trace_results_queue[self.id] = {"request_id": self.id,
                                                 "result": self.trace_result,
                                                 "start_time": str(self.start_time),
                                                 "total_time": self.get_time()}

    def send_trace_probe(self, switch, in_port, probe_pkt):
        """
            This method sends the PacketOut and checks if the
            PacketIn was received in 3 seconds.
            Args:
                switch: target switch to start with
                in_port: target port to start with
                probe_pkt: ethernet frame to send (PacketOut.data)
            Returns:
                Timeout
                {switch & port}
        """
        timeout_control = 0  # Controls the timeout of 1 second and two tries

        print('Tracer: Sending POut to switch: %s and in_port %s '
              % (switch.name, in_port))
        switch.send_packet_out(in_port, probe_pkt.data)

        while True:
            hub.sleep(0.5)  # Wait 0.5 second before querying for PacketIns
            timeout_control += 1
            # Check if there is any Probe PacketIn in the queue
            if len(self.obj.trace_pktIn) is 0:
                if timeout_control > 2:
                    return 'timeout', False
                else:
                    print('Sending PacketOut Again')
                    switch.send_packet_out(in_port, probe_pkt.data)
            else:
                # There are probes in the PacketIn queue
                for pIn in self.obj.trace_pktIn:
                    # Let's look for one with our self.id
                    # Each entry has the following format:
                    # (pktIn_dpid, pktIn_port, pkt[-1], pkt, ev)
                    if self.id == int(pIn[2]):
                        self.clear_trace_pkt_in()
                        return {'dpid': pIn[0], "port": pIn[1]}, pIn[4]

    def clear_trace_pkt_in(self):
        """
            Once the probe PacketIn was processed, delete it from queue
        """
        for pIn in self.obj.trace_pktIn:
            if self.id == int(pIn[2]):
                self.obj.trace_pktIn.remove(pIn)

    def check_loop(self):
        """
            Check if there are equal entries
        """
        i = 0
        last = len(self.trace_result) - 1
        while i < last:
            # print i, last
            if self.trace_result[i] == self.trace_result[last]:
                return last
            i += 1
        return 0

    def trace_interdomain(self):
        # Inter-domain operations start here...
        # Rewrite trace
        pass
