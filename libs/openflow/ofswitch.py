"""
    OpenFlow generic switch class
"""


from ryu.ofproto import ether
from ryu.lib.packet import packet, lldp, ethernet, vlan
from libs.coloring.auxiliary import simplify_list_links
from libs.openflow.port_speed import get_speed_name

class OFSwitch(object):
    """
        Used to keep track of each node
        This object is used in the SDNTrace.switches
    """
    def __init__(self, ev, config_vars):
        self.obj = ev
        self.dpid = ev.msg.datapath_id
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

    def add_default_flow(self, match):
        """
            Push our default flow (MAC + LLDP + VLAN)
        """
        datapath = self.obj.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
        self.push_flow(datapath, 0, 0, ofproto.OFPFC_ADD, match, actions)

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
                speed = get_speed_name(ev.msg.version, msg.desc)
                self.ports[msg.desc.port_no] = {"port_no": msg.desc.port_no,
                                                "name": msg.desc.name,
                                                "speed": speed}

    def send_packet_out(self, port, data, lldp=False):
        """
            Sends PacketOut - Serializes Traces and LLDP packets for
            topology discovery
            Args:
                node: node to send PacketOut
                port: if LLDP: port to send PacketOut out. if
                      Trace: in_port field
                data: Ethernet frame to be send
                lldp: used in case of LLDP packets
                    (used by _topology_discovery)
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

    def push_color(self, match):
        """
            Finish preparing the colored flow after
            receiving a per-OpenFlow version OFMatch
            Args:
                match: OFMatch
        """
        datapath = self.obj.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        op = ofproto.OFPP_CONTROLLER
        actions = [datapath.ofproto_parser.OFPActionOutput(op)]

        flow_prio = self.config_vars['FLOW_PRIORITY']
        self.push_flow(datapath, self.cookie, flow_prio,
                         ofproto.OFPFC_ADD, match, actions)

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
        # TODO: Uncomment these next two lines
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
            if self.version == 1:
                return 2, pkt, ev.msg.in_port
            elif ev.msg.version == 4:
                return 2, pkt, ev.msg.match['in_port']
