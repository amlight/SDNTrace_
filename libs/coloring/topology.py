from ryu.lib.packet import packet, lldp, ethernet, vlan
from ryu.ofproto import ether
import prepare


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
