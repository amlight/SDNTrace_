"""
    Tracer main class
"""


from ryu.lib import hub
from libs.core.config_reader import ConfigReader
from libs.rest.tracer import FormatRest
from libs.topology.switches import Switches
from apps.tracing.trace_msg import TraceMsg
from apps.tracing.trace_pkt import generate_trace_pkt, prepare_next_packet


class TracePath(object):
    """
        Tracer main class - responsible for running a tracer.
        It is composed of two parts:
         1) Sending PacketOut messages to switches
         2) Reading the obj.trace_pktIn queue with PacketIn received

        There are a few possibilities of result (except for errors):
        - Timeouts ({'trace': 'completed'}) - even positive results end w/
            timeouts.
        - Loops ({'trace': 'loop'}) - every time an entry is seen twice
            in the trace_result queue, we stop

        Some things to take into consideration:
        - we can have parallel traces
        - we can have flow rewrite along the path (vlan translation, f.i)
    """

    def __init__(self, trace_manager, r_id, initial_entries):
        self.switches = Switches()
        self.trace_mgr = trace_manager
        self.id = r_id
        self.init_entries = initial_entries
        self.trace_result = []
        self.trace_ended = False
        self.init_switch = self.get_init_switch()
        self.rest = FormatRest()
        self.config = ConfigReader()

        # Support for inter-domain
        self.inter_domain = self.trace_mgr.is_interdomain(self.id)
        self.mydomain = self.config.interdomain.my_domain

    def get_init_switch(self):
        """
        
            Returns:

        """
        dpid = self.init_entries['trace']['switch']['dpid']
        return Switches().get_switch(dpid, by_name=True)

    def tracepath(self):
        """
            Do the trace path
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
        print("Starting Trace Path for ID %s" % self.id)
        entries = self.init_entries
        color = self.init_switch.color
        switch = self.init_switch
        # Add initial trace step
        self.rest.add_trace_step(self.trace_result, trace_type='starting',
                                 dpid=switch.datapath_id,
                                 port=entries['trace']['switch']['in_port'])

        # A loop waiting for trace_ended. It changes to True when reaches timeout
        while not self.trace_ended:
            in_port, probe_pkt = generate_trace_pkt(entries, color, self.id, self.mydomain)
            result, packet_in = self.send_trace_probe(switch, in_port, probe_pkt)

            if result == 'timeout':
                self.rest.add_trace_step(self.trace_result, trace_type='last')
                print("Intra-Domain Trace Completed!")
                self.trace_ended = True
            else:
                self.rest.add_trace_step(self.trace_result, trace_type='trace',
                                         dpid=result['dpid'], port=result['port'])
                if self.check_loop():
                    self.rest.add_trace_step(self.trace_result, trace_type='last',
                                             reason='loop')
                    self.trace_ended = True
                    break
                # If we got here, that means we need to keep going.
                # Prepare next packet
                prepare = prepare_next_packet
                entries, color, switch = prepare(Switches(), entries, result, packet_in)

        # Check if the last switch has inter-domain neighbors
        # if so, infer is current flows go through the interdomain port
        if switch.is_inter_domain:
            out_port = switch.match_flow(in_port, probe_pkt)
            if out_port in switch.inter_domain_ports.keys():
                neighbor_conf = switch.inter_domain_ports[out_port]
                self.trace_interdomain(switch, neighbor_conf.color_value, entries, in_port)

        # Add final result to trace_results_queue
        # if inter_domain, add a status to the result, f. i, 'running'
        t_result = {"request_id": self.id, "result": self.trace_result,
                    "start_time": str(self.rest.start_time),
                    "total_time": self.rest.get_time()}

        self.trace_mgr.add_result(self.id, t_result)

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
            if timeout_control >= 3:
                return 'timeout', False

            if len(self.trace_mgr.trace_pktIn) is 0:
                print('Sending PacketOut Again')
                switch.send_packet_out(in_port, probe_pkt.data)
            else:
                # There are probes in the PacketIn queue
                for pIn in self.trace_mgr.trace_pktIn:
                    # Let's look for one with our self.id
                    # Each entry has the following format:
                    # (pktIn_dpid, pktIn_port, pkt[-1], pkt, ev)
                    # packetIn_data_request_id is the request id
                    # of the packetIn.data.
                    msg = TraceMsg()
                    msg.import_data(pIn[2])
                    if self.id == msg.request_id:
                        self.clear_trace_pkt_in()
                        return {'dpid': pIn[0], "port": pIn[1]}, pIn[4]

    def clear_trace_pkt_in(self):
        """
            Once the probe PacketIn was processed, delete it from queue
        """
        for pIn in self.trace_mgr.trace_pktIn:
            msg = TraceMsg()
            msg.import_data(pIn[2])
            if self.id == msg.request_id:
                self.trace_mgr.trace_pktIn.remove(pIn)

    def check_loop(self):
        """
            Check if there are equal entries
        """
        i = 0
        last = len(self.trace_result) - 1
        while i < last:
            if self.trace_result[i] == self.trace_result[last]:
                return last
            i += 1
        return 0

    def trace_interdomain(self, switch, neighbor_color, entries, in_port):
        """
        
            Args:
                switch: 
                neighbor_color: 
                entries: 
                in_port: 
    
            Returns:

        """
        # Inter-domain operations start here...
        # Rewrite trace
        print('Inter-Domain Trace Started!')
        # Customize a trace_pkt
        # Assuming switch.color (intra) is different
        # from neighbor.color (inter), creates a probe packet
        # If switch.color == neighbor.color, it is not going to work
        # with dl_src it wont be a problem because we can use ranges
        # if we move to a limited field (vlan_pcp), it is important to
        # make sure colors are not the same
        _, probe_pkt = generate_trace_pkt(entries, neighbor_color, self.id,
                                          self.mydomain, interdomain=True)
        # Send a packet-out
        switch.send_packet_out(in_port, probe_pkt.data)
        print('Inter-Domain Trace: Packet Out sent!')
        # How many packet outs to send? Just one for now
