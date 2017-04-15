"""
    Tracer main class
"""
from ryu.lib import hub
from libs.tracing.trace_pkt import generate_trace_pkt, prepare_next_packet
from libs.core.rest.tracer import FormatRest
from libs.tracing.trace_msg import TraceMsg


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
        self.rest = FormatRest(self.obj)
        # Support for inter-domain
        self.inter_domain = False
        self.remote_server = False
        self.mydomain = self.obj.config_vars['inter-domain']['my_domain']
        self.check_if_interdomain()

    def initial_validation(self):
        """
            Make sure the switch selected by the user exists.
            In fact, this method has to validate all params inputed.
        Returns:
            True: all set
            False: switch requested doesn't exist

        """
        dpid = self.init_entries['trace']['switch']['dpid']
        self.init_switch = self.obj.get_switch(dpid, by_name=True)
        if not isinstance(self.init_switch, bool):
            return True
        return 'Error: DPID provided was not found'

    def check_if_interdomain(self):
        src_switch = self.init_entries['trace']['switch']['dpid']
        src_port = self.init_entries['trace']['switch']['in_port']

        locals = self.obj.config_vars['inter-domain']['locals'].split(',')
        for local in locals:
            if local.split(':')[0] == src_switch and int(local.split(':')[1]) == src_port:
                self.inter_domain = True
                try:
                    # if a trace starts in an inter-domain port but it is a intra test
                    # there is no request id
                    self.remote_request_id = self.init_entries['trace']['data']['request_id']
                except:
                    self.inter_domain = False
                break
        if self.inter_domain:
            neighbors = self.obj.config_vars['inter-domain']['neighbors'].split(',')
            for neighbor in neighbors:
                if self.obj.config_vars[neighbor]['local'].split(':')[0] == src_switch:
                    self.remote_server = self.obj.config_vars[neighbor]['service']
                    break

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
                # Add last trace step
                self.rest.add_trace_step(self.trace_result, trace_type='last')
                print("Intra-Domain Trace Completed!")
                self.trace_ended = True
            else:
                self.rest.add_trace_step(self.trace_result, trace_type='trace',
                                         dpid=result['dpid'], port=result['port'])
                is_loop = self.check_loop()
                if is_loop:
                    self.rest.add_trace_step(self.trace_result, trace_type='last',
                                             reason='loop')
                    self.trace_ended = True
                    break
                # If we got here, that means we need to keep going.
                # Prepare next packet
                prepare = prepare_next_packet
                entries, color, switch = prepare(self.obj, entries, result, packet_in)

        # Check if the last switch has inter-domain neighbors
        # if so, infer is current flows go through the interdomain port

        if switch.is_inter_domain:
            out_port = switch.match_flow(in_port, probe_pkt)
            if out_port in switch.inter_domain_ports.keys():
                neighbor_conf = switch.inter_domain_ports[out_port]
                self.trace_interdomain(switch, neighbor_conf, entries, color, in_port)

        # Add final result to trace_results_queue
        self.obj.trace_results_queue[self.id] = {"request_id": self.id,
                                                 "result": self.trace_result,
                                                 "start_time": str(self.rest.start_time),
                                                 "total_time": self.rest.get_time()}

        if self.inter_domain:
            self.upload_trace_interdomain(self.remote_server, self.obj.trace_results_queue[self.id])

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
            if timeout_control > 3:
                return 'timeout', False

            if len(self.obj.trace_pktIn) is 0:
                print('Sending PacketOut Again')
                switch.send_packet_out(in_port, probe_pkt.data)
            else:
                # There are probes in the PacketIn queue
                for pIn in self.obj.trace_pktIn:
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
        for pIn in self.obj.trace_pktIn:
            msg = TraceMsg()
            msg.import_data(pIn[2])
            if self.id == msg.request_id:
                self.obj.trace_pktIn.remove(pIn)

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

    def trace_interdomain(self, switch, neighbor_conf, entries, color, in_port):
        # Inter-domain operations start here...
        # Rewrite trace
        print('Inter-Domain Trace Started!')
        neighbor_color = neighbor_conf['color'].split(',')[1]
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
        # How many packet outs to send?
        # just one for now

    def upload_trace_interdomain(self, remote, trace_result):
        """

        Args:
            remote:
            trace_result:

        Returns:

        """
        print('Uploading Inter-domain Trace Results')
        final_result = []
        final_result.append({"type":"intertrace", "domain": self.mydomain,
                            "request_id": self.remote_request_id})
        final_result.append(trace_result)

        # Now upload
        import urllib2, json
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(remote, data=json.dumps(final_result))
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: 'PUT'
        url = opener.open(request)
        print('Upload completed')