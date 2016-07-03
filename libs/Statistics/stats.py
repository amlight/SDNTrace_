
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
    add_flows_to_node(node, ev.msg.body)
    node.clear_start = True


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
    datapath.send_barrier()
    return


def add_flows_to_node(node, flows):
    """
        Add flows to node.flows in a JSON-supported way
        Args:
            node: node
            flows: OpenFlow entries associated to node 'node'
    """
    temp_flow = {} # each temporary flow
    temp_flows = [] # all temporary flows
    for flow in flows:
        temp_flow['match'] = flow.match
        temp_flow['actions'] = flow.actions
        temp_flow['byte_count'] = flow.byte_count
        temp_flow['duration_sec'] = flow.duration_sec
        temp_flow['duration_nsec'] = flow.duration_nsec
        temp_flow['packet_count'] = flow.packet_count
        temp_flow['priority'] = flow.priority
        temp_flows.append(temp_flow)
    node.flows = temp_flows
    return