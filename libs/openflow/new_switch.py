"""
    
"""
from ryu.ofproto import ofproto_v1_0, ofproto_v1_3
from libs.openflow.of10.ofswitch import OFSwitch10
from libs.openflow.of13.ofswitch import OFSwitch13


def new_switch(ev):
    """
        Instantiate an OpenFlow 1.0 or 1.3 switch
        Args:
            ev: FeatureReply received
        Returns:
            OFSwitch1* class
    """
    if ev.msg.version == ofproto_v1_0.OFP_VERSION:
        return OFSwitch10(ev)
    elif ev.msg.version == ofproto_v1_3.OFP_VERSION:
        return OFSwitch13(ev)
    return False
