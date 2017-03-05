"""
    This file will be the core of the trace system.
"""
from ryu.lib import hub
from ryu.lib.packet import ethernet
from ryu.ofproto import ofproto_v1_0, ofproto_v1_3
import trace_pkt


def handle_trace(obj, entries, node, color, r_id):
    """
        Perform the SDNTrace itself
        Args:
            obj: SDNTrace class
            entries: user's request
            node: starting node
            color: starting node's color
            r_id: request_id sent to user
    """
    trace_result = []
    ended = False

    while not ended:
        # Prepare pkt using user's input
        in_port, pkt = trace_pkt.generate_trace_pkt(entries, color, r_id)
        # Send packet out, wait for result - 3 sec time out
        result, ev = trace_send_packet_out(obj, node, in_port, r_id, pkt)
        # If time out, pkt will be False
        if not ev:
            ended = True
        else:
            # If pkt not False ...
            if result['trace'] == 'done':
                print "That is it!"
                ended = True
            else:
                # print result
                trace_result.append(result)
                is_loop = check_loop(trace_result)
                if is_loop:
                    trace_result.append('loop')
                    return trace_result
                # Prepare next packet
                prepare = trace_pkt.prepare_next_packet
                entries, color, node = prepare(obj, entries, result, ev)

                #print 'entries, color'
                #print entries, color

    return trace_result


def trace_send_packet_out(obj, node, in_port, r_id, pkt):
    """
        Sends the Trace probe and wait for result.
        If result is not received in 3 seconds, it is done.
        Args:
            obj: class SDNTrace
            node: target node
            in_port: target port
            r_id: result_id created at the REST
            pkt: ethernet frame to send (PacketOut.data)
        Returns:
            {'trace': 'done'} in case of timeout
            {'trace': {'switch': pIn[0], "port": pIn[1], "pkt": pkt[3]}} in case success
    """
    ctr = 0
    rest_result = {}

    node.send_packet_out(in_port, pkt.data)

    print 'tracing node: %s in_port %s ' % (node.name, in_port)
    while True:
        hub.sleep(1)
        ctr += 1
        # print 'len(obj.trace_pktIn) = %s' % len(obj.trace_pktIn)
        if len(obj.trace_pktIn) is 0:
            if ctr > 2:
                print 'done'
                return {'trace': 'done'}, False
            else:
                print 'sending PacketOut again'
                node.send_packet_out(in_port, pkt.data)
        else:
            # what if we get two answers?
            # get the first, delete other entries with same r_id?
            for pIn in obj.trace_pktIn:
                # compate pIn.payload.data with r_id
                # print(r_id, pIn)
                if r_id == int(pIn[2]):
                    rest_result['trace'] = {'dpid': pIn[0], "port": pIn[1]}
                    # print 'result',
                    # print rest_result
                    clear_trace_pktIn(obj.trace_pktIn, r_id)
                    return rest_result, pIn[-1]


def clear_trace_pktIn(trace_pktIn, r_id):
    for pIn in trace_pktIn:
        if r_id == int(pIn[2]):
            trace_pktIn.remove(pIn)


def check_loop(trace_result):
    i = 0
    last = len(trace_result) - 1
    while i < last:
        # print i, last
        if trace_result[i] == trace_result[last]:
            print trace_result[i]['trace'], trace_result[last]['trace']
            return last
        i += 1
    return 0


def process_probe_packet(ev, pkt, in_port):
    """
        Used by sdntrace.packet_in_handler
        Args:
            ev: msg
            pkt: data
        Returns:
            False in case it is not a probe packet
            or
            (pktIn_dpid, pktIn_port, pkt[4], pkt, ev)
    """
    pktIn_dpid = '%016x' % ev.msg.datapath.id
    pktIn_port = in_port

    pkt_eth = pkt.get_protocols(ethernet.ethernet)[0]
    if pkt_eth.src.find('ee:ee:ee:ee:ee:') == 0:
        return (pktIn_dpid, pktIn_port, pkt[-1], pkt, ev)
    else:
        # TODO: Understand possibilities
        print 'ignore'
    return False
