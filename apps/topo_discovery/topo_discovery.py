from ryu.lib import hub
from libs.core.singleton import Singleton
from libs.core.config_reader import ConfigReader
from libs.topology.switches import Switches
from apps.topo_discovery.lldp_helper import prepare_lldp_packet
from libs.topology.links import Links

class TopologyDiscovery(object):

    __metaclass__ = Singleton

    def __init__(self):
        self.config = ConfigReader()
        self.switches = Switches()
        self.links = Links()
        self.active = self._set_active()
        self.run = hub.spawn(self._topology_discovery)

    def _set_active(self):
        if self.config.topo.activate == 'on':
            print('Topology Discovery App activated')
            return True
        else:
            print('Topology Discovery App disabled')
            return False

    def _topology_discovery(self):
        """
            Keeps looping self.switches every PACKET_OUT_INTERVAL seconds
            Send a packet_out w/ LLDP to every port found
            Args:
                self
        """
        if self.active:
            vlan = self.config.topo.vlan_discovery
            while True:
                # Only send PacketOut + LLDP when more than one switch exists
                if len(self.switches) > 1:
                    for switch in self.switches.get_switches():
                        for port in switch.ports:
                            pkt = prepare_lldp_packet(switch, port, vlan)
                            switch.send_packet_out(port, pkt.data, lldp=True)
                hub.sleep(self.config.topo.packet_out_interval)

    def handle_packet_in_lldp(self, link):
        self.links.add_link(link)
        self.create_adjacencies(self.links)

    def create_adjacencies(self, links):
        """
            Everytime self.links is updated, update all
            adjacencies between switches
            Args:
                links: self.links
        """
        for switch in self.switches.get_switches():
            switch.create_adjacencies(self, links)
