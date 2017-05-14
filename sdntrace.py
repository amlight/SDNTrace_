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
from ryu.topology import event

from apps.coloring.auxiliary import define_colors
from libs.core.config_reader import ConfigReader
from libs.topology.links import Links
from libs.topology.switches import Switches
from apps.tracing import tracing
from apps.tracing.trace_manager import TraceManager
from apps.tracing.trace_pkt import generate_entries_from_packet_in
from apps.topo_discovery.topo_discovery import TopologyDiscovery


class SDNTrace(app_manager.RyuApp):

    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION, ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SDNTrace, self).__init__(*args, **kwargs)

        self.colors = []        # List of current colors in use
        self.old_colors = []    # List of old colors used
        # Threads
        self.push_colors = hub.spawn(self._push_colors)
        self.flows = hub.spawn(self.get_all_flows)

        self.trace_pktIn = []  # list of received PacketIn non LLDP

        # Topology
        self.switches = Switches()  # Dict for OFSwitch1* classes
        self.links = Links()     # List of links detected

        # Topology Discovery App
        self.topo_disc = TopologyDiscovery()

        # Trace_Manager
        self.tracer = TraceManager(self)

        # Other variables
        self.config = ConfigReader()
        self.print_ready = False  # Just to print System Ready once

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
            hub.sleep(self.config.trace.push_color_interval)

    def get_all_flows(self):
        """
            Keep asking for flow entries of each switch

        """
        while True:
            if len(self.switches) > 1:
                for switch in self.switches.get_switches():
                    switch.get_flows()
            hub.sleep(self.config.stats.flowstats_interval)

    # Event Listeners
    @set_ev_cls(event.EventSwitchEnter)
    def get_topology_data(self, ev):
        """
            Get switches' IPs and ports. This method is
            detected after EventOFPSwitchFeatures, so we just
            update the switch address.
        Args:
            ev: EventSwitchEnter
        """
        self.switches.update_switch_address(ev.switch.dp)

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
        self.switches.add_switch(ev)

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status(self, ev):
        """
            Process OFP_Port_Status
            Add or Remove ports from OFSwitch.ports
            Args:
                ev: PortStatus received
        """
        # TODO: Trigger topology change
        switch = self.switches.get_switch(ev.msg.datapath)
        switch.port_status(ev)

    @set_ev_cls(ofp_event.EventOFPStateChange, DEAD_DISPATCHER)
    def remove_switch(self, ev):
        """
            If DEAD_DISPATCHER received, remove switch from self.switches
            Args:
                ev: packet captured
        """
        self.switches.del_switch(ev)

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_stats_reply_handler(self, ev):
        """
            Multipart Port Stats Description
            Only used for OF1.3
            Args:
                ev: FeatureReply received
        """
        switch = self.switches.get_switch(ev.msg.datapath)
        switch.process_port_desc_stats_reply(ev)

    @set_ev_cls(ofp_event.EventOFPDescStatsReply, MAIN_DISPATCHER)
    def description_stats_reply_handler(self, ev):
        """
            Multipart Description Stats Description
            Only used for OF1.3
            Args:
                ev: FeatureReply received
        """
        switch = self.switches.get_switch(ev.msg.datapath)
        switch.process_description_stats_reply(ev)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """
            Process PacketIn
            PacketIN messages are used for topology discovery and traces
            Args:
                ev: PacketIn message
        """
        switch = self.switches.get_switch('%016x' % ev.msg.datapath.id, by_name=True)
        if isinstance(switch, bool):
            print('PacketIn received for a switch that was not instantiated!!')
            return

        action, result, in_port = switch.process_packetIn(ev, self.links)

        if action is 1:  # LLDP
            self.topo_disc.handle_packet_in_lldp(link=result)

        elif action is 2:  # Probe packets
            trace_type, pkt = tracing.process_probe_packet(ev, result, in_port,
                                                           self.config,
                                                           switch)
            if trace_type is 'Intra' and pkt is not False:
                # This list is store all PacketIn message received
                self.trace_pktIn.append(pkt)
            elif trace_type is 'Inter':
                print('Inter-domain probe received')
                # Convert pkt.data to entries
                new_entries = generate_entries_from_packet_in(ev,
                                                              switch.datapath_id,
                                                              in_port)
                # add new_entries to the trace_request_queue
                self.tracer.new_trace(new_entries)

    @set_ev_cls(ofp_event.EventOFPErrorMsg, MAIN_DISPATCHER)
    def openflow_error(self, ev):
        """
            Print Error Received. Useful for troubleshooting
            Args:
                ev: event
        """
        print('OFPErrorMsg received: type=0x%02x code=0x%02x message=%s' %
              (ev.msg.type, ev.msg.code, utils.hex_array(ev.msg.data)))

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def handle_flow_stats(self, ev):
        """
            Process OFPFlowStatsReply saving all the flows
            associated with a switch. These flows will be used for
            the inter-domain trace
            Args:
                ev: EventOFPFlowStatsReply message
        """
        flows = ev.msg.body
        switch = self.switches.get_switch(ev.msg.datapath)
        switch.flows = sorted(flows, key=lambda f: f.priority, reverse=True)

    def install_colored_flows(self):
        """
            First define colors for each node
            Delete old flows
            Then push new flows
        """
        colors = define_colors(self.switches.get_switches())
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
                        print('SDNTrace Ready!')
                    return

        # Check all colors in use
        # For each switch:
        # 1 - Delete colored flows
        # 2 - For each switch, check colors of neighbors
        # 3 - Install all neighbors' colors
        for switch in self.switches.get_switches():
            # 1 - Delete old colored flows
            switch.delete_colored_flows()
            # 2 - Check colors of all other switches
            neighbor_colors = []
            for color in self.colors:
                # Get Dict Key. Just one Key
                for key in color:
                    if key != switch.name:
                        neighbor = self.switches.get_switch(key, by_name=True)
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
