"""

"""
from ryu.ofproto.ofproto_v1_3_parser import *
from libs.tcpip.format import eth_addr, ip_addr, ip6_addr


def get_field_ryu(type_field):
    """

    Args:
        type_field:

    Returns:

    """
    names = {'MTInPort': 'in_port',
             'MTMetadata': 'metadata',
             'MTInPhyPort': 'in_phy_port',
             'MTEthSrc': 'eth_src',
             'MTEthDst': 'eth_dst',
             'MTVlanVid': 'vlan_vid',
             'MTEthType': 'eth_type',
             'MTVlanPcp': 'vlan_pcp',
             'MTIPDscp': 'ip_dscp',
             'MTIPECN': 'ip_ecn',
             'MTIPProto': 'ip_proto',
             'MTIPV4Src': 'ipv4_src',
             'MTIPV4Dst': 'ipv4_dst',
             'MTTCPSrc': 'tcp_src',
             'MTTCPDst': 'tcp_dst',
             'MTUDPSrc': 'udp_src',
             'MTUDPDst': 'udp_dst',
             'MTSCTPSrc': 'sctp_src',
             'MTSCTPDst': 'sctp_dst',
             'MTICMPV4Type': 'icmpv4_type',
             'MTICMPV4Code': 'icmpv4_code',
             'MTArpOp': 'arp_op',
             'MTArpSpa': 'arp_spa',
             'MTArpTpa': 'arp_tpa',
             'MTArpSha': 'arp_sha',
             'MTArpTha': 'arp_tha',
             'MTIPv6Src': 'ipv6_src',
             'MTIPv6Dst': 'ipv6_dst',
             'MTIPv6Flabel': 'ipv6_flabel',
             'MTMplsLabel': 'mpls_label',
             'MTICMPV6Type': 'icmpv6_type',
             'MTICMPV6Code': 'icmpv6_code',
             'MTIPv6NdTarget': 'ipv6_nd_target',
             'MTIPv6NdSll': 'ipv6_nd_sll',
             'MTIPv6NdTll': 'ipv6_nd_tll',
             'MTMplsTc': 'mpls_tc',
             'MTMplsBos': 'mpls_bos',
             'MTPbbIsid': 'pbb_isid',
             'MTTunnelId': 'tunnel_id',
             'MTIPv6ExtHdr': 'ipv6_hexthdr'
             }

    class_name = type_field.__name__
    return names[class_name]


def format_option(field, option):
    """

    Args:
        field:
        option:

    Returns:

    """
    if field in ['eth_src', 'eth_dst', 'arp_spa', 'arp_tpa', 'arp_sha', 'arp_tha']:
        return eth_addr(option)
    elif field in ['eth_type']:
        return hex(option)
    elif field in ['ipv4_src', 'ipv4_dst']:
        return ip_addr(option)
    elif field in ['ipv6_src', 'ipv6_dst', 'ipv6_nd_sll', 'ipv6_nd_tll']:
        return ip6_addr(option)

    return option


def get_fields(oxm_fields):
    """

    Args:
        oxm_fields:

    Returns:

    """
    fields = list()

    for field in oxm_fields:

        oxm_value = dict()
        # oxm_value['len'] = field.length
        oxm_value['field'] = get_field_ryu(type(field))
        oxm_value['value'] = format_option(oxm_value['field'], field.value)

        if 'mask' in field.__dict__.keys():
            if field.mask is not None:
                oxm_value['mask'] = format_option(oxm_value['field'], field.mask)

        fields.append(oxm_value)
        del oxm_value

    return fields


def process_match(flow_match):
    """
    Args:
        flow_match

        "match": {
                 "OFPMatch": {
                     "length": 22,
                     "oxm_fields": [
                         {
                             "OXMTlv": {
                                 "field": "in_port",
                                 "mask": null,
                                 "value": 6
                             }
                         },
                         {
                             "OXMTlv": {
                                 "field": "eth_src",
                                 "mask": null,
                                 "value": "f2:0b:a4:7d:f8:ea"
                             }
                         }
                     ],
                     "type": 1
                 }
             },
    Args:
        match:

    Returns:

    """

    match = dict()
    match['length'] = flow_match.length
    match['type'] = flow_match.type
    match['oxm'] = get_fields(flow_match.fields)

    return match


def get_instruction(instruction_type):
    """
        OFPIT_GOTO_TABLE = 1            # Setup the next table in the lookup pipeline.
        OFPIT_WRITE_METADATA = 2        # Setup the metadata field for use later in
                                        # pipeline.
        OFPIT_WRITE_ACTIONS = 3         # Write the action(s) onto the datapath
                                        # action set
        OFPIT_APPLY_ACTIONS = 4         # Applies the action(s) immediately
        OFPIT_CLEAR_ACTIONS = 5         # Clears all actions from the datapath action
                                        # set
        OFPIT_METER = 6                 # Apply meter (rate limiter)
        OFPIT_EXPERIMENTER = 0xFFFF     # Experimenter instruction
    """
    instructions = {1: 'OFPIT_GOTO_TABLE',
                    2: 'OFPIT_WRITE_METADATA',
                    3: 'OFPIT_WRITE_ACTIONS',
                    4: 'OFPIT_APPLY_ACTIONS',
                    5: 'OFPIT_CLEAR_ACTIONS',
                    6: 'OFPIT_METER',
                    65535: 'OFPIT_EXPERIMENTER'}

    try:
        return instructions[instruction_type]
    except KeyError:
        return instruction_type


def get_port(port):
    """

    """
    # TODO: complete this dict with all special ports
    ports = {4294967293: 'CONTROLLER'}
    try:
        return ports[port]
    except KeyError:
        return port


def get_action(action):
    """

    """
    response = dict()
    response['type'] = type(action).__name__
    if action.type == 0:
        response['port'] = get_port(action.port)
        if action.max_len != 0:
            response['max_len'] = action.max_len
    elif action.type == 17:
        response['ethertype'] = hex(action.ethertype)
    elif action.type == 25:
        response['field'] = action.key
        response['value'] = action.value - 4096 if action.key == 'vlan_vid'\
            else action.value

    return response


def get_actions(actions):
    """

    """
    action_dict = list()
    for action in actions:
        action_dict.append(get_action(action))
    return action_dict


def process_instructions(instructions):
    """


    """
    instruction_value = dict()

    for instruction in instructions:
        instruction_value['type'] = get_instruction(instruction.type)
        instruction_value['actions'] = get_actions(instruction.actions)

    return instruction_value


def process_flows_stats(flow):
    """
        /sdntrace/switches/{dpid}/flows
       {
            "dpid": "0000000000000001",
            "number_flows": 5,
            "flows": [
                {
                    "idle_timeout": 0,
                    "cookie": 2000002,
                    "priority": 50001,
                    "hard_timeout": 0,
                    "byte_count": 0,
                    "duration_nsec": 71000000,
                    "packet_count": 0,
                    "duration_sec": 4,
                    "table_id": 0,
                    "match": [
                        {

                        },
                        ...
                    ],
                    "instructions": [
                        {

                        },
                        ...
                    ]
                }
                ...
            ]
        }
        or
        {} if not found
    """
    match = process_match(flow.match)
    instructions = process_instructions(flow.instructions)

    # TODO: translate flags

    flow_stats = {
        "table_id": flow.table_id,
        "duration_sec": flow.duration_sec,
        "duration_nsec": flow.duration_nsec,
        "priority": flow.priority,
        "idle_timeout": flow.idle_timeout,
        "hard_timeout": flow.hard_timeout,
        "flags": flow.flags,
        "cookie": flow.cookie,
        "packet_count": flow.packet_count,
        "byte_count": flow.byte_count,
        "match": match,
        "instructions": instructions
    }

    return flow_stats
