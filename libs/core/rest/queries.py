import json
from libs.core.config_reader import ConfigReader
from libs.core.rest.openflow_helper import process_actions
from libs.core.rest.openflow_helper import process_match


class FormatRest:

    def __init__(self, switches, links=None):
        self.switches = switches
        self.links = links
        self.config = ConfigReader()

    def switch_info(self, dpid):
        """
            /sdntrace/switches/00004af7b0f68749/info
            {
                "datapath_id": "00004af7b0f68749",
                "switch_color": "char",
                "tcp_port": integer,
                "openflow_version": "string",
                "switch_vendor": "string",
                "ip_address": "ip_address",
                "switch_name": "string",
                "number_flows": integer
            }
            or
            {} if not found
        """
        body = dict()  # in case user requests before switch appears
        for _, switch in self.switches.items():
            if switch.name == dpid:
                info = {
                        'switch_name': switch.switch_name,
                        'switch_vendor': switch.switch_vendor,
                        'datapath_id': switch.datapath_id,
                        'switch_color': switch.color,
                        'openflow_version': switch.version_name,
                        'ip_address': switch.addr[0],
                        'tcp_port': switch.addr[1],
                        'number_flows': 0
                        }
                body = json.dumps(info)
                break
        return body

    def switch_ports(self, dpid):
        """
            {
            "1": {
                    "speed": "10GB_FD",
                    "name": "s1-eth1",
                    "port_no": 1,
                    "status": "down|up"
                },
            "2": {
                    "speed": "10GB_FD",
                    "name": "s1-eth2",
                    "port_no": 2,
                    "status": "down|up"
                }
            }
        """
        body = dict()
        for _, switch in self.switches.items():
            if switch.name == dpid:
                ports = switch.ports
                body = json.dumps(ports)
                break
        return body

    def get_topology(self):
        """
            This method is used by SDNTraceREST to post the network
            topology using the following format:

            Request:
            /sdntrace/switches/topology

            Returns:
            {
                "dpid_a": { "port_no1": { "type": "link",
                                          "neighbor_dpid": "dpid_b",
                                          "neighbor_port": port_no
                                        },
                            "port_no2": { "type": "interdomain",
                                          "neighbor_name": "ANSP"
                                        },
                            "port_no3": { "type": "host",
                                          "host_name": "perfSonar"
                                        }
                            },
                "dpid_b": ...
            }
        """
        # Collect all inter-domain info from the configuration file
        inter_conf = self.config.interdomain.locals
        inter_names = self.config.interdomain.neighbors

        # Create a temporary dictionary with all inter-domain ports adding
        #  the remote domain's name to it
        inter = dict()
        for node in inter_conf:
            sw_dpid, sw_port = node.split(':')
            inter[sw_dpid] = {}
            for neighbor in inter_names:
                local = self.config.interdomain.get_local_sw(neighbor)
                if local == sw_dpid:
                    inter[sw_dpid][sw_port] = {'type':'interdomain',
                                               'domain_name': neighbor}

        # Create the final dictionary with all switches and ports
        #   Uses the inter dict to add inter-domain info. If no inter-domain
        #   is found, assume it is a host port - for now.
        switches = dict()
        for _, switch in self.switches.items():
            switches[switch.name] = {}
            for port in switch.ports:
                try:
                    switches[switch.name][port] = inter[switch.name][str(port)]
                except:
                    switches[switch.name][port] = {'type': 'host',
                                                   'host_name': 'no_name'}

        # Now, update the switches dictionary with the link info from the
        #   SDNTrace.links, which is the Links class.
        for link in self.links.links:
            switches[link.switch_a][link.port_a] = { 'type': 'link',
                                                     'neighbor_dpid': link.switch_z,
                                                     'neighbor_port': link.port_z}
            switches[link.switch_z][link.port_z] = { 'type': 'link',
                                                     'neighbor_dpid': link.switch_a,
                                                     'neighbor_port': link.port_a}

        # Return switches in the json format
        return json.dumps(switches)

    def list_flows(self, dpid):
        """
            /sdntrace/switches/{dpid}/flows
           {
                "dpid": "0000000000000001",
                "number_flows": 5,
                "flows": [
                    {
                        "actions": [
                            {
                                "max_len": 65509,
                                "type": "OFPActionOutput(0)",
                                "port": 65533
                            }
                            ...
                        ],
                        "idle_timeout": 0,
                        "cookie": 2000002,
                        "priority": 50001,
                        "hard_timeout": 0,
                        "byte_count": 0,
                        "duration_nsec": 71000000,
                        "packet_count": 0,
                        "duration_sec": 4,
                        "table_id": 0,
                        "match": {
                            "wildcards": 3678458,
                            "dl_src": "ee:ee:ee:11:11:11",
                            "in_port": 1
                            ...
                        }
                    }
                    ...
                ]
            }
            or
            {} if not found
        """
        body = dict()  # in case user requests before switch appears
        flows = list()
        for _, switch in self.switches.items():
            if switch.name == dpid:
                for flow in sorted(sorted(switch.flows, key=lambda f: f.duration_sec, reverse=True),
                                   key=lambda f: f.priority, reverse=True):
                    match = process_match(flow.match)
                    actions = process_actions(flow.actions)
                    flow_stats = {
                        "byte_count": flow.byte_count,
                        "cookie": flow.cookie,
                        "duration_nsec": flow.duration_nsec,
                        "duration_sec": flow.duration_sec,
                        "hard_timeout": flow.hard_timeout,
                        "idle_timeout": flow.idle_timeout,
                        "packet_count": flow.packet_count,
                        "priority": flow.priority,
                        "table_id": flow.table_id,
                        "match": match,
                        "actions": actions
                    }
                    flows.append(flow_stats)

                # Finished loop, process output
                final = {
                    "dpid": dpid,
                    "number_flows": len(flows),
                    "flows": flows
                }
                body = json.dumps(final)
                break
        return body

