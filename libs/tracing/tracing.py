"""
    This file will be the core of the trace system.
"""
from ryu.lib.packet import ethernet
from libs.tracing.trace_msg import TraceMsg


def process_probe_packet(ev, pkt, in_port, configs, switch):
    """
        Used by sdntrace.packet_in_handler
        Args:
            ev: msg
            pkt: data
            configs: SDNTrace configs - used for inter-domain
        Returns:
            False in case it is not a probe packet
            or
            (pktIn_dpid, pktIn_port, pkt[4], pkt, ev)
    """
    color = configs['inter-domain']['color'].split(',')[1]
    inter_port = switch.inter_domain_ports
    my_domain = configs['inter-domain']['my_domain']
    pktIn_dpid = '%016x' % ev.msg.datapath.id
    pktIn_port = in_port

    pkt_eth = pkt.get_protocols(ethernet.ethernet)[0]
    msg = TraceMsg()
    msg.import_data(pkt[-1])
    if msg.type == 'intra' and msg.local_domain == my_domain:
        # Intra-domain
        if pkt_eth.src.find('ee:ee:ee:ee:ee:') == 0:
            return 'Intra', (pktIn_dpid, pktIn_port, pkt[-1], pkt, ev)

    elif pkt_eth.src == color and str(in_port) in inter_port:
        return 'Inter', (pktIn_dpid, pktIn_port, pkt[-1], pkt, ev)

    else:
        # TODO: Understand possibilitie:
        # 1 - put it back? Drop? For, drop it.
        #print('ignore')
        return None, False
