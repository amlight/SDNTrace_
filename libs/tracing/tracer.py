"""
    Tracer main class
"""

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

    def initial_validation(self):
        dpid = self.init_entries['trace']['switch']['dpid']
        self.init_switch = self.obj.get_switch(dpid, by_name=True)
        if not isinstance(self.init_switch, bool):
            return True
        return 'Error: DPID provided was not found'

    def tracepath(self):
        """
            Do the trace path
        """
        print("Starting Trace Path for ID %s" % self.id)
        entries = self.init_entries
        color = self.init_switch.color
        switch = self.init_switch

        while not self.trace_ended:
            # Generate the probe packet
            in_port, probe_pkt = generate_trace_pkt(entries, color, self.id)
            # Send Packet out
            result, packet_in = self.send_trace_probe(switch, in_port, probe_pkt)

            # If time out, packetIn will be False
            if 'done' in result['trace']:
                print("Trace Completed!")
                self.trace_ended = True
            else:
                self.trace_result.append(result)
                is_loop = self.check_loop()
                if is_loop:
                    self.trace_result.append({'trace': 'loop'})
                    self.trace_ended = True
                    break
                # If we got here, that means we need to keep going.
                # Prepare next packet
                prepare = prepare_next_packet
                entries, color, switch = prepare(self.obj, entries, result, packet_in)

        self.trace_result.append({'trace': 'completed'})
        # Add trace result to SDNTrace.traces dictionary
        self.obj.trace_results_queue[self.id] = (self.trace_result)
        # Inter-domain operations start here...
        # Identify next hop
        # Check contract to see if there any another domain
        # If so, rewrite trace

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
        timeout_control = 0  # Controls the timeout of 2 seconds
        rest_result = {}

        print('Tracer: Sending POut to switch: %s and in_port %s '
              % (switch.name, in_port))
        switch.send_packet_out(in_port, probe_pkt.data)

        while True:
            hub.sleep(0.5)  # Wait 1 second
            timeout_control += 1
            # Check if there is any Probe PacketIn in the queue
            if len(self.obj.trace_pktIn) is 0:
                if timeout_control > 2:
                    print('Timeout reached')
                    return {'trace': 'done'}, False
                else:
                    print('Sending PacketOut Again')
                    switch.send_packet_out(in_port, probe_pkt.data)
            else:
                # There are probes in the PacketIn queue
                for pIn in self.obj.trace_pktIn:
                    # Let's look for one with our ID
                    # Each entry has the following format:
                    # (pktIn_dpid, pktIn_port, pkt[-1], pkt, ev)
                    if self.id == int(pIn[2]):
                        rest_result['trace'] = {'dpid': pIn[0], "port": pIn[1]}
                        self.clear_trace_pkt_in()
                        return rest_result, pIn[4]

    def clear_trace_pkt_in(self):
        """
            Once the probe PacketIn was processed, delete from queue
        """
        for pIn in self.obj.trace_pktIn:
            if self.id == int(pIn[2]):
                self.obj.trace_pktIn.remove(pIn)

    def check_loop(self):
        """
            Check if there are two equal entries
        """
        i = 0
        last = len(self.trace_result) - 1
        while i < last:
            # print i, last
            if self.trace_result[i] == self.trace_result[last]:
                return last
            i += 1
        return 0
