
import json
from webob import Response
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
import sdntrace
from libs.core.rest.queries import FormatRest


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
        self.sdntrace_rest = FormatRest(self.sdntrace_app.switches,
                                        self.sdntrace_app.links)
        self.sdntrace_trace = self.sdntrace_app.tracer

    @route('sdntrace', '/sdntrace/switches', methods=['GET'])
    def print_switches(self, req, **kwargs):
        return self._switches(req, **kwargs)

    @route('sdntrace', '/sdntrace/switches/{dpid}/info', methods=['GET'])
    def print_switch_info(self, req, **kwargs):
        return self._switch_info(req, **kwargs)

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

    @route('sdntrace', '/sdntrace/switches/{dpid}/flows', methods=['GET'])
    def print_trace_id(self, req, **kwargs):
        return self._listflows(req, **kwargs)

    @route('sdntrace', '/sdntrace/trace', methods=['PUT'])
    def run_trace(self, req, **kwargs):
        return self._trace(req, **kwargs)

    @route('sdntrace', '/sdntrace/trace/{trace_id}', methods=['GET'])
    def get_trace(self, req, **kwargs):
        return self._get_trace(req, **kwargs)

    @route('sdntrace', '/sdntrace/trace/inter', methods=['PUT'])
    def put_trace_inter(self, req, **kwargs):
        return self._put_trace_inter(req, **kwargs)

    def _switches(self, req, **kwargs):
        sws = [switch.name for _, switch in self.sdntrace_app.switches.items()]
        body = json.dumps(sws)
        return Response(content_type='application/json', body=body)

    def _switch_info(self, req, **kwargs):
        dpid = kwargs['dpid']
        body = self.sdntrace_rest.switch_info(dpid)
        return Response(content_type='application/json', body=body)

    def _switch_ports(self, req, **kwargs):
        dpid = kwargs['dpid']
        body = self.sdntrace_rest.switch_ports(dpid)
        return Response(content_type='application/json', body=body)

    def _switch_neighbors(self, req, **kwargs):
        dpid = kwargs['dpid']
        for _, switch in self.sdntrace_app.switches.items():
            if switch.name == dpid:
                neighbors = [neighbor.name for neighbor in switch.adjacencies_list]
        body = json.dumps(neighbors)
        return Response(content_type='application/json', body=body)

    def _topology(self, req, **kwargs):
        body = self.sdntrace_rest.get_topology()
        return Response(content_type='application/json', body=body)

    def _colors(self, req, **kwargs):
        colors = {}
        for _, switch in self.sdntrace_app.switches.items():
            colors[switch.name] = {'color': switch.color, 'old_color': switch.old_color}
        body = json.dumps(colors)
        return Response(content_type='application/json', body=body)

    def _get_trace(self, req, **kwargs):
        trace_id = kwargs['trace_id']
        trace_id = trace_id.encode('ascii')
        result = self.sdntrace_trace.get_result(trace_id)
        if result == 0:
            msg = "Error: Trace ID not found: %s" % trace_id
            error = {'result': {'error': msg}}
            body = json.dumps(error)
        else:
            body = json.dumps(result)
        return Response(content_type='application/json', body=body)

    def _trace(self, req, **kwargs):
        """
            Trace method.
        """
        nodes_app = self.sdntrace_app
        try:
            new_entry = eval(req.body)

            if not nodes_app.print_ready:
                body = json.dumps("SDNTrace: System Not Ready Yet!")
                return Response(content_type='application/json', body=body)

            request_id = self.sdntrace_trace.new_trace(new_entry)
            if request_id == 0:
                body = json.dumps({'error': 'invalid entry provided'})
            else:
                body = json.dumps({'request_id': request_id})
            return Response(content_type='application/json', body=body)

        except Exception as e:
            print('SDNTraceRest Error: %s' % e)
            body = json.dumps({'error': '%s' % str(e)})
            return Response(content_type='application/json', body=body, status=500)

    def _put_trace_inter(self, req, **kwargs):
        """
            This method was created for the neighbor domains to upload the trace
            results. Once result is received and validated, it is added to the
            self.sdntrace_app.trace_results_queue after type=interdomain
            Args:
                req: dictionary in the REST format
                **kwargs:
        """
        print("Inter-domain SDNTrace updates")
        try:
            new_entry = eval(req.body)

        except Exception as e:
            print('SDNTraceRest Error: %s' % e)
            body = json.dumps({'error': "malformed request %s" % e})
            return Response(content_type='application/json', body=body, status=500)

        self.sdntrace_trace.add_inter_result(new_entry)
