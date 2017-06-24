"""
    
"""


from ryu.lib import hub
from libs.core.singleton import Singleton
from libs.core.config_reader import ConfigReader
from libs.topology.switches import Switches
from apps.topo_discovery.lldp_helper import prepare_lldp_packet
from libs.topology.links import Links
from libs.core.queues import topology_refresher_queue
from libs.core.signals import called_on


class TopologyDiscovery(object):
    """
    
    """

    __metaclass__ = Singleton

    def __init__(self):
        self.active = self._set_active()
        self.run = hub.spawn(self._topology_discovery)
        self._topology = None

    @staticmethod
    def _set_active():
        """
            Check configuration to see if it is enabled
            Returns:
                True:
                False:
        """
        if ConfigReader().topo.activate == 'on':
            print('Topology Discovery App activated')
            return True
        else:
            print('Topology Discovery App disabled')
            return False

    def _topology_discovery(self):
        """
            Keeps looping Switches() every PACKET_OUT_INTERVAL seconds
            Send a packet_out w/ LLDP to every port found
        """
        if self.active:
            vlan = ConfigReader().topo.vlan_discovery
            while True:
                # Only send PacketOut + LLDP when more than one switch exists
                if len(Switches()) > 1:
                    for switch in Switches().get_switches():
                        for port in switch.ports:
                            pkt = prepare_lldp_packet(switch, port, vlan)
                            switch.send_packet_out(port, pkt.data, lldp=True)
                hub.sleep(ConfigReader().topo.packet_out_interval)

    @staticmethod
    @called_on(topology_refresher_queue)
    def _listen_for_topology_changes():
        """
            Refresh the topology.
            TODO: remove remove staticmethod
        """
        TopologyDiscovery()._update_topology()

    def handle_packet_in_lldp(self, link):
        """
            Once a LLDP + PacketIn is received, send link to Links.
            Links will add create an entry if both directions are seen.
            If so, add the discovered link, updated adjacencies and 
            update topology
            Args:
                link: Class Link
        """
        created = Links().process_new_link(link)
        if created:
            self.create_adjacencies(Links())
            self._update_topology()

    @staticmethod
    def create_adjacencies(links):
        """
            Everytime Links() is updated, update all
            adjacencies between switches
            Args:
                links: Links()
        """
        for switch in Switches().get_switches():
            switch.create_adjacencies(links)

    def _update_topology(self):
        """
            Update topology
        """

        self._topology = {}

        # Collect all inter-domain info from the configuration file
        inter_conf = ConfigReader().interdomain.locals
        inter_names = ConfigReader().interdomain.neighbors

        # Create a temporary dictionary with all inter-domain ports adding
        #  the remote domain's name to it
        inter = dict()
        for node in inter_conf:
            sw_dpid, sw_port = node.split(':')
            inter[sw_dpid] = {}
            for neighbor in inter_names:
                local = ConfigReader().interdomain.get_local_sw(neighbor)
                if local == sw_dpid:
                    inter[sw_dpid][sw_port] = {'type': 'interdomain',
                                               'domain_name': neighbor}

        # Create the final dictionary with all switches and ports
        #   Uses the inter dict to add inter-domain info. If no inter-domain
        #   is found, assume it is a host port - for now.
        switches = dict()
        for switch in Switches().get_switches():
            switches[switch.name] = {}
            for port in switch.ports:
                try:
                    switches[switch.name][port] = inter[switch.name][str(port)]
                except (KeyError, ValueError):
                    switches[switch.name][port] = {'type': 'host',
                                                   'host_name': 'no_name'}

        try:
            # Now, update the switches dictionary with the link info from the
            #   SDNTrace.links, which is the Links class.
            for link in Links().links:
                switches[link.switch_a][link.port_a] = {'type': 'link',
                                                        'neighbor_dpid': link.switch_z,
                                                        'neighbor_port': link.port_z}
                switches[link.switch_z][link.port_z] = {'type': 'link',
                                                        'neighbor_dpid': link.switch_a,
                                                        'neighbor_port': link.port_a}
        except KeyError:
            pass

        self._topology = switches

    def get_topology(self):
        """
            Used by REST
            Force a topology sync before sending the reply.
        """
        # TODO: this shouldn't be needed - fix it
        self._update_topology()

        return self._topology
