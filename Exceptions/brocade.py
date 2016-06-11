"""
    Because Brocade and some vendors do not support OFPP_TABLE, a workaround was created to
    'virtually' trace the Flows
    Instead of going through the flow table, flow_stat_res are being used to know to where send PacketOuts to
"""






def send_trace_probes(obj, entries, node, color, r_id):
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