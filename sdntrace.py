from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.ofproto.ofproto_v1_0_parser import OFPPhyPort
import prepare
from ryu.lib import hub
import topology
import trace_pkt
import brocade


class OFSwitch:
    """
        Used to keep track of the main info about each node
    """
    def __init__(self, ev):
        self.obj = ev
        self.dpid = ev.msg.datapath_id
        self.ports = self._extract_ports()
        # To be used for coloring
        self.adjenceciesList = []
        self.color = "0"
        self.old_color = "0"
        self.name = self.datapath_id

    @property
    def datapath_id(self):
        return '%016x' % self.dpid

    def _extract_ports(self):
        num_ports = len(self.obj.msg.ports)
        ofproto = self.obj.msg.datapath.ofproto
        offset = ofproto.OFP_SWITCH_FEATURES_SIZE
        port_list = []

        for _i in range(num_ports):
            if _i < ofproto.OFPP_MAX:
                port = OFPPhyPort.parser(self.obj.msg.buf, offset)
                port_list.append(port.port_no)
                offset += ofproto.OFP_PHY_PORT_SIZE

        return port_list


PACKET_OUT_INTERVAL = 5
PUSH_COLORS_INTERVAL = 10
COLLECT_INTERVAL = 30
HAS_OFPP_TABLE_SUPPORT = True


class SDNTrace(app_manager.RyuApp):

    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SDNTrace, self).__init__(*args, **kwargs)

        self.node_list = []
        self.links = []
        self.colors = []
        self.old_colors = []
        # Threads
        self.topo_disc = hub.spawn(self._topology_discovery)
        self.push_colors = hub.spawn(self._push_colors)
        # self.collect_stats = hub.spawn(self._collect_stats)
        # Trace
        self.trace_pktIn = []

    def _topology_discovery(self):
        """
            Keeps loops node_list every 5 seconds
            Send packet_out + LLDP for every port found
        """
        while True:
            for node in self.node_list:
                for port in node.ports:
                    self._send_packet_out_lldp(node, port)
            hub.sleep(PACKET_OUT_INTERVAL)

    def _push_colors(self):
        """
            This routine will run each PUSH_COLORS_INTERVAL inverval
            and process the self.links to associate colors to OFSwitches.
            Flows will be pushed to the switch with the VLAN_PCP field set
            to the defined color outputing to controller
        """
        while True:
            if len(self.node_list) > 1:
                if len(self.links) is not 0:
                    self.get_topology_data()
            hub.sleep(PUSH_COLORS_INTERVAL)

    def _collect_stats(self):
        """
            This method will send FLOW_STAT_REQ each COLLECT_INTERVAL interval

        """
        while True:
            for node in self.node_list:
                brocade.send_stat_req(self, node)
            hub.sleep(COLLECT_INTERVAL)

    def _send_packet_out_lldp(self, node, port):
        """
            PacketOut - Serializes LLDP packets for topology discovery

            node, port = node and port to send the LLDP out
        """
        pkt = topology.prepare_lldp(node, port)

        parser = node.obj.msg.datapath.ofproto_parser
        datapath = node.obj.msg.datapath
        actions = [parser.OFPActionOutput(port)]
        ofproto = datapath.ofproto
        buffer_id = ofproto.OFP_NO_BUFFER
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=buffer_id,
                                  in_port=ofproto.OFPP_NONE, actions=actions,
                                  data=pkt.data)
        datapath.send_msg(out)
        return

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """
            FeatureReply - For each new switch that connects, add to the
            node_list array. This array will be used for sending packetOut
            and generate topology and colors

            ev - packet captured
        """
        self.node_list.append(OFSwitch(ev))
        self.add_default_flow(ev)

    def add_default_flow(self, ev):
        """
            Push default flow
        """
        datapath, match, actions = topology.prepare_default_flow(self, ev)
        ofproto = datapath.ofproto
        self.add_flow(datapath, 0, 0, ofproto.OFPFC_ADD, match, actions)

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status(self, ev):
        """
            Process OFP_Port_Status
            Add or Remove ports from OFSwitch.ports
        """
        topology.process_port_status(self, ev)

    @set_ev_cls(ofp_event.EventOFPStateChange, DEAD_DISPATCHER)
    def remove_switch(self, ev):
        """
            If DEAD_DISPATCHER received, remove switch from self.node_list
        """
        topology.remove_switch(self, ev)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handle(self, ev):
        """
            Process PacketIn - create the topology
        """
        print 'packetIn'
        action, result = topology.process_packetIn(self, ev, self.links)
        if action is 1:
            self.links = result
        elif action is 2:
            pkt = trace_pkt.process_probe_packet(ev, result)
            if pkt is not False:
                self.trace_pktIn.append(pkt)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def flow_stats_reply(self, ev):
        """
            Process Flow Stats
            ev = packet received
        """
        brocade.flow_stats_reply(ev)

    def get_topology_data(self):
        """
            First define colors for each node
            Then push flows
        """
        prepare.prepare_adjencenciesList(self, self.links)
        colors = prepare.define_color(self)

        # Compare received colors with self.old_colors
        # If the same, ignore

        if colors is not None:
            self.colors = colors
            if len(self.old_colors) is 0:
                self.old_colors = self.colors
            else:
                if self.colors == self.old_colors:
                    return

        # Check all colors in use
        # For each switch:
        # 1 - Delete colored flows
        # 2 - Check colors of all other switches
        # 3 - Install all colors from other switches
        for node in self.node_list:
            self.delete_colored_flows(node)
            neighbor_colors = []
            for color in self.colors:
                # Get Dict Key. Just one Key
                for key in color:
                    if key != node.name:
                        idx = prepare.get_node_from_name(self, key)
                        if self.node_list[idx] in node.adjenceciesList:
                            neighbor_colors.append(color[key])
            for color in neighbor_colors:
                self.install_color(node, color)
            del neighbor_colors

    def delete_colored_flows(self, node):
        """
            Remove old colored flows from the node
        """
        # Test this method!!
        datapath = node.obj.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        op = ofproto.OFPP_CONTROLLER
        actions = [datapath.ofproto_parser.OFPActionOutput(op)]
        color = int(node.old_color)
        match = parser.OFPMatch(dl_type=0x8100, dl_vlan=100, dl_vlan_pcp=color)
        self.add_flow(datapath, 0, 55555, ofproto.OFPFC_DELETE_STRICT,
                      match, actions)
        return

    def install_color(self, node, color):
        """
            Prepare to send the FlowMod to install the colored flow
            node - datapath
            color - VLAN_PCP to be used
        """
        datapath = node.obj.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        op = ofproto.OFPP_CONTROLLER
        actions = [datapath.ofproto_parser.OFPActionOutput(op)]

        color = int(color)
        match = parser.OFPMatch(dl_type=0x8100, dl_vlan=100, dl_vlan_pcp=color)
        self.add_flow(datapath, 0, 55555, ofproto.OFPFC_ADD, match, actions)

    def add_flow(self, datapath, cookie, priority, command, match, actions):
        """
             Send the FlowMod to datapath
        """
        parser = datapath.ofproto_parser
        mod = parser.OFPFlowMod(datapath=datapath, match=match, cookie=cookie,
                                out_port=datapath.ofproto.OFPP_CONTROLLER,
                                flags=datapath.ofproto.OFPFF_SEND_FLOW_REM,
                                command=command, priority=priority,
                                actions=actions)
        # DEBUG:
        # print mod

        datapath.send_msg(mod)
        datapath.send_barrier()

    def process_trace_req(self, entries):
        """
            Receives the REST/PUT to generate a PacketOut
            data needs to be serialized
            template_trace.json is an example

            entries  -
        """
        dpid = entries['trace']['switch']['dpid']

        for node in self.node_list:
            if dpid == node.name:
                color = node.color
                break
        else:
            print 'Device not found %s' % dpid
            return

        in_port, pkt = trace_pkt.generate_trace_pkt(entries, color)

        parser = node.obj.msg.datapath.ofproto_parser
        datapath = node.obj.msg.datapath
        ofproto = node.obj.msg.datapath.ofproto
        buffer_id = ofproto.OFP_NO_BUFFER

        if HAS_OFPP_TABLE_SUPPORT is True:
            actions = [parser.OFPActionOutput(ofproto.OFPP_TABLE)]
            # ofproto.OFPP_NONE
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=buffer_id, in_port=ofproto.OFPP_NONE,
                                      actions=actions, data=pkt.data)
            datapath.send_msg(out)
            print out
        else:
            brocade.send_trace_probes(node, in_port, pkt)

        # Check array of packets
        # to be developed
        hub.sleep(5)
        print self.trace_pktIn
        return self.trace_pktIn[0]
