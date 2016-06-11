
def flow_stats_reply(pkt, ev):
    """
        Process OFP_STAT_RES
        Args:
            ev: event
    """

    # Two main tasks:
    # 1 - Syncronize flow tables
    # 2 - Save stats

    # Get the node from node_list
    for node in pkt.node_list:
        if ev.msg.datapath.id == node.dpid:
            break

    # Check if node has cleat_start == False
    # If so, check if there is any colored flow
    for stat in ev.msg.body:
        if not node.clear_start and stat.match.dl_vlan_pcp is not 0:
            delete_colored_flow(pkt, node, stat)
            node.flows.append(stat)


def delete_colored_flow(pkt, node, flow):
    # print node.dpid
    # print match
    # print 'delete flow'
    datapath = node.obj.msg.datapath
    ofproto = datapath.ofproto
    op = ofproto.OFPP_CONTROLLER
    actions = [datapath.ofproto_parser.OFPActionOutput(op)]
    cookie = node.cookie
    flags = 0
    pkt.push_flow(datapath, cookie, flow.priority, ofproto.OFPFC_DELETE_STRICT,
                   flow.match, actions, flags)
    node.clear_start = True
    return
