from ryu.lib.packet import packet, lldp, ethernet, vlan
from ryu.ofproto import ether

import prepare


def prepare_default_flow(pkt, ev, vlan):
    """
        Prepare the LLDP for topology discovery
        Args:
            pkt: object SDNTrace
            ev: event
            vlan: VLAN used for LLDP match
        Returns:
            datapath, the match and actions for the FlowMod
    """
    datapath = ev.msg.datapath
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
    match = parser.OFPMatch(dl_dst=lldp.LLDP_MAC_NEAREST_BRIDGE,
                            dl_type=ether.ETH_TYPE_LLDP,
                            dl_vlan=vlan)
    actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
    return datapath, match, actions


def prepare_lldp_packet(node, port, vlan_id):
    """
        Prepare the LLDP frame to be used by PacketOut
        Args:
            node: destination node
            port: destination port
        Returns:
            an Ethernet+LLDP frame (data field of PacketOut)
    """

    pkt = packet.Packet()
    # Generate Ethernet frame
    dst = lldp.LLDP_MAC_NEAREST_BRIDGE
    src = 'ca:fe:ca:fe:ca:fe'

    if vlan_id > 1:
        ethertype = ether.ETH_TYPE_8021Q
        vlan_pkt = vlan.vlan(vid=vlan_id, ethertype=ether.ETH_TYPE_LLDP)
    else:
        ethertype = ether.ETH_TYPE_LLDP

    eth_pkt = ethernet.ethernet(dst, src, ethertype)
    pkt.add_protocol(eth_pkt)

    if vlan_id > 1:
        pkt.add_protocol(vlan_pkt)

    # Generate LLDP apcket
    dp = '%016x' % node.dpid
    chassis_subtype = lldp.ChassisID.SUB_LOCALLY_ASSIGNED
    tlv_chassis_id = lldp.ChassisID(subtype=chassis_subtype,
                                    chassis_id=dp)
    tlv_port_id = lldp.PortID(subtype=lldp.PortID.SUB_PORT_COMPONENT,
                              port_id=(b'%s' % port))
    tlv_ttl = lldp.TTL(ttl=120)
    tlv_end = lldp.End()
    tlvs = (tlv_chassis_id, tlv_port_id, tlv_ttl, tlv_end)
    lldp_pkt = lldp.lldp(tlvs)
    pkt.add_protocol(lldp_pkt)

    pkt.serialize()

    return pkt


def process_port_status(pkt, ev):
    """
        Adjust node_list with new ports or removing DELETED ports
        MGS.Reasons: 0 - port added, 1 - port deleted, 2 - port modified
        Args:
            pkt: Object SDNTrace
            ev: event
    """
    msg = ev.msg
    datapath = msg.datapath

    for node in pkt.node_list:
        if node.dpid is datapath.id:
            break

    if msg.reason is 1:
        if msg.desc.port_no in node.ports:
            node.ports.remove(msg.desc.port_no)
    else:
        if msg.desc.port_no not in node.ports:
            node.ports.append(msg.desc.port_no)


def remove_switch(pkt, ev):
    """
        Remove switch from node_list
        If DISPATCHER is received, it means switch is not connected
            and should be removed from node_list
        Args:
            pkt: SDNTrace object
            ev: event

    """
    for link in pkt.links:
        dpid = '%016x' % ev.datapath.id
        if dpid in link:
            pkt.links.remove(link)
    for node in pkt.node_list:
        if ev.datapath.id is node.dpid:
            pkt.node_list.remove(node)
            return


def process_packetIn(pkt, ev, links):
    """
        Process PacketIn - core of the SDNTrace
        PacketIn.action will define the reason: if content is LLDP,
            it means it is a topology discovery packet
            if content is not, it COULD be a trace file
        Args:
            pkt: SDNTrace object
            ev: event
            links: list of links known so far
        Returns:
            2, pkt if not LLDP
            1, list of current known links
    """
    pktIn_dpid = '%016x' % ev.msg.datapath.id
    # pktIn_port = ev.msg.in_port

    msg = ev.msg
    dp = msg.datapath
    ofp = dp.ofproto

    # If it is a OFPR_NO_MATCH, it means it is not our packet
    if ev.msg.reason == ev.msg.datapath.ofproto.OFPR_NO_MATCH:
        return 0, 0

    pkt = packet.Packet(ev.msg.data)
    pkt_eth = pkt.get_protocols(ethernet.ethernet)[0]
    next_header = pkt_eth.ethertype

    if pkt_eth.ethertype == ether.ETH_TYPE_8021Q:
        pkt_vlan = pkt.get_protocols(vlan.vlan)[0]
        next_header = pkt_vlan.ethertype

    # If not LLDP, it could be a probe Packet
    if next_header != ether.ETH_TYPE_LLDP:
        return 2, pkt

    # Extract LLDP from PacketIn.data
    pkt_lldp = pkt.get_protocols(lldp.lldp)[0]

    ChassisID = pkt_lldp.tlvs[0]
    # PortId = pkt_lldp.tlvs[1]
    pktOut_dpid = ChassisID.chassis_id
    # pktOut_port = PortId.port_id

    # print ('pIn dpid: %s pIn port: %s pOut dpid: %s pOut port: %s' %
    #       (pktIn_dpid, pktIn_port, pktOut_dpid, pktOut_port))

    link = pktIn_dpid, pktOut_dpid

    # Keep a single record between switches
    # It doesn't matter how many connections between them
    links.append(link)
    return 1, prepare.simplify_list_links(links)
