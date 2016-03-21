"""
    Because Brocade and some vendors do not support OFPP_TABLE, a workaround was created to
    'virtually' trace the Flows
    Instead of going through the flow table, flow_stat_res are being used to know to where send PacketOuts to
"""


def send_stat_req(ev, node):
    datapath = node.obj.msg.datapath
    parser = datapath.ofproto_parser
    ofproto = datapath.ofproto
    flags = 0
    match = parser.OFPMatch()
    table_id = 0
    req = parser.OFPFlowStatsRequest(datapath, flags, match, table_id,
                                     ofproto.OFPP_NONE)
    datapath.send_msg(req)


def flow_stats_reply(ev):
    """
        Process Flow Stats
        ev = packet received
    """
    return
    body = ev.msg.body
    for stat in body:
        # print stat
        print ('%016x %s %s %8d %8d' %
               (ev.msg.datapath.id, stat.match, stat.actions, stat.packet_count, stat.byte_count))


def send_trace_probes(node, in_port, pkt):
    parser = node.obj.msg.datapath.ofproto_parser
    datapath = node.obj.msg.datapath
    ofproto = node.obj.msg.ofproto
    buffer_id = ofproto.OFP_NO_BUFFER
    for port in node.ports:
        if port != in_port:
            actions = [parser.OFPActionOutput(port)]
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=buffer_id, in_port=ofproto.OFPP_NONE,
                                      actions=actions, data=pkt.data)
            datapath.send_msg(out)