"""
    OpenFlow 1.3 switch class
"""
from ryu.ofproto import ether
from ryu.lib.packet import lldp
from ryu.lib import ip, mac
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto.ofproto_v1_3_parser import OFPMatch

from libs.openflow.ofswitch import OFSwitch
from libs.openflow.of13.port_helper import get_port_speed


class OFSwitch13(OFSwitch):
    """
        Used to keep track of each node
        This object is used in the SDNTrace.switches
    """
    def __init__(self, ev):
        OFSwitch.__init__(self, ev)
        self.version = ofproto_v1_3.OFP_VERSION
        self.prepare_default_flow()
        self.request_initial_description()

    def request_initial_description(self):
        """
            Sends Multipart Port Description to get
            list of ports and configurations
        """
        datapath = self.obj.msg.datapath
        parser = datapath.ofproto_parser
        # Port Request
        req = parser.OFPPortDescStatsRequest(datapath, 0)
        datapath.send_msg(req)
        # Description Request
        req = parser.OFPDescStatsRequest(datapath, 0)
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
                status = 'up' if port.config == 0 and port.state == 0 else 'down'
                ports[port.port_no] = {"port_no": port.port_no,
                                       "name": port.name,
                                       "speed": speed,
                                       'status': status}
        self.ports = ports

    def prepare_default_flow(self):
        """
            Push our default flow (MAC + LLDP + VLAN)
        """
        # TODO: Commented the ethertype for tests
        # TODO: with Corsa
        match = OFPMatch(eth_dst=lldp.LLDP_MAC_NEAREST_BRIDGE,
                        # eth_type=ether.ETH_TYPE_LLDP,
                         vlan_vid=self.config.topo.vlan_discovery |
                         ofproto_v1_3.OFPVID_PRESENT)
        self.add_default_flow(match)

    def install_color(self, color):
        """
            Prepare to send the FlowMod to install colored flows
            Args:
                color: eth_src to be used
        """
        mac_color = "ee:ee:ee:ee:ee:%s" % int(color, 2)
        self.push_color(OFPMatch(eth_src=mac_color))

    def install_interdomain_color(self, color, in_port, priority):
        """
            Prepare to send the FlowMod to install interdomain
            colored flows
            Args:
                color: dl_src to be used
                in_port: incoming port
                priority: flow priority
        """
        if not isinstance(priority, int):
            priority = int(priority)
        if not isinstance(in_port, int):
            in_port = int(in_port)

        datapath = self.obj.msg.datapath
        ofproto = datapath.ofproto
        match = OFPMatch(in_port=in_port, eth_src=color)

        op = ofproto.OFPP_CONTROLLER
        actions = [datapath.ofproto_parser.OFPActionOutput(op)]

        self.push_flow(datapath, self.cookie, priority,
                       ofproto.OFPFC_ADD, match, actions)

    @staticmethod
    def push_flow(datapath, cookie, priority, command, match, actions,
                  flags=1):
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
        mod = parser.OFPFlowMod(datapath=datapath, match=match,
                                out_port=ofproto.OFPP_CONTROLLER,
                                cookie=cookie, flags=flags,
                                command=command, priority=priority,
                                instructions=inst)
        datapath.send_msg(mod)
        datapath.send_barrier()

    def get_flows(self):
        """
        
                Returns:

        """
        dp = self.obj.msg.datapath
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        match = ofp_parser.OFPMatch()
        req = ofp_parser.OFPFlowStatsRequest(
            dp, 0, ofp.OFPTT_ALL, ofp.OFPP_ANY, ofp.OFPG_ANY,
            0, 0, match
        )
        dp.send_msg(req)

    def match_flow(self, in_port, pkt):
        """
            
            Args:
                in_port: 
                pkt: 
    
            Returns:

        """
        for flow in self.flows:
            if self.match(flow.match, pkt, in_port, self.obj.msg.datapath.ofproto):
                for instruction in flow.instructions:
                    # TODO: test if it is an acton output
                    return instruction.actions[0].port
        return 0

    @staticmethod
    def match(flow, pkt, in_port, ofp, in_phy_port=None):
        """
        
            Args:
                flow: 
                pkt: 
                in_port: 
                ofp: 
                in_phy_port: 
    
            Returns:

        """
        eth = pkt[0]
        vlan = pkt[1]

        print flow
        if 'in_port' in flow:
            if flow['in_port'] != in_port:
                return False

        if 'in_phy_port' in flow:
            if flow['in_phy_port'] != in_phy_port:
                return False

        if 'eth_dst' in flow:
            eth_dst = flow['eth_dst']
            if isinstance(eth_dst, tuple):
                edst, mask = map(mac.haddr_to_int, eth_dst)
                if edst & mask != mac.haddr_to_int(eth.dst) & mask:
                    return False
            else:
                if eth_dst != eth.dst:
                    return False

        if 'eth_src' in flow:
            eth_src = flow['eth_src']
            if isinstance(eth_src, tuple):
                esrc, mask = map(mac.haddr_to_int, eth_src)
                if esrc & mask != mac.haddr_to_int(eth.src) & mask:
                    return False
            else:
                if eth_src != eth.src:
                    return False

        if 'eth_type' in flow:
            if flow['eth_type'] != vlan.ethertype:
                return False

        def test_vid(vid):
            if vid == ofp.OFPVID_NONE and vlan.vid:
                return False
            if vid != vlan.vid | ofp.OFPVID_PRESENT:
                return False
            return True

        if 'vlan_vid' in flow:
            vlan_vid = flow['vlan_vid']
            if isinstance(vlan_vid, tuple):
                vid, mask = vlan_vid
                if vid == mask == ofp.OFPVID_PRESENT and not vlan.vid:
                    return False
                else:
                    test_vid(vid)
            else:
                vid = vlan_vid
                if not test_vid(vid):
                    return False

        if 'vlan_pcp' in flow:
            if flow['vlan_pcp'] != vlan.vid:
                return False

        ip_dscp = None
        ip_ecn = None
        ip_proto = None

        if vlan.ethertype == 0x0800:
            ip4 = pkt[2]
            tp = pkt[3]

            ip_dscp = ip4.tos >> 2
            ip_ecn = ip4.tos & 0x03
            ip_proto = ip4.proto

            if 'ipv4_src' in flow:
                ipv4_src = flow['ipv4_src']
                if isinstance(ipv4_src, tuple):
                    ipsrc, mask = map(ip.ipv4_to_int, ipv4_src)
                    if ipsrc & mask != ip.ipv4_to_int(ip4.src) & mask:
                        return False
                else:
                    if ipv4_src != ip4.src:
                        return False

            if 'ipv4_dst' in flow:
                ipv4_dst = flow['ipv4_dst']
                if isinstance(ipv4_dst, tuple):
                    ipsrc, mask = map(ip.ipv4_to_int, ipv4_dst)
                    if ipsrc & mask != ip.ipv4_to_int(ip4.dst) & mask:
                        return False
                else:
                    if ipv4_dst != ip4.dst:
                        return False

        if vlan.ethertype == 0x86dd:
            ip6 = pkt[2]
            tp = pkt[3]

            ip_dscp = ip6.traffic_class >> 2
            ip_ecn = ip6.traffic_class & 0x03
            ip_proto = ip6.nxt

            if 'ipv6_src' in flow:
                ipv6_src = flow['ipv6_src']
                if isinstance(ipv6_src, tuple):
                    ipsrc, mask = map(ip.ipv6_to_int, ipv6_src)
                    if ipsrc & mask != ip.ipv6_to_int(ip6.src) & mask:
                        return False
                else:
                    if ipv6_src != ip6.src:
                        return False

            if 'ipv6_dst' in flow:
                ipv6_dst = flow['ipv64_dst']
                if isinstance(ipv6_dst, tuple):
                    ipsrc, mask = map(ip.ipv6_to_int, ipv6_dst)
                    if ipsrc & mask != ip.ipv6_to_int(ip6.dst) & mask:
                        return False
                else:
                    if ipv6_dst != ip6.dst:
                        return False

        if 'ip_dscp' in flow and ip_dscp is not None:
            if flow['ip_dscp'] != ip_dscp:
                return False

        if 'ip_ecn' in flow and ip_ecn is not None:
            if flow['ip_ecn'] != ip_ecn:
                return False

        if 'ip_proto' in flow and ip_proto is not None:
            if flow['ip_proto'] != ip_proto:
                return False

        if ip_proto == 6:  # TCP
            if 'tcp_src' in flow:
                if flow['tcp_src'] != tp.src_port:
                    return False

            if 'tcp_dst' in flow:
                if flow['tcp_dst'] != tp.dst_port:
                    return False

        if ip_proto == 17:  # UDP
            if 'udp_src' in flow:
                if flow['udp_src'] != tp.src_port:
                    return False

            if 'udp_dst' in flow:
                if flow['udp_dst'] != tp.dst_port:
                    return False

        if ip_proto == 132:  # SCTP
            if 'sctp_src' in flow:
                if flow['sctp_src'] != tp.src_port:
                    return False

            if 'sctp_dst' in flow:
                if flow['sctp_dst'] != tp.dst_port:
                    return False

        return True
