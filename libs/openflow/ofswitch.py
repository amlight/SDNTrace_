

class OFSwitch:
    """
        Used to keep track of each node
        This object is used in the SDNTrace.node_list
    """
    def __init__(self, ev, config_vars):
        self.obj = ev
        self.dpid = ev.msg.datapath_id
        self.ports, self.ports_dict = self._extract_ports()
        # To be used for coloring
        self.adjacencies_list = []
        self.color = "0"
        self.old_color = "0"
        self.name = self.datapath_id
        # Clear colored flows when connected
        self.clear_start = False
        # statistics
        self.flows = []
        # To avoid issues when deleting flows
        self.min_cookie_id = config_vars['MINIMUM_COOKIE_ID']
        self.cookie = self.min_cookie_id + 1
        self.min_cookie_id += 1