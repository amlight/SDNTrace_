"""
    OpenFlow 1.3 switch class
"""


from ryu.ofproto import ether
from ryu.lib.packet import packet, lldp, ethernet, vlan
from ryu.ofproto import ofproto_v1_3
from libs.coloring.auxiliary import simplify_list_links
from libs.openflow.of13.port_helper import get_port_speed



class OFSwitch13(object):
    """
        Used to keep track of each node
        This object is used in the SDNTrace.switches
    """
    def __init__(self, ev, config_vars):
        self.obj = ev
        self.dpid = ev.msg.datapath_id
        self.version = ofproto_v1_3.OFP_VERSION
        self.ports = dict()
        self.adjacencies_list = []  # list of DPIDs or OFSwitch10?
        self.color = "0"
        self.old_color = "0"
        self.name = self.datapath_id
        # TODO: Clear colored flows when connected
        # self.delete_colored_flows()
        self.clear_start = False
        # To avoid issues when deleting flows
        self.config_vars = config_vars
        # set cookie
        self.set_cookie()
        self.add_default_flow()

    @property
    def datapath_id(self):
        """
            Property to print datapath_id in the hex format
            Returns:
                dpid in hex
        """
        return '%016x' % self.dpid

    def set_cookie(self):
        self.min_cookie_id = self.config_vars['MINIMUM_COOKIE_ID']
        self.cookie = self.min_cookie_id + 1
        self.min_cookie_id += 1

    def port_status(self, ev):
        """
            Process OFP_Port_Status
            Add or Remove ports from OFSwitch.ports
            Args:
                ev: port status message
        """
        msg = ev.msg
        port_no = msg.desc.port_no
        ofproto = msg.datapath.ofproto
        if msg.desc.port_no > 65530:
            return

        if msg.reason == ofproto.OFPPR_DELETE:
            if port_no in self.ports:
                del self.ports[msg.desc.port_no]
        else:
            if msg.desc.port_no not in self.ports:
                speed = get_port_speed(msg.desc.curr_speed)
                self.ports[msg.desc.port_no] = {"port_no": msg.desc.port_no,
                                                "name": msg.desc.name,
                                                "speed": speed}

    @staticmethod
    def push_flow(datapath, cookie, priority, command, match, actions,
                  flags=1, buffer_id=None):
        """
             Send the FlowMod to datapath. Send BarrierReq after to confirm
             Args:
                 datapath: switch class
                 cookie: cookie to be used on the flow
                 priority: flow priority
                 command: action (Add, Delete, modify)
                 match: flow match
                 actions: flow action
                 flags: flow mod flags
        """
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        if flags is not 0:
            flags = ofproto.OFPFF_SEND_FLOW_REM

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, match=match,
                                    out_port=datapath.ofproto.OFPP_CONTROLLER,
                                    cookie=cookie, flags=flags,
                                    command=command, priority=priority,
                                    instructions=inst, buffer_id=buffer_id)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, match=match,
                                    out_port=datapath.ofproto.OFPP_CONTROLLER,
                                    cookie=cookie, flags=flags,
                                    command=command, priority=priority,
                                    instructions=inst)
        # DEBUG:
        # print mod
        datapath.send_msg(mod)
        datapath.send_barrier()

    def request_port_description(self):
        """
            Sends Multipart Port Description to get
            list of ports and configurations
        """
        datapath = self.obj.msg.datapath
        parser = datapath.ofproto_parser
        req = parser.OFPPortDescStatsRequest(datapath, 0)
        datapath.send_msg(req)

    def process_port_desc_stats_reply(self, ev):
        """
            Process Multipart Port Stat Description
            Works just like _extract_ports from OpenFlow 1.0
            Args:
                ev: Multipart Reply message
        """
        ofproto = self.obj.msg.datapath.ofproto
        ports = dict()
        for port in ev.msg.body:
            if port.port_no < ofproto.OFPP_MAX:
                speed = get_port_speed(port.curr_speed)
                ports[port.port_no] = {"port_no": port.port_no,
                                       "name": port.name,
                                       "speed": speed}
        self.ports = ports

    def add_default_flow(self):
        """
            Push our default flow (MAC + LLDP + VLAN)
        """
        vlan = self.config_vars['VLAN_DISCOVERY']
        datapath = self.obj.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(eth_dst=lldp.LLDP_MAC_NEAREST_BRIDGE,
                                eth_type=ether.ETH_TYPE_LLDP,
                                vlan_vid=vlan)
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
        self.push_flow(datapath, 0, 0, ofproto.OFPFC_ADD, match, actions)

    def send_packet_out(self, port, data, lldp=False):
        """
            Sends PacketOut - Serializes Traces and LLDP packets for topology discovery
            Args:
                node: node to send PacketOut
                port: if LLDP: port to send PacketOut out. if Trace: in_port field
                data: Ethernet frame to be send
                lldp: used in case of LLDP packets (used by _topology_discovery)
        """
        parser = self.obj.msg.datapath.ofproto_parser
        datapath = self.obj.msg.datapath
        ofproto = datapath.ofproto

        if lldp:
            in_port = ofproto.OFPP_CONTROLLER
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

    def process_packetIn(self, ev, links):
        """
            Process PacketIn - core of the SDNTrace
            PacketIn.action will define the reason: if content is LLDP,
                it means it is a topology discovery packet
                if content is not, it COULD be a trace file
            Args:
                obj: SDNTrace object
                ev: event
                links: list of links known so far
            Returns:
                0, 0 if table miss
                2, pkt if not LLDP
                1, list of current known links
        """
        pktIn_dpid = '%016x' % ev.msg.datapath.id

        # If it is a OFPR_NO_MATCH, it means it is not our packet
        # Return 0
        # Ignored for now:
        #if ev.msg.reason == ev.msg.datapath.ofproto.OFPR_NO_MATCH:
        #    return 0, 0, 0

        pkt = packet.Packet(ev.msg.data)
        pkt_eth = pkt.get_protocols(ethernet.ethernet)[0]
        next_header = pkt_eth.ethertype

        if pkt_eth.ethertype == ether.ETH_TYPE_8021Q:
            pkt_vlan = pkt.get_protocols(vlan.vlan)[0]
            next_header = pkt_vlan.ethertype

        if next_header == ether.ETH_TYPE_LLDP:

            # Extract LLDP from PacketIn.data
            pkt_lldp = pkt.get_protocols(lldp.lldp)[0]

            ChassisID = pkt_lldp.tlvs[0]
            pktOut_dpid = ChassisID.chassis_id
            link = pktIn_dpid, pktOut_dpid

            # Keep a single record between switches
            # It doesn't matter how many connections between them
            links.append(link)
            return 1, simplify_list_links(links), 0

        # If not LLDP, it could be a probe Packet
        else:
            return 2, pkt, ev.msg.match['in_port']

    def delete_colored_flows(self):
        """
            Remove old colored flows from the switch
        """
        # TODO: add cookies to the filter
        # TODO: Test again
        datapath = self.obj.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        op = ofproto.OFPP_CONTROLLER
        actions = [datapath.ofproto_parser.OFPActionOutput(op)]
        color = self.old_color
        if color is "0":
            # It means no color was previously associated to this node
            return
        mac_color = "ee:ee:ee:ee:ee:%s" % int(color, 2)
        match = parser.OFPMatch(eth_src=mac_color)
        flags = 0
        flow_prio = self.config_vars['FLOW_PRIORITY']
        self.push_flow(datapath, self.cookie, flow_prio,
                         ofproto.OFPFC_DELETE_STRICT,
                         match, actions, flags)

    def install_color(self, color):
        """
            Prepare to send the FlowMod to install colored flows
            Args:
                color: eth_src to be used
        """
        datapath = self.obj.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        op = ofproto.OFPP_CONTROLLER
        actions = [datapath.ofproto_parser.OFPActionOutput(op)]

        mac_color = "ee:ee:ee:ee:ee:%s" % int(color,2)
        match = parser.OFPMatch(eth_src=mac_color)
        flow_prio = self.config_vars['FLOW_PRIORITY']
        self.push_flow(datapath, self.cookie, flow_prio,
                         ofproto.OFPFC_ADD, match, actions)

    def create_adjacencies(self, obj, links):
        """
            Once self.links is populated with links obtained from
            PacketOut/PacketIn, populate per switch adjacencies.
            Adjacencies are used by the Coloring class to Color the
            topology
            Args:
                obj: SDNTrace class
                links: SDNTrace.links
        """
        self.adjacencies_list[:] = []
        for link in links:
            if link[0] == self.name:
                neighbor = obj.get_switch(link[1], True)
                self.adjacencies_list.append(neighbor)
            elif link[1] == self.name:
                neighbor = obj.get_switch(link[0], True)
                self.adjacencies_list.append(neighbor)
