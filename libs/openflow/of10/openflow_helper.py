import itertools as it
import socket
import struct


def process_match(match):

    def process_subnet(wcard, field):

        if field == 'nw_src':
            OFPFW_NW_SRC_SHIFT = 8
            OFPFW_NW_SRC_MASK = 16128
            nw_bits = (wcard & OFPFW_NW_SRC_MASK) >> OFPFW_NW_SRC_SHIFT
        else:
            OFPFW_NW_DST_SHIFT = 14
            OFPFW_NW_DST_MASK = 1032192
            nw_bits = (wcard & OFPFW_NW_DST_MASK) >> OFPFW_NW_DST_SHIFT

        return (32 - nw_bits) if nw_bits < 32 else 0

    def _process_wildcard(wcard):
        wildcard = {1: 'in_port',
                    2: 'dl_vlan',
                    4: 'dl_src',
                    8: 'dl_dst',
                    16: 'dl_type',
                    32: 'nw_proto',
                    64: 'tp_src',
                    128: 'tp_dst',
                    1048576: 'dl_vlan_pcp',
                    2097152: 'nw_tos'}

        return wildcard.get(wcard)

    wildcard = match['wildcards']
    my_list = []

    for i in it.chain(range(0, 8), range(20, 22)):
        mask = 2 ** i
        aux = wildcard & mask
        if aux == 0:
            my_list.append(_process_wildcard(mask))

    ofmatch = dict()
    ofmatch['wildcards'] = wildcard
    for key in my_list:
        ofmatch[key] = match[key]

    for key in ['nw_src', 'nw_dst']:
        netmask = process_subnet(wildcard, key)
        if netmask != 0:
            ofmatch[key] = match[key] + '/' + str(netmask)

    return ofmatch


def process_actions(actions):

    def get_ip_from_long(long_ip):
        return socket.inet_ntoa(struct.pack('!L', long_ip))

    def eth_addr(a):
        """
            Print Mac Address in the human format
        Args:
            a: string "6s"
        Returns:
            mac in the human format
        """
        string = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x"
        mac = string % (ord(a[0]), ord(a[1]), ord(a[2]),
                        ord(a[3]), ord(a[4]), ord(a[5]))
        return mac

    actions_list = list()

    for action in actions:
        if action.type == 0:
            actions_list.append({'type': 'OFPActionOutput(0)', 'max_len': action.max_len,
                                 'port': action.port})
        elif action.type == 1:
            actions_list.append({'type': 'OFPActionVlanVid(1)', 'vlan_vid': action.vlan_vid})
        elif action.type == 2:
            actions_list.append({'type': 'OFPActionVlanPcp(2)', 'vlan_pcp': action.vlan_pcp})
        elif action.type == 3:
            actions_list.append({'type': 'OFPActionStripVlan(3)'})
        elif action.type == 4:
            actions_list.append({'type': 'OFPActionDlAddr(4)',
                                 'dl_addr': eth_addr(action.dl_addr)})
        elif action.type == 5:
            actions_list.append({'type': 'OFPActionSetDlSrc(5)',
                                 'dl_addr': eth_addr(action.dl_addr)})
        elif action.type == 6:
            actions_list.append({'type': 'OFPActionSetNwSrc(6)',
                                 'nw_addr': get_ip_from_long(action.nw_addr)})
        elif action.type == 7:
            actions_list.append({'type': 'OFPActionSetNwDst(7)',
                                 'nw_addr': get_ip_from_long(action.nw_addr)})
        elif action.type == 8:
            actions_list.append({'type': 'OFPActionSetNwTos(8)', 'tos': action.tos})
        elif action.type == 9:
            actions_list.append({'type': 'OFPActionSetTpSrc(9)', 'tp': action.tp})
        elif action.type == int('a', 16):
            actions_list.append({'type': 'OFPActionSetTpDst(10)', 'tp': action.tp})
        elif action.type == int('b', 16):
            actions_list.append({'type': 'OFPActionEnqueue(11)', 'queue_id': action.queue_id,
                                 'port': action.port})
        elif action.type == 65535:
            actions_list.append({'type': 'OFPActionVendor(65535)', 'vendor': action.vendor})

    return actions_list
