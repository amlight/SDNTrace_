import json


class FormatRest:

    def __init__(self, switches):
        self.switches = switches

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