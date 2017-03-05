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
from libs.coloring import topology
from libs.coloring import prepare
from libs.tracing import trace_pkt, tracing
from libs.read_config import read_config
from libs.coloring.topology import prepare_lldp_packet


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
        # Trace
        self.trace_pktIn = []  # list of received PacketIn not LLDP
        # Read configuration file
        self.config_vars = read_config()
        self.print_ready = False # Just to print System Ready once

    def _topology_discovery(self):
        """
            Keeps looping node_list every PACKET_OUT_INTERVAL seconds
            Send a packet_out w/ LLDP to every port found
            Args:
                self
        """
        vlan = self.config_vars['VLAN_DISCOVERY']
        while True:
            if len(self.switches) > 1:
                for _, switch in self.switches.items():
                    for port in switch.ports:
                        pkt = prepare_lldp_packet(switch, port, vlan)
                        switch.send_packet_out(switch, port, pkt.data, True)
            hub.sleep(self.config_vars['PACKET_OUT_INTERVAL'])

    def _push_colors(self):
        """
            This routine will run each PUSH_COLORS_INTERVAL interval
            and process the self.links to associate colors to OFSwitches.
            Flows will be pushed to the switch with the dl_src field set
            to the defined color outputing to controller
            Args:
                self
        """
        while True:
            if len(self.switches) > 1:
                if len(self.links) is not 0:
                    self.get_topology_data()
            hub.sleep(self.config_vars['PUSH_COLORS_INTERVAL'])

    def instantiate_switch(self, ev):
        if ev.msg.version == 1:
            return OFSwitch10(ev, self.config_vars)
        elif ev.msg.version == 4:
            return OFSwitch13(ev, self.config_vars)
        return False

    def debug(self, msg):
        print("variable: (%s) and type: %s" % (repr(msg), type(msg)))

    def add_switch(self, ev):
        self.switches[ev.msg.datapath_id] = self.instantiate_switch(ev)

    def del_switch(self, ev):
        switch = self.get_switch(ev.datapath)
        if switch is not False:
            self.switches.pop(switch.dpid)

    def get_switch(self, datapath, by_name=False):
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
            node_list array. This array will be used for sending packetOut
            and generate topology and colors.
            When instantiating a switch, clears old colored flows
            and adds the default LLDP flow
            Args:
                ev: event triggered
        """
        self.add_switch(ev)

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status(self, ev):
        """
            Process OFP_Port_Status
            Add or Remove ports from OFSwitch.ports
            Args:
                ev: packet captured
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
            # Table Miss, ignore
            pass
        elif action is 1:
            self.links = result
            self.create_adjacencies(self.links)
        elif action is 2:
            pkt = tracing.process_probe_packet(ev, result)
            if pkt is not False:
                self.trace_pktIn.append(pkt)

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

    def create_adjacencies(self, links):
        """
            Everytime self.links is updated, update all
            adjacencies between switches
            Args:
                links: self.links
        """
        for _, switch in self.switches.items():
            switch.create_adjacencies(self, links)

    def get_topology_data(self):
        """
            First define colors for each node
            Then push flows
            Args:
                self
        """
        print(self.links)
        colors = prepare.define_color(self.switches)
        print(colors)
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
        for _, switch in self.switches.items():
            # 1 - Delete colored flows
            self.delete_colored_flows(switch)
            # 2 - Check colors of all other switches
            neighbor_colors = []
            for color in self.colors:
                # Get Dict Key. Just one Key
                for key in color:
                    if key != switch.name:
                        neighbor = self.get_switch(key, True)
                        if neighbor in switch.adjacencies_list:
                            neighbor_colors.append(color[key])
            # 3 - Install all colors from other switches
            # in some cases, if two neighbors have the same color, the same flow
            # will be installed twice. It is not an issue.
            print(neighbor_colors)
            for color in neighbor_colors:
                self.install_color(switch, color)
            del neighbor_colors
            switch.old_color = switch.color

        self.old_colors = self.colors

    def delete_colored_flows(self, switch):
        """
            Remove old colored flows from the node
            Args:
                switch: node to be removed
        """
        # TODO: add cookies to the filter
        # TODO: Test again
        datapath = switch.obj.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        op = ofproto.OFPP_CONTROLLER
        actions = [datapath.ofproto_parser.OFPActionOutput(op)]
        color = int(switch.old_color)
        if color is 0:
            # It means no color was previously associated to this node
            return
        mac_color = "ee:ee:ee:ee:ee:%s" % int(color, 2)
        match = parser.OFPMatch(dl_src=mac_color)
        cookie = switch.cookie
        flags = 0
        flow_prio = self.config_vars['FLOW_PRIORITY']
        switch.push_flow(datapath, cookie, flow_prio,
                         ofproto.OFPFC_DELETE_STRICT,
                         match, actions, flags)

    def install_color(self, switch, color):
        """
            Prepare to send the FlowMod to install the colored flow
            Args:
                switch: datapath
                color: dl_src to be used
        """
        datapath = switch.obj.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        op = ofproto.OFPP_CONTROLLER
        actions = [datapath.ofproto_parser.OFPActionOutput(op)]

        mac_color = "ee:ee:ee:ee:ee:%s" % int(color,2)
        match = parser.OFPMatch(dl_src=mac_color)
        cookie = switch.cookie
        flow_prio = self.config_vars['FLOW_PRIORITY']
        switch.push_flow(datapath, cookie, flow_prio, ofproto.OFPFC_ADD,
                         match, actions)


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

        switch, color = trace_pkt.get_node_from_dpid(self.switches, dpid)
        if not switch or not color:
            print 'WARN: System Not Ready Yet'
            return 0

        return tracing.handle_trace(self, entries, switch, color, r_id)
