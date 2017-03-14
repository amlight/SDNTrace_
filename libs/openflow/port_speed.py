"""
    Generic translate from number to name port speed
"""

from ryu.ofproto import ofproto_v1_0
from ryu.ofproto import ofproto_v1_3

from libs.openflow.of10.port_helper import get_port_speed as of10_helper
from libs.openflow.of13.port_helper import get_port_speed as of13_helper


def get_speed_name(version, desc):

    if version == ofproto_v1_0.OFP_VERSION:
        return of10_helper(desc.curr)

    elif version == ofproto_v1_3.OFP_VERSION:
        return of13_helper(desc.curr_speed)
