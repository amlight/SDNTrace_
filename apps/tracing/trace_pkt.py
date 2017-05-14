from ryu.lib.packet import ethernet, vlan, packet, ipv4, tcp
from ryu.ofproto import ether
from apps.tracing.trace_msg import TraceMsg


def prepare_switch(switch, dpid, in_port):
    for idx in switch:
        if idx == 'dpid':
            dpid = switch[idx]
        elif idx == 'in_port':
            in_port = switch[idx]
    return dpid, in_port


def prepare_ethernet(eth, dl_src, dl_dst, dl_vlan, dl_type):
    for idx in eth:
        if idx == 'dl_src':
            dl_src = eth[idx]
        elif idx == 'dl_dst':
            dl_dst = eth[idx]
        elif idx == 'dl_vlan':
            dl_vlan = eth[idx]
        elif idx == 'dl_type':
            dl_type = eth[idx]
    return dl_src, dl_dst, dl_vlan, dl_type


def prepare_ip(ip, nw_src, nw_dst, nw_tos):
    for idx in ip:
        if idx == 'nw_src':
            nw_src = ip[idx]
        elif idx == 'nw_dst':
            nw_dst = ip[idx]
        elif idx == 'nw_tos':
            nw_tos = ip[idx]
    return nw_src, nw_dst, nw_tos


def prepare_tp(tp, tp_src, tp_dst):
    for idx in tp:
        if idx == 'tp_src':
            tp_src = tp[idx]
        elif idx == 'tp_dst':
            tp_dst = tp[idx]
    return tp_src, tp_dst


def generate_trace_pkt(entries, color, r_id, my_domain, interdomain=False):
    '''
        Receives the REST/PUT to generate a PacketOut
        data needs to be serialized
        template_trace.json is an example
    '''
    trace = {}
    switch = {}
    eth = {}
    ip = {}
    tp = {}

    # TODO Validate for dl_vlan. If empty, return error.

    dpid, in_port = 0, 65532
    if interdomain:
        dl_src = color
    else:
        dl_src = "ee:ee:ee:ee:ee:%s" % int(color,2)
    dl_dst = "ca:fe:ca:fe:ca:fe"
    dl_vlan, dl_type = 100, 2048
    nw_src, nw_dst, nw_tos = '127.0.0.1', '127.0.0.1', 0
    tp_src, tp_dst = 1, 1

    try:
        trace = entries['trace']
        switch = trace['switch']
        eth = trace['eth']
    except:
        pass

    try:
        ip = trace['ip']
    except:
        pass

    try:
        tp = trace['tp']
    except:
        pass

    if len(switch) > 0:
        dpid, in_port = prepare_switch(switch, dpid, in_port)

    if len(eth) > 0:
        dl_src, dl_dst, dl_vlan, dl_type = prepare_ethernet(eth, dl_src, dl_dst,
                                                            dl_vlan, dl_type)
    # if len(ip) > 0:
    nw_src, nw_dst, nw_tos = prepare_ip(ip, nw_src, nw_dst, nw_tos)

    # if len(tp) > 0:
    tp_src, tp_dst = prepare_tp(tp, tp_src, tp_dst)

    pkt = packet.Packet()

    eth_pkt = ethernet.ethernet(dst=dl_dst, src=dl_src, ethertype=33024)
    vlan_pkt = vlan.vlan(vid=dl_vlan, ethertype=int(dl_type))

    pkt.add_protocol(eth_pkt)
    pkt.add_protocol(vlan_pkt)

    if int(dl_type) == 2048:

        ip_pkt = ipv4.ipv4(dst=str(nw_dst), src=str(nw_src), tos=nw_tos,
                           proto=6)
        pkt.add_protocol(ip_pkt)
        tp_pkt = tcp.tcp(dst_port=int(tp_dst), src_port=int(tp_src))
        pkt.add_protocol(tp_pkt)

    msg = TraceMsg(r_id, my_domain)
    if interdomain:
        msg.set_interdomain()
    pkt.add_protocol(msg.data())
    pkt.serialize()
    return in_port, pkt


def get_node_color_from_dpid(switches, dpid):
    for switch in switches.get_switches():
        if dpid == switch.name:
            return switch, switch.color
    return 0


def get_vlan_from_pkt(data):
    pkt = packet.Packet(data)
    pkt_vlan = pkt.get_protocols(vlan.vlan)[0]
    return pkt_vlan.vid


def prepare_next_packet(switches, entries, result, ev):
    dpid =  result['dpid']
    switch, color = get_node_color_from_dpid(switches, dpid)

    entries['trace']['switch']['dpid'] =  dpid
    if ev.msg.version == 1:
        entries['trace']['switch']['in_port'] = ev.msg.in_port
    else:
        entries['trace']['switch']['in_port'] = ev.msg.match['in_port']

    entries['trace']['eth']['dl_vlan'] = get_vlan_from_pkt(ev.msg.data)

    return entries, color, switch


def gen_entries_from_packet_in(packet_in, datapath_id, in_port):
    """
        Extract the probe msg from a PacketIn.data
        Only happens for inter-domain traces
    Args:
        packet_in:

    Returns:
        dictionary with the fields to be used by the Tracer class
    """
    entries = dict()
    # Default Init
    entries['trace'] = {'switch': {}, 'eth': {}, 'ip': {}, 'tp': {}}
    entries['trace']['eth']['dl_dst'] = "ca:fe:ca:fe:ca:fe"
    entries['trace']['eth']['dl_vlan'] = 100
    entries['trace']['ip']['nw_src'] = '127.0.0.1'
    entries['trace']['ip']['nw_dst'] = '127.0.0.1'
    entries['trace']['ip']['nw_tos'] = 0
    entries['trace']['tp']['tp_src'] = 1
    entries['trace']['tp']['tp_dst'] = 1

    # Starting
    entries['trace']['switch']['dpid'] = datapath_id
    entries['trace']['switch']['in_port'] = in_port

    pkt = packet.Packet(packet_in.msg.data)
    pkt_eth = pkt.get_protocols(ethernet.ethernet)[0]

    entries['trace']['eth']['dl_dst'] = pkt_eth.dst

    if pkt_eth.ethertype == ether.ETH_TYPE_8021Q:
        pkt_vlan = pkt.get_protocols(vlan.vlan)[0]
        entries['trace']['eth']['dl_vlan'] = pkt_vlan.vid

        if int(pkt_vlan.ethertype) == 2048:
            pkt_ip = pkt.get_protocols(ipv4.ipv4)[0]
            entries['trace']['ip']['nw_src'] = pkt_ip.src
            entries['trace']['ip']['nw_dst'] = pkt_ip.dst
            entries['trace']['ip']['nw_tos'] = pkt_ip.tos

            if pkt_ip.proto == 6:
                pkt_tp = pkt.get_protocols(tcp.tcp)[0]
                entries['trace']['tp']['tp_src'] = pkt_tp.src_port
                entries['trace']['tp']['tp_dst'] = pkt_tp.dst_port

    msg = TraceMsg()
    msg.import_data(pkt[-1])
    entries['trace']['data'] = msg.data()

    return entries