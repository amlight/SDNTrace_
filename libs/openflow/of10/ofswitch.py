"""
    OpenFlow 1.0 switch class
"""
from ryu.ofproto import ether
from ryu.lib.packet import lldp
from ryu.lib import ip, addrconv
from ryu.ofproto import ofproto_v1_0
from ryu.ofproto.ofproto_v1_0_parser import OFPPhyPort
from ryu.ofproto.ofproto_v1_0_parser import OFPMatch

from libs.openflow.ofswitch import OFSwitch
from libs.openflow.of10.port_helper import get_port_speed


class OFSwitch10(OFSwitch):
    """
        Used to keep track of each node
        This object is used in the SDNTrace.switches
    """
    def __init__(self, ev, config_vars):
        OFSwitch.__init__(self, ev, config_vars)
        self.version = ofproto_v1_0.OFP_VERSION
        self.ports = self._extract_ports()
        self.prepare_default_flow()
        self.request_initial_description()

    def request_initial_description(self):
        """
            Sends Multipart Port Description to get
            list of ports and configurations
        """
        datapath = self.obj.msg.datapath
        parser = datapath.ofproto_parser
        # Description Request
        req = parser.OFPDescStatsRequest(datapath, 0)
        datapath.send_msg(req)

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
        ports = dict()

        for _i in range(num_ports):
            if _i < ofproto.OFPP_MAX:
                # TODO: investigate possible bug on Ryu
                # if len(self.obj.msg.buf) == offset, or offset < 48 Ryu crashes
                # To try, just start and kill mininet a few times
                if len(self.obj.msg.buf) != offset:
                    port = OFPPhyPort.parser(self.obj.msg.buf, offset)
                    if port.port_no < ofproto.OFPP_MAX:
                        curr = get_port_speed(port.curr)
                        ports[port.port_no] = {"port_no": port.port_no,
                                               "name": port.name,
                                               "speed": curr}
                offset += ofproto.OFP_PHY_PORT_SIZE
        return ports

    def prepare_default_flow(self):
        """
            Push our default flow (MAC + LLDP + VLAN)
        """
        match = OFPMatch(dl_dst=lldp.LLDP_MAC_NEAREST_BRIDGE,
                         dl_type=ether.ETH_TYPE_LLDP,
                         dl_vlan=self.config_vars['topo_discovery']['vlan_discovery'])
        self.add_default_flow(match)

    def install_color(self, color):
        """
            Prepare to send the FlowMod to install colored flows
            Args:
                color: dl_src to be used
        """
        mac_color = "ee:ee:ee:ee:ee:%s" % int(color, 2)
        self.push_color(OFPMatch(dl_src=mac_color))

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
            flags = datapath.ofproto.OFPFF_SEND_FLOW_REM

        mod = parser.OFPFlowMod(datapath=datapath, match=match,
                                out_port=ofproto.OFPP_CONTROLLER,
                                cookie=cookie, flags=flags,
                                command=command, priority=priority,
                                actions=actions)

        datapath.send_msg(mod)
        datapath.send_barrier()

    def match_flow(self, in_port, pkt):

        for flow in self.flows:
            if self.match(flow.match, pkt, in_port, self.obj.msg.datapath.ofproto):
                for action in flow.actions:
                    # TODO: test if it is an action output
                    return action.port
        return 0

    @staticmethod
    def match(flow, pkt, in_port, ofp):
        eth = pkt[0]
        vlan = pkt[1]

        if not flow.wildcards & ofp.OFPFW_IN_PORT:
            if flow.in_port != in_port:
                return False

        if not flow.wildcards & ofp.OFPFW_DL_VLAN_PCP:
            if flow.dl_vlan_pcp != vlan.pcp:
                return False

        if not flow.wildcards & ofp.OFPFW_DL_VLAN:
            if flow.dl_vlan != vlan.vid:
                return False

        if not flow.wildcards & ofp.OFPFW_DL_SRC:
            print('Flow %s, pkt %s' % (flow.dl_src, eth.src))
            if flow.dl_src != addrconv.mac.text_to_bin(eth.src):
                return False

        if not flow.wildcards & ofp.OFPFW_DL_DST:
            if flow.dl_dst != addrconv.mac.text_to_bin(eth.dst):
                return False

        if not flow.wildcards & ofp.OFPFW_DL_TYPE:
            if flow.dl_type != vlan.ethertype:
                return False

        if vlan.ethertype == 0x0800:
            ipp = pkt[2]
            tp = pkt[3]

            ip_src = ip.ipv4_to_int(ipp.src)
            if ip_src != 0:
                mask = (flow.wildcards & ofp.OFPFW_NW_SRC_MASK) >> ofp.OFPFW_NW_SRC_SHIFT
                if mask > 32:
                    mask = 32
                mask = (0xffffffff << mask) & 0xffffffff
                if ip_src & mask != flow.nw_src & mask:
                    return False

            ip_dst = ip.ipv4_to_int(ipp.dst)
            if ip_dst != 0:
                mask = (flow.wildcards & ofp.OFPFW_NW_DST_MASK) >> ofp.OFPFW_NW_DST_SHIFT
                if mask > 32:
                    mask = 32
                mask = (0xffffffff << mask) & 0xffffffff
                if ip_dst & mask != flow.nw_dst & mask:
                    return False

            if not flow.wildcards & ofp.OFPFW_NW_TOS:
                if flow.nw_tos != ipp.tos:
                    return False

            if not flow.wildcards & ofp.OFPFW_NW_PROTO:
                if flow.nw_proto != ipp.proto:
                    return False

            if not flow.wildcards & ofp.OFPFW_TP_SRC:
                if flow.tp_src != tp.src:
                    return False

            if not flow.wildcards & ofp.OFPFW_TP_DST:
                if flow.tp_dst != tp.dst:
                    return False

        return True
