import json
import sdntrace
from webob import Response
from ryu.app.wsgi import ControllerBase, WSGIApplication, route


sdntrace_instance_name = 'sdntrace_api_app'


class SDNTraceRest(sdntrace.SDNTrace):

    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(SDNTraceRest, self).__init__(*args, **kwargs)
        wsgi = kwargs['wsgi']
        wsgi.register(SDNTraceController, {sdntrace_instance_name: self})


class SDNTraceController(ControllerBase):

    def __init__(self, req, link, data, **config):
        super(SDNTraceController, self).__init__(req, link, data, **config)
        self.sdntrace_app = data[sdntrace_instance_name]

    @route('sdntrace', '/sdntrace/switches', methods=['GET'])
    def print_switches(self, req, **kwargs):
        return self._switches(req, **kwargs)

    @route('sdntrace', '/sdntrace/switches/{dpid}/ports', methods=['GET'])
    def print_switch_ports(self, req, **kwargs):
        return self._switch_ports(req, **kwargs)

    @route('sdntrace', '/sdntrace/switches/{dpid}/neighbors', methods=['GET'])
    def print_switch_neighbors(self, req, **kwargs):
        return self._switch_neighbors(req, **kwargs)

    @route('sdntrace', '/sdntrace/switches/topology', methods=['GET'])
    def print_switch_neighbors(self, req, **kwargs):
        return self._topology(req, **kwargs)

    @route('sdntrace', '/sdntrace/switches/traceid/{tid}', methods=['GET'])
    def print_switch_neighbors(self, req, **kwargs):
        return self._traceid(req, **kwargs)

    @route('sdntrace', '/sdntrace/trace', methods=['PUT'])
    def run_trace(self, req, **kwargs):
        return self._trace(req, **kwargs)

    def _switches(self, req, **kwargs):
        sws = [node.name for node in self.sdntrace_app.node_list]
        body = json.dumps(sws)
        return Response(content_type='application/json', body=body)

    def _switch_ports(self, req, **kwargs):
        dpid = kwargs['dpid']
        for node in self.sdntrace_app.node_list:
            if node.name == dpid:
                ports = node.ports
        body = json.dumps(ports)
        return Response(content_type='application/json', body=body)

    def _switch_neighbors(self, req, **kwargs):
        dpid = kwargs['dpid']
        for node in self.sdntrace_app.node_list:
            if node.name == dpid:
                neighbors = [node.name for node in node.adjenceciesList]
        body = json.dumps(neighbors)
        return Response(content_type='application/json', body=body)

    def _topology(self, req, **kwargs):
        topology = ""
        body = json.dumps(topology)
        return Response(content_type='application/json', body=body)

    def _traceid(self, req, **kwargs):
        traceid = ""
        body = json.dumps(traceid)
        return Response(content_type='application/json', body=body)

    def _trace(self, req, **kwargs):
        nodes_app = self.sdntrace_app
        new_entry = eval(req.body)
        # Process trace
        result = nodes_app.process_trace_req(new_entry)
        print result
        result_json = {'dpid': result[0], 'in_port': result[1]}
        body = json.dumps(result_json)
        return Response(content_type='application/json', body=body)
