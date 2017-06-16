"""

"""
import json
from libs.openflow.of10.openflow_helper import process_actions
from libs.openflow.of10.openflow_helper import process_match
from libs.topology.switches import Switches
from apps.topo_discovery.topo_discovery import TopologyDiscovery


class FormatRest(object):

    @staticmethod
    def list_switches():
        switches = [switch.name for switch in Switches().get_switches()]
        return json.dumps(switches)

    @staticmethod
    def list_colors():
        colors = {}
        for switch in Switches().get_switches():
            colors[switch.name] = {'color': switch.color, 'old_color': switch.old_color}
        return json.dumps(colors)

    @staticmethod
    def switch_info(dpid):
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
                "number_flows": integer,
                "distance": integer
            }
            or
            {} if not found
        """
        info = dict()  # in case user requests before switch appears
        for switch in Switches().get_switches():
            if switch.name == dpid:
                info = {
                        'switch_name': switch.switch_name,
                        'switch_vendor': switch.switch_vendor,
                        'datapath_id': switch.datapath_id,
                        'switch_color': switch.color,
                        'openflow_version': switch.version_name,
                        'ip_address': switch.addr[0],
                        'tcp_port': switch.addr[1],
                        'number_flows': len(switch.flows),
                        'distance': switch.distance
                        }
                break
        return json.dumps(info)

    @staticmethod
    def switch_ports(dpid):
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
        for switch in Switches().get_switches():
            if switch.name == dpid:
                ports = switch.ports
                body = json.dumps(ports)
                break
        return body

    @staticmethod
    def switch_neighbors(dpid):
        neighbors = list()
        for switch in Switches().get_switches():
            if switch.name == dpid:
                neighbors = [neighbor.name for neighbor in switch.adjacencies_list]
        return json.dumps(neighbors)

    @staticmethod
    def get_topology():
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
        topology = TopologyDiscovery().get_topology()
        # Return switches in the json format
        return json.dumps(topology)

    @staticmethod
    def list_flows(dpid):
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
        for switch in Switches().get_switches():
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
