"""
    This file will be the core of the trace system.
"""
from ryu.lib.packet import ethernet, vlan, packet, ipv4, tcp
from ryu.lib import hub
import trace_pkt


def handle_trace(obj, entries, node, color, r_id):
    ctr = 0
    flag = False

    in_port, pkt = trace_pkt.generate_trace_pkt(entries, color, r_id)

    # Now send PacketOut
    # TODO: update the pkt.data with correct VLAN and PCP
    obj.send_packet_out(node, in_port, pkt.data)

    while True:
        hub.sleep(1)
        ctr += 1
        print 'len(obj.trace_pktIn) = %s' % len(obj.trace_pktIn)
        if len(obj.trace_pktIn) is 0:
            if ctr > 2:
                if ctr > 4:
                    flag = True
                    print 'populate with Done'
                    # update the trace_list
                    return
                else:
                    print 'send PacketOut again'
                    obj.send_packet_out(node, in_port, pkt.data)
            else:
                pass
        else:
            # what if we get two answers?
            for pIn in obj.trace_pktIn:
                # compate pIn.payload.data with r_id

                print "pIn"
                print pIn
                if True:
                    print 'It is over'
                    return


def process_probe_packet(ev, pkt):
    pktIn_dpid = '%016x' % ev.msg.datapath.id
    pktIn_port = ev.msg.in_port

    print 'process_probe_packet'
    print pkt[4]
    pkt_eth = pkt.get_protocols(ethernet.ethernet)[0]
    if pkt_eth.ethertype == 33024:
        pkt_vlan = pkt.get_protocols(vlan.vlan)[0]
        print pkt_vlan
        if pkt_vlan.pcp is not 0:
            # Validate to confirm it is a probe, not a user tagged packet
            # If not a probe, generate a PacketOut to send the packet back to
            # datapath
            # Once validated, the the whole pkt to an array
            pkt_tcp = pkt.get_protocols(tcp.tcp)[0]
            if pkt_tcp.dst_port == 1 and pkt_tcp.src_port == 1:
                print 'valid'
                return (pktIn_dpid, pktIn_port, pkt)
        else:
            print 'ignore'
    return False