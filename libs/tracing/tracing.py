"""
    This file will be the core of the trace system.
"""
from ryu.lib.packet import ethernet


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
