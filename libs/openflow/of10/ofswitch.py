"""
    OpenFlow 1.0 switch class
"""
from ryu.ofproto import ether
from ryu.lib.packet import lldp
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
