"""
    This is the core of the SDNTrace
    Here all OpenFlow events are received and handled
"""
from ryu import utils
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import DEAD_DISPATCHER
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.ofproto import ofproto_v1_0, ofproto_v1_3

from libs.openflow.of10.ofswitch import OFSwitch10
from libs.openflow.of13.ofswitch import OFSwitch13
from libs.tracing import tracing
from libs.read_config import read_config
from libs.coloring.auxiliary import prepare_lldp_packet, define_colors
from libs.tracing.tracer import TracePath


class SDNTrace(app_manager.RyuApp):

    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION, ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SDNTrace, self).__init__(*args, **kwargs)
        self.switches = dict()
        self.links = []
        self.colors = []
        self.old_colors = []
        # Threads
        self.topo_disc = hub.spawn(self._topology_discovery)
        self.push_colors = hub.spawn(self._push_colors)
        self.monitor_thread = hub.spawn(self._req_port_desc)
        self.tracing = hub.spawn(self._run_traces)
        # Traces
        self.trace_results_queue = dict()
        self.trace_request_queue = dict()

        self.config_vars = read_config()  # Read configuration file
        self.print_ready = False  # Just to print System Ready once
        self.trace_pktIn = []  # list of received PacketIn not LLDP

    # Auxiliary Threads
    def _topology_discovery(self):
        """
            Keeps looping node_list every PACKET_OUT_INTERVAL seconds
            Send a packet_out w/ LLDP to every port found
            Args:
                self
        """
        vlan = self.config_vars['VLAN_DISCOVERY']
        while True:
            # Only send PacketOut + LLDP when more than one switch exists
            if len(self.switches) > 1:
                for _, switch in self.switches.items():
                    for port in switch.ports:
                        pkt = prepare_lldp_packet(switch, port, vlan)
                        switch.send_packet_out(port, pkt.data, lldp=True)
            hub.sleep(self.config_vars['PACKET_OUT_INTERVAL'])

    def _push_colors(self):
        """
            This routine will run every PUSH_COLORS_INTERVAL interval
            and process the self.links to associate colors to OFSwitches.
            Flows will be pushed to switches with the dl_src field set
            to the defined color outputting to controller
            Args:
                self
        """
        while True:
            if len(self.switches) > 1:
                if len(self.links) is not 0:
                    self.install_colored_flows()
            hub.sleep(self.config_vars['PUSH_COLORS_INTERVAL'])

    def _req_port_desc(self):
        """
            OF1.3 only
            Because FeatureReply doesn't provide port info
            we need to use multipart request with option
            OFPPortDescStatsRequests
        """
        while True:
            if len(self.switches) > 0:
                for _, switch in self.switches.items():
                    if switch.version == ofproto_v1_3.OFP_VERSION:
                        switch.request_port_description()
            hub.sleep(self.config_vars['COLLECT_INTERVAL'])

    def _run_traces(self):
        """
            Reads the trace_request_queue queue for new request
            Once a request is found, creates a thread to process it
        """
        while True:
            if len(self.trace_request_queue) > 0:
                try:
                    r_ids = []
                    for r_id in self.trace_request_queue:
                        hub.spawn(self.spawn_trace(r_id))
                        r_ids.append(r_id)
                    for rid in r_ids:
                        del self.trace_request_queue[rid]
                except Exception as e:
                    print("Error %s" % e)
            hub.sleep(0.5)

    # Main thread
    def instantiate_switch(self, ev):
        """
            Instantiate an OpenFlow 1.0 or 1.3 switch
            Args:
                ev: FeatureReply received
            Returns:
                OFSwitch1* class
        """
        if ev.msg.version == ofproto_v1_0.OFP_VERSION:
            return OFSwitch10(ev, self.config_vars)
        elif ev.msg.version == ofproto_v1_3.OFP_VERSION:
            return OFSwitch13(ev, self.config_vars)
        return False

    @staticmethod
    def debug(msg):
        print("variable: (%s) and type: %s" % (repr(msg), type(msg)))

    def add_switch(self, ev):
        """
            Add the new switch to the self.switches dict
            Args:
                ev: FeatureReply
        """
        self.switches[ev.msg.datapath_id] = self.instantiate_switch(ev)

    def del_switch(self, ev):
        """
            In case of DEAD_DISPATCH, remove the switch from
            the self.switches dict
            Args:
                ev: DEAD_DISPATCH event
        """
        switch = self.get_switch(ev.datapath)
        if switch is not False:
            self.switches.pop(switch.dpid)

    def get_switch(self, datapath, by_name=False):
        """
            Query the self.switches
            Args:
                datapath: datapath object
                by_name: if search is by datapath id

            Returns:
                OFSwitch10 or OFSwitch13 objects
                False if not found
        """
        for _, switch in self.switches.items():
            if by_name:
                if switch.name == datapath:
                    return switch
            else:
                if switch.obj.msg.datapath == datapath:
                    return switch
        return False

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """
            FeatureReply - For each new switch that connects, add to the
            switches dictionary. This dict will be used for sending packetOut
            and generate topology and colors.
            When instantiating a switch, clears old colored flows
            and adds the default LLDP flow
            Args:
                ev: FeatureReply received
        """
        self.add_switch(ev)

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status(self, ev):
        """
            Process OFP_Port_Status
            Add or Remove ports from OFSwitch.ports
            Args:
                ev: PortStatus received
        """
        switch = self.get_switch(ev.msg.datapath)
        switch.port_status(ev)

    @set_ev_cls(ofp_event.EventOFPStateChange, DEAD_DISPATCHER)
    def remove_switch(self, ev):
        """
            If DEAD_DISPATCHER received, remove switch from self.switches
            Args:
                ev: packet captured
        """
        self.del_switch(ev)

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_stats_reply_handler(self, ev):
        """
            Multipart Port Stats Description
            Only used for OF1.3
            Args:
                ev: FeatureReply received
        """
        switch = self.get_switch(ev.msg.datapath)
        switch.process_port_desc_stats_reply(ev)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """
            Process PacketIn
            PacketIN messages are used for topology discovery and traces
            Args:
                ev: PacketIn message
        """
        switch = self.get_switch('%016x' % ev.msg.datapath.id, by_name=True)
        action, result, in_port = switch.process_packetIn(ev, self.links)
        if action is 0:  # Table Miss, ignore
            pass
        elif action is 1:  # LLDP
            self.links = result
            self.create_adjacencies(self.links)
        elif action is 2:  # Probe packets
            pkt = tracing.process_probe_packet(ev, result, in_port)
            if pkt is not False:
                # This list is store all PacketIn message received
                self.trace_pktIn.append(pkt)

    @set_ev_cls(ofp_event.EventOFPErrorMsg, MAIN_DISPATCHER)
    def openflow_error(self, ev):
        """
            Print Error Received. Useful for troubleshooting
            Args:
                ev: event
        """
        msg = ev.msg
        print ('OFPErrorMsg received: type=0x%02x code=0x%02x message=%s' %
               (msg.type, msg.code, utils.hex_array(msg.data)))

    def create_adjacencies(self, links):
        """
            Everytime self.links is updated, update all
            adjacencies between switches
            Args:
                links: self.links
        """
        for _, switch in self.switches.items():
            switch.create_adjacencies(self, links)

    def install_colored_flows(self):
        """
            First define colors for each node
            Delete old flows
            Then push new flows
        """
        colors = define_colors(self.switches)
        # Compare received colors with self.old_colors
        # If the same, ignore
        if colors is not None:
            self.colors = colors
            if len(self.old_colors) is 0:
                self.old_colors = self.colors
            else:
                if self.colors == self.old_colors:
                    if not self.print_ready:
                        self.print_ready = True
                        print 'System Ready!'
                    return

        # Check all colors in use
        # For each switch:
        # 1 - Delete colored flows
        # 2 - For each switch, check colors of neighbors
        # 3 - Install all neighbors' colors
        for _, switch in self.switches.items():
            # 1 - Delete old colored flows
            switch.delete_colored_flows()
            # 2 - Check colors of all other switches
            neighbor_colors = []
            for color in self.colors:
                # Get Dict Key. Just one Key
                for key in color:
                    if key != switch.name:
                        neighbor = self.get_switch(key, by_name=True)
                        if neighbor in switch.adjacencies_list:
                            neighbor_colors.append(color[key])
            # 3 - Install all colors from other switches
            # in some cases, if two neighbors have the same color, the same flow
            # will be installed twice. It is not an issue.
            for color in neighbor_colors:
                switch.install_color(color)
            del neighbor_colors
            switch.old_color = switch.color
        self.old_colors = self.colors

    def spawn_trace(self, rid):
        """
            Once a request is found by the _run_traces method,
            instantiate a TracePath class and runs the tracepath
            Args:
                rid: trace request id
            Returns:
                tracer.tracepath
        """
        print("Creating thread to trace request id %s..." % rid)
        tracer = TracePath(self, rid, self.trace_request_queue[rid])
        tracer.initial_validation()
        return tracer.tracepath
