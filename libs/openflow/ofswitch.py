"""
    OpenFlow generic switch class
"""


from ryu.ofproto import ether
from ryu.lib.packet import packet, lldp, ethernet, vlan
from libs.coloring.auxiliary import simplify_list_links


class OFSwitch():
    """
        Used to keep track of each node
        This object is used in the SDNTrace.switches
    """
    def __init__(self, ev, config_vars):
        self.obj = ev
        self.dpid = ev.msg.datapath_id
        self.ports = dict()
        self.adjacencies_list = []  # list of DPIDs or OFSwitch10?
        self.color = "0"
        self.old_color = "0"
        self.name = self.datapath_id
        # TODO: Clear colored flows when connected
        # self.delete_colored_flows()
        self.clear_start = False
        # To avoid issues when deleting flows
        self.config_vars = config_vars
        # set cookie
        self.set_cookie()
        self.add_default_flow()

    @property
    def datapath_id(self):
        """
            Property to print datapath_id in the hex format
            Returns:
                dpid in hex
        """
        return '%016x' % self.dpid

    def set_cookie(self):
        self.min_cookie_id = self.config_vars['MINIMUM_COOKIE_ID']
        self.cookie = self.min_cookie_id + 1
        self.min_cookie_id += 1