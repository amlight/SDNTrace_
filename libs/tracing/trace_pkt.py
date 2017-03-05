from ryu.lib.packet import ethernet, vlan, packet, ipv4, tcp


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


def generate_trace_pkt(entries, color, r_id):
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

    data = str(r_id)   # this will be the ID
    pkt.add_protocol(data)

    pkt.serialize()
    return in_port, pkt


def get_node_color_from_dpid(switches, dpid):
    for _, switch in switches.items():
        if dpid == switch.name:
            return switch, switch.color
    return 0


def get_vlan_from_pkt(data):
    pkt = packet.Packet(data)
    pkt_vlan = pkt.get_protocols(vlan.vlan)[0]
    return pkt_vlan.vid


def prepare_next_packet(obj, entries, result, ev):

    dpid =  result['trace']['dpid']
    node, color = get_node_color_from_dpid(obj.switches, dpid)

    entries['trace']['switch']['dpid'] =  dpid
    if ev.msg.version == 1:
        entries['trace']['switch']['in_port'] = ev.msg.in_port
    else:
        entries['trace']['switch']['in_port'] = ev.msg.match['in_port']
    entries['trace']['eth']['dl_vlan'] = get_vlan_from_pkt(ev.msg.data)

    return entries, color, node





