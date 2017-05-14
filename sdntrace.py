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
from ryu.ofproto import ofproto_v1_0, ofproto_v1_3
from ryu.topology import event

from libs.core.config_reader import ConfigReader
from libs.topology.links import Links
from libs.topology.switches import Switches
from apps.tracing.trace_manager import TraceManager
from apps.topo_discovery.topo_discovery import TopologyDiscovery
from apps.graph_coloring.graph_coloring import GraphColoring


class SDNTrace(app_manager.RyuApp):

    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION, ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SDNTrace, self).__init__(*args, **kwargs)

        self.config = ConfigReader()
        # List of received PacketIn non-LLDP
        # self.trace_pktIn = []
        # Topology
        self.switches = Switches()
        self.links = Links()
        # Topology Discovery App
        self.topo_disc = TopologyDiscovery()
        # Graph Coloring App
        self.graph_coloring = GraphColoring()
        # Trace_Manager App
        self.tracer = TraceManager()
        print('SDNTrace Ready!')

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

        elif action is 2:  # Trace packets
            self.tracer.process_probe_packet(ev, result, in_port, switch)

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
        switch = self.switches.get_switch(ev.msg.datapath)
        switch.save_flows(flows=ev.msg.body)

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
