from ryu.lib.packet import lldp
from ryu.ofproto import ether


class OFSwitch13(object):
    """
        Used to keep track of each node
        This object is used in the SDNTrace.switches
    """
    def __init__(self, ev, config_vars):
        self.obj = ev
        self.dpid = ev.msg.datapath_id
        self.ports = self._extract_ports()
        print(self.ports)
        self.adjacencies_list = []
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
                port = OFPPhyPort.parser(self.obj.msg.buf, offset)
                if port.port_no < ofproto.OFPP_MAX:
                    curr = get_port_speed(port.curr)
                    ports[port.port_no] = {"port_no": port.port_no,
                                           "name": port.name,
                                           "speed": curr}
                offset += ofproto.OFP_PHY_PORT_SIZE
        return ports

    def set_cookie(self):
        self.min_cookie_id = self.config_vars['MINIMUM_COOKIE_ID']
        self.cookie = self.min_cookie_id + 1
        self.min_cookie_id += 1

    def add_default_flow(self):
        """
            Push our default flow (MAC + LLDP + VLAN)
        """
        vlan = self.config_vars['VLAN_DISCOVERY']
        datapath = self.obj.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(dl_dst=lldp.LLDP_MAC_NEAREST_BRIDGE,
                                dl_type=ether.ETH_TYPE_LLDP,
                                dl_vlan=vlan)
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
        self.push_flow(datapath, 0, 0, ofproto.OFPFC_ADD, match, actions)

    @staticmethod
    def send_packet_out(switch, port, data, lldp=False):
        """
            Sends PacketOut - Serializes Traces and LLDP packets for topology discovery
            Args:
                node: node to send PacketOut
                port: if LLDP: port to send PacketOut out. if Trace: in_port field
                data: Ethernet frame to be send
                lldp: used in case of LLDP packets (used by _topology_discovery)
        """
        parser = switch.obj.msg.datapath.ofproto_parser
        datapath = switch.obj.msg.datapath
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
                 flags: flow mod flags
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
                self.ports[msg.desc.port_no] = msg.desc.name

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
        flow_prio = self.config_vars['FLOW_PRIORITY']
        self.push_flow(datapath, cookie, flow_prio, ofproto.OFPFC_DELETE_STRICT,
                       match, actions, flags)
        return

    def create_adjacencies(self, obj, links):
        self.adjacencies_list[:] = []
        for link in links:
            if link[0] == self.name:
                neighbor = obj.get_switch(link[1], True)
                self.adjacencies_list.append(neighbor)
            elif link[1] == self.name:
                neighbor = obj.get_switch(link[0], True)
                self.adjacencies_list.append(neighbor)
