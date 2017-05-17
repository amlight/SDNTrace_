"""

"""


from libs.core.singleton import Singleton
from libs.openflow.new_switch import new_switch
from libs.topology.links import Links
from libs.core.queues import topology_change


class Switches:
    """
    
    """
    __metaclass__ = Singleton

    def __init__(self):
        self._switches = dict()
        self.links = Links()

    # def __setitem__(self, key, value):
    #     self._switches[key] = value
    #
    # def __getitem__(self, key):
    #     return self._switches[key]

    def __len__(self):
        return len(self._switches)

    @topology_change
    def add_switch(self, ev):
        """
            Add the new switch to the self.switches dict
            Args:
                ev: FeatureReply
        """
        self._switches[ev.msg.datapath_id] = new_switch(ev)

    @topology_change
    def del_switch(self, ev):
        """
            In case of DEAD_DISPATCH, remove the switch from
            the self.switches dict
            Args:
                ev: DEAD_DISPATCH event
        """
        switch = self.get_switch(ev.datapath)
        if switch is not False:
            self.links.remove_switch(switch.name)
            self._switches.pop(switch.dpid)
            switch.print_removed()

    def get_switch(self, datapath, by_name=False):
        """
            Query the self.switches
            Args:
                datapath: datapath object <'str'> 16 digits
                by_name: if search is by datapath id

            Returns:
                OFSwitch10 or OFSwitch13 objects
                False if not found
        """
        for switch in self._switches.values():
            if by_name:
                if switch.name == datapath:
                    return switch
            else:
                if switch.obj.msg.datapath == datapath:
                    return switch
        return False

    def get_switches(self):
        return self._switches.values()

    def update_switch_address(self, switch_dp):
        """"
            Add tuple (IP, Port) to the OFSwitch class
        """
        dpid = '%016x' % switch_dp.id
        sw = self.get_switch(dpid, True)
        sw.update_addr(switch_dp.address)
