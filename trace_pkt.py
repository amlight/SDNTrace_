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


def generate_trace_pkt(entries, color):
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

    dpid, in_port = 0, 65532
    dl_src, dl_dst = "ca:fe:ca:fe:00:00", "ca:fe:ca:fe:ca:fe"
    dl_vlan, dl_type = 0, 2048
    nw_src, nw_dst, nw_tos = '127.0.0.1', '127.0.0.1', 0
    tp_src, tp_dst = 1, 1

    try:
        trace = entries['trace']
        switch = trace['switch']
        eth = trace['eth']
        ip = trace['ip']
        tp = trace['tp']
    except:
        pass

    if len(switch) > 0:
        dpid, in_port = prepare_switch(switch, dpid, in_port)

    if len(eth) > 0:
        dl_src, dl_dst, dl_vlan, dl_type = prepare_ethernet(eth, dl_src, dl_dst,
                                                            dl_vlan, dl_type)
    if len(ip) > 0:
        nw_src, nw_dst, nw_tos = prepare_ip(ip, nw_src, nw_dst, nw_tos)

    if len(tp) > 0:
        tp_src, tp_dst = prepare_tp(tp, tp_src, tp_dst)

    pkt = packet.Packet()

    if dl_vlan is 0:
        eth_pkt = ethernet.ethernet(dst=dl_dst, src=dl_src, ethertype=dl_type)
        pkt.add_protocol(eth_pkt)
    else:
        eth_pkt = ethernet.ethernet(dst=dl_dst, src=dl_src, ethertype=33024)
        vlan_pkt = vlan.vlan(vid=dl_vlan, ethertype=dl_type, pcp=int(color, 2))
        pkt.add_protocol(eth_pkt)
        pkt.add_protocol(vlan_pkt)

    if dl_type is 2048:
        ip_pkt = ipv4.ipv4(dst=str(nw_dst), src=str(nw_src), tos=nw_tos,
                           proto=6)
        pkt.add_protocol(ip_pkt)
        tp_pkt = tcp.tcp(dst_port=tp_dst, src_port=tp_src)
        pkt.add_protocol(tp_pkt)
        data = "jab"
        pkt.add_protocol(data)

    pkt.serialize()
    print pkt
    return in_port, pkt


def process_probe_packet(ev, pkt):
    pktIn_dpid = '%016x' % ev.msg.datapath.id
    pktIn_port = ev.msg.in_port

    print 'process_probe'
    pkt_eth = pkt.get_protocols(ethernet.ethernet)[0]
    if pkt_eth.ethertype == 33024:
        pkt_vlan = pkt.get_protocols(vlan.vlan)[0]
        print pkt_vlan
        if pkt_vlan.pcp is not 0:
            # Validate to confirm it is a probe, not a user tagged packet
            # If not a probe, generate a PacketOut to send the packet back to
            # datapath
            # Once validated, the the whole pkt to an array
            print 'valid'
            return (pktIn_dpid, pktIn_port, pkt)
    return False

    return
