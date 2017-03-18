"""
    OpenFlow 1.3 switch class
"""
from ryu.ofproto import ether
from ryu.lib.packet import lldp
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto.ofproto_v1_3_parser import OFPMatch

from libs.openflow.ofswitch import OFSwitch
from libs.openflow.of13.port_helper import get_port_speed


class OFSwitch13(OFSwitch):
    """
        Used to keep track of each node
        This object is used in the SDNTrace.switches
    """
    def __init__(self, ev, config_vars):
        OFSwitch.__init__(self, ev, config_vars)
        self.version = ofproto_v1_3.OFP_VERSION
        self.prepare_default_flow()

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

    def prepare_default_flow(self):
        """
            Push our default flow (MAC + LLDP + VLAN)
        """
        match = OFPMatch(eth_dst=lldp.LLDP_MAC_NEAREST_BRIDGE,
                         eth_type=ether.ETH_TYPE_LLDP,
                         vlan_vid=self.config_vars['topo_discovery']['vlan_discovery']
                          | ofproto_v1_3.OFPVID_PRESENT)
        self.add_default_flow(match)

    def install_color(self, color):
        """
            Prepare to send the FlowMod to install colored flows
            Args:
                color: eth_src to be used
        """
        mac_color = "ee:ee:ee:ee:ee:%s" % int(color, 2)
        self.push_color(OFPMatch(eth_src=mac_color))

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
