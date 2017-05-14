from ryu.lib.packet import packet, lldp, ethernet, vlan
from ryu.ofproto import ether


def prepare_lldp_packet(node, port, vlan_id):
    """
        Prepare the LLDP frame to be used by PacketOut
        Args:
            node: destination node
            port: destination port
            vlan_id: vlan tag to be added to pkt
        Returns:
            an Ethernet+LLDP frame (data field of PacketOut)
    """

    pkt = packet.Packet()
    # Generate Ethernet frame
    dst = lldp.LLDP_MAC_NEAREST_BRIDGE
    src = 'ca:fe:ca:fe:ca:fe'
    vlan_pkt = None

    if vlan_id > 1:
        ethertype = ether.ETH_TYPE_8021Q
        vlan_pkt = vlan.vlan(vid=vlan_id, ethertype=ether.ETH_TYPE_LLDP)
    else:
        ethertype = ether.ETH_TYPE_LLDP

    eth_pkt = ethernet.ethernet(dst, src, ethertype)
    pkt.add_protocol(eth_pkt)

    if vlan_id > 1:
        pkt.add_protocol(vlan_pkt)

    # Generate LLDP packet
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
