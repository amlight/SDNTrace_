
import json
from webob import Response
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from ryu.lib import hub
import sdntrace


sdntrace_instance_name = 'sdntrace_api_app'
request_id = 80000


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
    def print_topology(self, req, **kwargs):
        return self._topology(req, **kwargs)

    @route('sdntrace', '/sdntrace/switches/colors', methods=['GET'])
    def print_colors(self, req, **kwargs):
        return self._colors(req, **kwargs)

    @route('sdntrace', '/sdntrace/switches/traceid/{tid}', methods=['GET'])
    def print_trace_id(self, req, **kwargs):
        return self._traceid(req, **kwargs)

    @route('sdntrace', '/sdntrace/trace', methods=['PUT'])
    def run_trace(self, req, **kwargs):
        return self._trace(req, **kwargs)

    @route('sdntrace', '/sdntrace/trace', methods=['OPTIONS'])
    def run_trace_options(self, req, **kwargs):
        """
        Receive OPTIONS in case of cross-site ajax calls.
        Returning the correct CORS headers allowing the cross-site request using PUT.
        """
        #Access - Control - Request - Method
        response = Response(content_type='application/json', body='')
        response = self._add_CORS_hearder(response)
        return response

    @route('sdntrace', '/sdntrace/sdntrace.html', methods=['GET'])
    def run_load_content(self, req, **kwargs):
        return self._load_content(req, "./web/html/sdntrace.html", **kwargs)
    @route('sdntrace', '/sdntrace/ajax-loader.gif', methods=['GET'])
    def run_load_image(self, req, **kwargs):
        return self._load_image(req, "./web/html/ajax-loader.gif", **kwargs)


    def _add_CORS_hearder(self, response):
        # CORS headers
        response.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS, PUT',
            'Access-Control-Max-Age': '86400'
        })
        return response

    def _switches(self, req, **kwargs):
        sws = [node.name for node in self.sdntrace_app.node_list]
        body = json.dumps(sws)
        response = Response(content_type='application/json', body=body)
        response = self._add_CORS_hearder(response)
        return response

    def _switch_ports(self, req, **kwargs):
        dpid = kwargs['dpid']
        body = "0"  # in case user requests before switch appears
        for node in self.sdntrace_app.node_list:
            if node.name == dpid:
                ports = node.ports
                body = json.dumps(ports)
        response = Response(content_type='application/json', body=body)
        response = self._add_CORS_hearder(response)
        return response

    def _switch_neighbors(self, req, **kwargs):
        dpid = kwargs['dpid']
        for node in self.sdntrace_app.node_list:
            if node.name == dpid:
                neighbors = [node.name for node in node.adjacencies_list]
        body = json.dumps(neighbors)
        response = Response(content_type='application/json', body=body)
        response = self._add_CORS_hearder(response)
        return response

    def _topology(self, req, **kwargs):
        topology = {}
        for node in self.sdntrace_app.node_list:
            neighbors = []
            for neigh in node.adjacencies_list:
                neighbors.append(neigh.name)
            topology[node.name] = neighbors
        body = json.dumps(topology)
        response = Response(content_type='application/json', body=body)
        response = self._add_CORS_hearder(response)
        return response

    def _colors(self, req, **kwargs):
        colors = {}
        for node in self.sdntrace_app.node_list:
            colors[node.name] = {'color': node.color, 'old_color': node.old_color}
        body = json.dumps(colors)
        response = Response(content_type='application/json', body=body)
        response = self._add_CORS_hearder(response)
        return response

    def _traceid(self, req, **kwargs):
        traceid = ""
        body = json.dumps(traceid)
        response = Response(content_type='application/json', body=body)
        response = self._add_CORS_hearder(response)
        return response

    def _trace(self, req, **kwargs):
        """
            Trace method.
        """
        nodes_app = self.sdntrace_app
        new_entry = eval(req.body)
        global request_id
        # First, generate an ID to be send back to user
        # This ID will be used as the data in the packet
        request_id += 1
        result_json = {'request_id': request_id}
        body = json.dumps(result_json)

        # Process trace
        # Find a way to create a thread
        print 'request_id: %s' % body
        trace = nodes_app.process_trace_req(new_entry, request_id)
        body = json.dumps(trace)
        response = Response(content_type='application/json', body=body)
        response = self._add_CORS_hearder(response)
        return response

    def _load_content(self, req, html_path, **kwargs):
        """
        Load web content (html).
        """
        res = Response(content_type="text/html")
        res.body = open(html_path, 'rb').read()

        return res

    def _load_image(self, req, image_path, **kwargs):
        """
        Load web image.
        """
        res = Response(content_type="image/gif")
        res.body = open(image_path, 'rb').read()

        return res