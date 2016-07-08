from ryu import utils
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import DEAD_DISPATCHER
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.ofproto import ofproto_v1_0
from ryu.ofproto.ofproto_v1_0_parser import OFPPhyPort

from libs.Coloring import topology
from libs.Coloring import prepare
from libs.Exceptions import brocade
from libs.Statistics import stats
from libs.Tracing import trace_pkt, tracing


class OFSwitch:
    """
        Used to keep track of each node
        This object is used in the SDNTrace.node_list
    """
    def __init__(self, ev):
        self.obj = ev
        self.dpid = ev.msg.datapath_id
        self.ports, self.ports_dict = self._extract_ports()
        # To be used for Coloring
        self.adjacencies_list = []
        self.color = "0"
        self.old_color = "0"
        self.name = self.datapath_id
        # Clear colored flows when connected
        self.clear_start = False
        # Statistics
        self.flows = []
        # To avoid issues when deleting flows
        global MINIMUM_COOKIE_ID
        self.cookie = MINIMUM_COOKIE_ID + 1
        MINIMUM_COOKIE_ID += 1

    @property
    def datapath_id(self):
        """
            Property to print datapath_id in the hex format
            Returns:
                dpid in hex
        """
        return '%016x' % self.dpid

    def _extract_ports(self):
        """
            Extract ports from FeatureReply message
            Ports are added to the self.ports
            Returns:
                list of ports found for a specific node
        """
        num_ports = len(self.obj.msg.ports)
        ofproto = self.obj.msg.datapath.ofproto
        offset = ofproto.OFP_SWITCH_FEATURES_SIZE
        port_list = []
        ports_dict = {}

        for _i in range(num_ports):
            if _i < ofproto.OFPP_MAX:
                port = OFPPhyPort.parser(self.obj.msg.buf, offset)
                if port.port_no < 65280:  # Special ports are 65280+
                    port_list.append(port.port_no)
                    port_list.sort()
                    ports_dict[port.port_no] = port.name
                offset += ofproto.OFP_PHY_PORT_SIZE
 
        return port_list, ports_dict


# These are configurable on the sdntrace.conf file
MINIMUM_COOKIE_ID = 2000000
PACKET_OUT_INTERVAL = 5
PUSH_COLORS_INTERVAL = 10
COLLECT_INTERVAL = 30
HAS_OFPP_TABLE_SUPPORT = True
VLAN_DISCOVERY = 100
FLOW_PRIORITY = 50000


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
        self.query_flows = hub.spawn(self._query_flows)
        # self.collect_stats = hub.spawn(self._collect_stats)
        # Trace
        self.trace_pktIn = []  # list of received PacketIn not LLDP
        # Read configuration file
        self.read_config()

        self.print_ready = False # Just to print System Ready once

    def read_config(self):
        """
            Read the configuration file (sdntrace.conf) to import
            global variables. If file does not exist, ignore.
        """
        config_file = "conf/sdntrace.conf"
        try:
            f = open(config_file, 'ro')
        except:
            return
        for line in f:
            if line[0].isalpha():
                variable, param = line.split('=')
                variable = variable.strip(' ')
                param = param.strip('\n').strip(' ')
                if variable == 'MINIMUM_COOKIE_ID':
                    global MINIMUM_COOKIE_ID
                    MINIMUM_COOKIE_ID = int(param)
                elif variable == 'PACKET_OUT_INTERVAL':
                    global PACKET_OUT_INTERVAL
                    PACKET_OUT_INTERVAL = int(param)
                elif variable == 'PUSH_COLORS_INTERVAL':
                    global PUSH_COLORS_INTERVAL
                    PUSH_COLORS_INTERVAL = int(param)
                elif variable == 'COLLECT_INTERVAL':
                    global COLLECT_INTERVAL
                    COLLECT_INTERVAL = int(param)
                elif variable == 'HAS_OFPP_TABLE_SUPPORT':
                    global HAS_OFPP_TABLE_SUPPORT
                    HAS_OFPP_TABLE_SUPPORT = param
                elif variable == 'VLAN_DISCOVERY':
                    global VLAN_DISCOVERY
                    VLAN_DISCOVERY = int(param)
                elif variable == 'FLOW_PRIORITY':
                    global FLOW_PRIORITY
                    FLOW_PRIORITY = int(param)
                else:
                    print 'Invalid Option'

    def _topology_discovery(self):
        """
            Keeps looping node_list every PACKET_OUT_INTERVAL seconds
            Send a packet_out w/ LLDP to every port found
            Args:
                self
        """
        while True:
            for node in self.node_list:
                for port in node.ports:
                    pkt = topology.prepare_lldp_packet(node, port, VLAN_DISCOVERY)
                    self.send_packet_out(node, port, pkt.data, True)
            hub.sleep(PACKET_OUT_INTERVAL)

    def _push_colors(self):
        """
            This routine will run each PUSH_COLORS_INTERVAL interval
            and process the self.links to associate colors to OFSwitches.
            Flows will be pushed to the switch with the VLAN_PCP field set
            to the defined color outputing to controller
            Args:
                self
        """
        while True:
            if len(self.node_list) > 1:
                if len(self.links) is not 0:
                    self.get_topology_data()
            hub.sleep(PUSH_COLORS_INTERVAL)

    def _query_flows(self):
        """
            Keeps querying for OFP_STAT_RES code Flow
        """
        while True:
            for node in self.node_list:
                self.send_stat_req(node)
            hub.sleep(COLLECT_INTERVAL)

    @staticmethod
    def send_packet_out(node, port, data, lldp=False):
        """
            Sends PacketOut - Serializes Traces and LLDP packets for topology discovery
            Args:
                node: node to send PacketOut
                port: if LLDP: port to send PacketOut out. if Trace: in_port field
                data: Ethernet frame to be send
                lldp: used in case of LLDP packets (used by _topology_discovery)
        """

        parser = node.obj.msg.datapath.ofproto_parser
        datapath = node.obj.msg.datapath
        ofproto = datapath.ofproto

        if lldp:
            in_port = ofproto.OFPP_NONE
            out_port = port
        else:
            in_port = port
            out_port = ofproto.OFPP_TABLE

        actions = [parser.OFPActionOutput(out_port)]
        buffer_id = ofproto.OFP_NO_BUFFER

        out = parser.OFPPacketOut(datapath=datapath, in_port=in_port,
                                  buffer_id=buffer_id, actions=actions,
                                  data=data)
        datapath.send_msg(out)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """
            FeatureReply - For each new switch that connects, add to the
            node_list array. This array will be used for sending packetOut
            and generate topology and colors
            Args:
                ev: event triggered
        """
        # Add new node to self.node_list and instantiate class OFSwitch
        self.node_list.append(OFSwitch(ev))

        # Let's remove any old colored flow
        # 1 - Get the inserted switch
        sw_added = self.node_list[len(self.node_list)-1]
        # 2 - Send a OFP_STAT_REQ code Flow
        self.send_stat_req(sw_added)
        # 3 - Once the STAT_REPLY is received, delete the flow

        # Add the topology discovery flow
        self.add_default_flow(ev)

    @staticmethod
    def send_stat_req(node):
        """
            Send  STAT_REQ for synchronization
            Args:
                ev: event
        """
        datapath = node.obj.msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        flags = 0
        match = parser.OFPMatch()
        table_id = 0
        req = parser.OFPFlowStatsRequest(datapath, flags, match, table_id,
                                         ofproto.OFPP_NONE)
        datapath.send_msg(req)

    def add_default_flow(self, ev):
        """
            Push default flow
            Args:
                ev: event triggered
        """
        vlan = VLAN_DISCOVERY
        datapath, match, actions = topology.prepare_default_flow(self, ev, vlan)
        ofproto = datapath.ofproto
        self.push_flow(datapath, 0, 0, ofproto.OFPFC_ADD, match, actions)

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status(self, ev):
        """
            Process OFP_Port_Status
            Add or Remove ports from OFSwitch.ports
            Args:
                ev: packet captured
        """
        topology.process_port_status(self, ev)

    @set_ev_cls(ofp_event.EventOFPStateChange, DEAD_DISPATCHER)
    def remove_switch(self, ev):
        """
            If DEAD_DISPATCHER received, remove switch from self.node_list
            Args:
                ev: packet captured
        """
        topology.remove_switch(self, ev)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """
            Process PacketIn
            PacketIN messages are used for topology discovery and traces
            Args:
                ev: event triggered
        """
        action, result = topology.process_packetIn(self, ev, self.links)
        if action is 0:
            # NO_MATCH, ignore
            pass
        elif action is 1:
            self.links = result
        elif action is 2:
            # To be finished.
            pkt = tracing.process_probe_packet(ev, result)
            if pkt is not False:
                self.trace_pktIn.append(pkt)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def flow_stats_reply(self, ev):
        """
             Process Flow Stats
             Args:
                 ev: packet captured
        """
        stats.flow_stats_reply(self, ev)

    @set_ev_cls(ofp_event.EventOFPErrorMsg, MAIN_DISPATCHER)
    def openflow_error(self, ev):
        """
            Print Error Received. Useful for troubleshooting, specially with Brocade
            Args:
                ev: event
        """
        msg = ev.msg
        print ('OFPErrorMsg received: type=0x%02x code=0x%02x message=%s' %
               (msg.type, msg.code, utils.hex_array(msg.data)))

    def get_topology_data(self):
        """
            First define colors for each node
            Then push flows
            Args:
                self
        """
        colors = prepare.define_color(self, self.links)

        # print 'colors'
        # print colors
        # print 'self.colors'
        # print self.colors
        # print 'self.old_colors'
        # print self.old_colors
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
                        if self.node_list[idx] in node.adjacencies_list:
                            neighbor_colors.append(color[key])
            # in some cases, if two neighbors have the same color, the same flow
            # will be installed twice. It is not an issue.
            for color in neighbor_colors:
                self.install_color(node, color)
            del neighbor_colors
            node.old_color = node.color

        self.old_colors = self.colors

    def delete_colored_flows(self, node):
        """
            Remove old colored flows from the node
            TODO: add cookies to the filter
            Args:
                node: node to be removed
        """
        # Test this method!!!!!
        datapath = node.obj.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        op = ofproto.OFPP_CONTROLLER
        actions = [datapath.ofproto_parser.OFPActionOutput(op)]
        color = int(node.old_color)
        if color is 0:
            # It means no color was previously associated to this node
            return
        match = parser.OFPMatch(dl_type=0x8100, dl_vlan_pcp=color)
        cookie = node.cookie
        flags = 0
        self.push_flow(datapath, cookie, FLOW_PRIORITY, ofproto.OFPFC_DELETE_STRICT,
                       match, actions, flags)
        return

    def install_color(self, node, color):
        """
            Prepare to send the FlowMod to install the colored flow
            Args:
                node: datapath
                color: VLAN_PCP to be used
        """
        datapath = node.obj.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        op = ofproto.OFPP_CONTROLLER
        actions = [datapath.ofproto_parser.OFPActionOutput(op)]

        color = int(color)
        # VLANS CAN NOT BE DEFINED OR IT WILL HAVE TO BE DEFINED ON DEMAND?? Brocade CES
        # match = parser.OFPMatch(dl_type=0x8100, dl_vlan=100, dl_vlan_pcp=color)
        match = parser.OFPMatch(dl_type=0x800, dl_vlan_pcp=color)
        cookie = node.cookie
        self.push_flow(datapath, cookie, FLOW_PRIORITY, ofproto.OFPFC_ADD, match, actions)

    @staticmethod
    def push_flow(datapath, cookie, priority, command, match, actions, flags=1):
        """
             Send the FlowMod to datapath. Send BarrierReq after to confirm
             Args:
                 datapath: switch class
                 cookie: cookie to be used on the flow
                 priority: flow priority
                 command: action (Add, Delete, modify)
                 match: flow match
                 actions: flow action
        """
        if flags is not 0:
            flags = datapath.ofproto.OFPFF_SEND_FLOW_REM

        parser = datapath.ofproto_parser
        mod = parser.OFPFlowMod(datapath=datapath, match=match, cookie=cookie,
                                out_port=datapath.ofproto.OFPP_CONTROLLER,
                                flags=flags,
                                command=command, priority=priority,
                                actions=actions)
        # DEBUG:
        # print mod

        datapath.send_msg(mod)
        datapath.send_barrier()

    def process_trace_req(self, entries, r_id):
        """
            Receives the REST/PUT to generate a PacketOut
            template_trace.json is an example
            Args:
                entries: entries provided by user received from REST interface
                r_id: request ID created by sdntraceRest and sent back to user
        """
        # print 'process_trace_req'
        dpid = entries['trace']['switch']['dpid']

        node, color = trace_pkt.get_node_from_dpid(self.node_list, dpid)
        if not node or not color:
            print 'WARN: System Not Ready Yet'
            return 0

        print repr(HAS_OFPP_TABLE_SUPPORT)
        if HAS_OFPP_TABLE_SUPPORT:
            # create a thread to handle this request
            return tracing.handle_trace(self, entries, node, color, r_id)
        else:
            # Find a solution for Brocade
            return brocade.send_trace_probes(self, entries, node, color, r_id)
