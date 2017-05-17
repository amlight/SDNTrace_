"""
    OpenFlow generic switch class
"""
from ryu.lib import hub
from ryu.lib.packet import packet, lldp, ethernet, vlan
from ryu.ofproto import ether

from libs.core.config_reader import ConfigReader
from libs.openflow.port_speed import get_speed_name
from libs.topology.link import Link
# from libs.topology.switches import Switches
import libs.topology.switches
from libs.core.queues import topology_change


class OFSwitch(object):
    """
        Used to keep track of each node
        This object is used in the SDNTrace.switches
    """
    def __init__(self, ev):
        self.obj = ev
        self.switches = libs.topology.switches.Switches()
        self.dpid = self.obj.msg.datapath_id
        self.ports = dict()
        self.adjacencies_list = []  # list of OFSwitch classes
        self.color = "0"
        self.old_color = "0"
        self.name = self.datapath_id
        self.switch_name = None  # mfr_desc
        self.switch_vendor = None  # mfr_desc
        self.addr = ('0.0.0.0', 0)
        self.version = None
        # TODO: Clear colored flows when connected
        # self.delete_colored_flows()
        self.clear_start = False
        self.config = ConfigReader()
        self.cookie = None
        self.set_cookie()
        # just to print connected once
        self.just_connected = 0
        self.flows = []
        # set up inter-domain
        self.is_inter_domain = False
        self.inter_domain_ports = dict()
        self.setup_interdomain()
        # threads
        self._get_flows = hub.spawn(self._request_flows)

    @property
    def version_name(self):
        if self.version == 1:
            return '1.0'
        elif self.version == 4:
            return '1.3'

    @property
    def datapath_id(self):
        """
            Property to print datapath_id in the hex format
            Returns:
                dpid in hex
        """
        return '%016x' % self.dpid

    def update_addr(self, addr):
        """
            This method is used to get the switch IP address and port.
            It has no purpose for the SDNTrace, just for the GUI
        """
        self.addr = addr
        self.print_connected()

    def print_connected(self):
        """
            This method just prints that a switch has connected. It waits for both
            FeatureReply (+1) and EventConnnect(+1). The way used to force that both
            need to be seen is that the self.just_connect is increased by 1 per message
            received. This function is used just for information on the CLI.
        """
        self.just_connected += 1
        if self.just_connected == 2:
            print("Switch %s (%s) IP %s:%s OpenFlow version %s has just connected!" %
                  (self.switch_name, self.datapath_id, self.addr[0],
                   self.addr[1], self.version_name))

    def print_removed(self):
        """
            Just print that the switch was disconnected
        """
        print('Switch %s has just disconnected' % self.datapath_id)

    def set_cookie(self):
        """
            Cookies will be used to guarantee that any flow installed or
            removed will be traceable. The idea is to avoid removing user flows.

        """
        # TODO: It is not 100% yet.
        min_cookie_id = self.config.openflow.min_cookie
        self.cookie = min_cookie_id + 1
        self.cookie += 1

    def process_description_stats_reply(self, ev):
        """
            Process Multipart Description Stat Description
            Used to collect the switch name - for now
            Args:
                ev: Multipart Reply message
        """
        body = ev.msg.body
        self.switch_name = str(body.dp_desc)
        self.switch_vendor = body.mfr_desc
        self.print_connected()

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
        for link in links.links:
            if link[0] == self.name:
                neighbor = self.switches.get_switch(link[1], True)
                self.adjacencies_list.append(neighbor)
            elif link[1] == self.name:
                neighbor = self.switches.get_switch(link[0], True)
                self.adjacencies_list.append(neighbor)

    def add_default_flow(self, match):
        """
            Push our default flow (MAC + LLDP + VLAN)
        """
        datapath = self.obj.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
        self.push_flow(datapath, 0, 1, ofproto.OFPFC_ADD, match, actions)

    @topology_change
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

    def _request_flows(self):
        """
            Keep asking for flow entries of each switch
        """
        while True:
                self.get_flows()
                hub.sleep(self.config.stats.flowstats_interval)

    def save_flows(self, flows):
        self.flows = sorted(flows, key=lambda f: f.priority, reverse=True)

    def send_packet_out(self, port, data, lldp=False):
        """
            Sends PacketOut - Serializes Traces and LLDP packets for
            topology discovery
            Args:
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

        if self.version == 1:
            match = parser.OFPMatch(dl_src=mac_color)
        elif self.version == 4:
            match = parser.OFPMatch(eth_src=mac_color)

        flags = 0
        flow_prio = self.config.trace.flow_priority
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

        op = ofproto.OFPP_CONTROLLER
        actions = [datapath.ofproto_parser.OFPActionOutput(op)]

        flow_prio = self.config.trace.flow_priority
        self.push_flow(datapath, self.cookie, flow_prio,
                       ofproto.OFPFC_ADD, match, actions)

    @staticmethod
    def process_packetIn(ev, links):
        """
            Process PacketIn - core of the SDNTrace
            PacketIn.action will define the reason: if content is LLDP,
                it means it is a topology discovery packet
                if content is not, it COULD be a trace file
            Args:
                ev: event
                links: List Class
            Returns:
                0, 0 if table miss
                2, pkt if not LLDP
                1, list of current known links
        """
        pktIn_dpid = '%016x' % ev.msg.datapath.id
        if ev.msg.version == 1:
            pktIn_in_port = ev.msg.in_port
        elif ev.msg.version == 4:
            pktIn_in_port = ev.msg.match['in_port']

        # If it is a OFPR_NO_MATCH, it means it is not our packet
        # Return 0
        if ev.msg.reason == ev.msg.datapath.ofproto.OFPR_NO_MATCH:
            return 0, 0, 0

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

            PortId = pkt_lldp.tlvs[1]
            pktOut_port = PortId.port_id

            link = Link(pktIn_dpid, pktIn_in_port, pktOut_dpid, pktOut_port)
            return 1, link, 0

        # If not LLDP, it could be a probe Packet
        else:
            if ev.msg.version == 1:
                return 2, pkt, ev.msg.in_port
            elif ev.msg.version == 4:
                return 2, pkt, ev.msg.match['in_port']

    def setup_interdomain(self):
        """
            In this section, we will reach the configuration
            and push more specific flows per domain neighbor.
            These flows will have higher priority. All values
            will come from the [inter-domain] section
        """
        # Check if this switch has neighbors
        self.is_inter_domain = self.config.interdomain.is_interdomain(self.datapath_id)
        if self.is_inter_domain:
            my_color = self.config.interdomain.color_value
            neighbors = self.config.interdomain.neighbors
            for neighbor in neighbors:
                local_dpid = self.config.interdomain.get_local_sw(neighbor)
                local_port = self.config.interdomain.get_local_port(neighbor)
                if local_dpid == self.datapath_id:
                    neighbor_conf = self.config.interdomain.get_neighbor_conf(neighbor)
                    self.inter_domain_ports[local_port] = neighbor_conf
                    prio = self.config.interdomain.priority
                    self.install_interdomain_color(my_color, local_port, prio)
