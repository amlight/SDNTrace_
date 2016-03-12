from ryu.lib.packet import packet, lldp, ethernet
from ryu.ofproto import ether
import prepare


def prepare_default_flow(pkt, ev):
    datapath = ev.msg.datapath
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
    match = parser.OFPMatch(dl_dst=lldp.LLDP_MAC_NEAREST_BRIDGE,
                            dl_type=ether.ETH_TYPE_LLDP)
    actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
    return datapath, match, actions


def prepare_lldp(node, port):
    '''
        Prepara LLDP message to be used by PacketOut
    '''

    pkt = packet.Packet()
    # Generate Ethernet frame
    dst = lldp.LLDP_MAC_NEAREST_BRIDGE
    src = 'ca:fe:ca:fe:ca:fe'
    ethertype = ether.ETH_TYPE_LLDP
    eth_pkt = ethernet.ethernet(dst, src, ethertype)
    pkt.add_protocol(eth_pkt)

    # Generate LLDP apcket
    dp = '%016x' % node.dpid
    tlv_chassis_id = lldp.ChassisID(subtype=lldp.ChassisID.SUB_LOCALLY_ASSIGNED,
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
    for node in pkt.node_list:
        if ev.datapath.id is node.dpid:
            pkt.node_list.remove(node)


def process_packetIn(pkt, ev, links):
    '''
        Two types of PacketIn expected
            - LLDP: Topology Discovery
            - Traces: VLAN_PCP set
    '''
    pktIn_dpid = '%016x' % ev.msg.datapath.id
    # pktIn_port = ev.msg.in_port

    pkt = packet.Packet(ev.msg.data)
    pkt_eth = pkt.get_protocols(ethernet.ethernet)[0]

    # If not LLDP, it could be a probe Packet
    if pkt_eth.ethertype != ether.ETH_TYPE_LLDP:
        return 2, pkt

    # Extract LLDP from PacketIn.data
    # Check if is LLDP
    pkt_lldp = pkt.get_protocols(lldp.lldp)[0]

    ChassisID = pkt_lldp.tlvs[0]
    # PortId = pkt_lldp.tlvs[1]
    pktOut_dpid = ChassisID.chassis_id
    # pktOut_port = PortId.port_id

    # print ('pIn dpid: %s pIn port: %s pOut dpid: %s pOut port: %s' %
    #       (pktIn_dpid, pktIn_port, pktOut_dpid, pktOut_port))

    link = pktIn_dpid, pktOut_dpid

    # Keep a single record between switches
    # It doesn't matter how many connectios between them
    links.append(link)
    return 1, prepare.simplify_list_links(links)
