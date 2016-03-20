from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
# from ryu.lib import addrconv
# from ryu.ofproto import ofproto_v1_0
from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link
from ryu.ofproto.ofproto_v1_0_parser import OFPPhyPort


class SDNTrace(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(SDNTrace, self).__init__(*args, **kwargs)
        self.topology_api_app = self

    def add_flow(self, datapath, in_port, dst, actions):
        ofproto = datapath.ofproto

        if in_port is not 0 and dst is not 0:
            match = datapath.ofproto_parser.OFPMatch(in_port=in_port,
                                                     nw_dst=(dst))
        elif in_port is 0 and dst is 0:
            match = datapath.ofproto_parser.OFPMatch()
        else:
            match = datapath.ofproto_parser.OFPMatch(in_port=in_port)

        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0, command=ofproto.OFPFC_ADD,
            idle_timeout=0, hard_timeout=0, priority=40000, actions=actions)
        print mod
        datapath.send_msg(mod)

    # @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg

        print msg.in_port
        print msg.buffer_id
        print msg.total_len
        print msg.reason

    # @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto

        out_port = ofproto.OFPP_NONE
        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

        self.add_flow(datapath, msg.desc.port_no, 0, actions)

        print datapath.id
        print msg.reason
        print msg.desc.port_no
        print msg.desc.hw_addr

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        print datapath
        #print ('OFPSwitchFeatures received: '
        #       'datapath_id=0x%016x n_buffers=%d '
        #       'n_tables=%d capabilities=0x%08x ports=%s' %
        #       (msg.datapath_id, msg.n_buffers, msg.n_tables,
        #        msg.capabilities, msg.ports))

        out_port = ofproto.OFPP_CONTROLLER
        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

        ports = len(msg.ports) - 1
        offset = ofproto.OFP_SWITCH_FEATURES_SIZE
        for _i in range(ports):
            port = OFPPhyPort.parser(msg.buf, offset)
            offset += ofproto.OFP_PHY_PORT_SIZE
            self.add_flow(datapath, port.port_no, "10.0.0.2", actions)
            print port.name

    # @set_ev_cls(event.EventSwitchEnter)
    def get_topology_data(self, ev):
        switch_list = get_switch(self.topology_api_app, None)
        switches = [switch.dp.id for switch in switch_list]
        links_list = get_link(self.topology_api_app, None)
        links = [(link.src.dpid, link.dst.dpid, {'port': link.src.port_no}) for link in links_list]
        print 'links ',
        print links
        self.define_color(links)

    def define_colors(self, links):
        # After each link detected, update the graph and install a colored flow
        # If necessary, remove an old color and install a new one
        self.graph = self
        self.colored_switches = []

        # Color source switch
        # Is the switch already colored?
        # If no, define color 0


        # Color destination switch

        # Create graph
        # Are both endpoints "colored

