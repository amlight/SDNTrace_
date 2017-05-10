"""
    Trace Manager Class
"""
import urllib2
import json
from ryu.lib import hub
from libs.tracing.tracer import TracePath
from libs.core.config_reader import ConfigReader
from libs.core.debugging import debugclass


@debugclass
class TraceManager(object):
    """
        The TraceManager class is the app responsible to
        manage all trace requests, intra or inter domain.
    """

    def __init__(self, sdntrace_class):
        """
            Initialization of the TraceManagre class
        Args:
            sdntrace_class: the main SDNTrace class
            config: configuration file with interdomain
                    information
        """
        # Main SDNTrace class
        # TODO: This class is used by the TracePath class.
        #       Sooner to be removed because only the switches are needed
        self.obj = sdntrace_class
        self.config = ConfigReader()
        # Configs
        self._my_domain = None  # my domain name from config
        self._trace_interval = int()  # Interval between traces
        self._neighbors = []   # List of neighbors
        self._borders = dict()  # All my domain's DPID:PORTs
        self._process_config()

        # Traces
        self._id = 80000
        self._active_traces = dict()
        self._request_queue = dict()
        self._results_queue = dict()

        # Thread to start traces
        self.tracing = hub.spawn(self._run_traces)

    def _is_border(self, sw, sw_port):
        """
            Method to identify if the switch and port belong are an inter
            domain connection
        Args:
            sw: dpid
            sw_port: int(port number)
        Returns:
            True: if it is a border interface
            False: if it is not
        """
        if sw in self._borders.keys():
            if str(sw_port) in self._borders[sw].keys():
                return True
        return False

    def _process_config(self):
        """
            Process the configuration file and update all configs
            variables (my_domain, trace_interval, neighbors and borders
        Args:
            config: configuration file
        """
        self._trace_interval = self.config.trace.run_trace_interval
        self._my_domain = self.config.interdomain.my_domain
        self._neighbors = self.config.interdomain.neighbors
        sw_ports = self.config.interdomain.locals
        for port in sw_ports:
            sw, sw_port = port.split(':')
            if sw in self._borders.keys():
                self._borders[sw][sw_port] = {}
            else:
                self._borders[sw] = dict()
                self._borders[sw][sw_port] = {}

    def _run_traces(self):
        """
            Method to become a thread that will keep reading the
            self.request_queue queue looking for new traces to
            start.
        """
        while True:
            if len(self._request_queue) > 0:
                try:
                    r_ids = []
                    for r_id in self._request_queue:
                        hub.spawn(self._spawn_trace(r_id))
                        r_ids.append(r_id)
                    for rid in r_ids:
                        del self._request_queue[rid]
                except Exception as e:
                    print("Trace Error: %s" % e)
            hub.sleep(self._trace_interval)

    def _spawn_trace(self, trace_id):
        """
            Once a request is found by the run_traces method,
            instantiate a TracePath class and runs the tracepath
            Args:
                trace_id: trace request id
            Returns:
                tracer.tracepath
        """
        print("Creating thread to trace request id %s..." % trace_id)
        tracer = TracePath(self, self.obj, trace_id, self._request_queue[trace_id])
        return tracer.tracepath

    def add_inter_result(self, new_entry):
        """
            Process results coming from remote neighbors
        Args:
            new_entry: full result received
        """
        interdomain = new_entry[0]
        other_entries = new_entry[1]

        trace_id = int(new_entry[0]['request_id'])
        trace_results = self.get_result(trace_id)

        new_results = dict()
        new_results['start_time'] = trace_results['start_time']
        new_results['request_id'] = trace_results['request_id']

        tmp_result = []
        for result in trace_results['result']:
            if result['type'] != 'last':
                tmp_result.append(result)
            elif result['type'] == 'last':
                tmp_result.append(interdomain)
                for entry in other_entries['result']:
                    if entry['type'] in ['trace']:
                        tmp_result.append(entry)
                    if entry['type'] in ['starting']:
                        entry['type'] = 'trace'
                        tmp_result.append(entry)
                tmp_result.append(result)

        new_results['result'] = tmp_result

        self.add_result(trace_id, new_results, forward=new_entry)

    def add_result(self, trace_id, result, forward=None):
        """
            Used by the tracer to upload results to the queue
            This method receives the results and, if inter-domain,
            upload the result to the remote server using the
            "service" provided in the configuration file.
        Args:
            trace_id: trace ID
            result: trace result generated using ./libs/core/rest/tracer
        """
        self._results_queue[trace_id] = result

        remote_id, service = self.get_service_from_active_queue(trace_id)
        if service is not 0:
            if forward is not None:
                self.upload_trace_interdomain(trace_id, remote_id, service, forward=forward)
            else:
                self.upload_trace_interdomain(trace_id, remote_id, service)

    def add_to_active_traces(self, trace_id, entries):
        """
            All requested traces are checked first to see if they
                are an intra or an inter domain trace. Then
                self._active_trace is populated with the following
                content
                {'trace_id':{
                    'type': ['intra'|'inter'],
                    'remote_id': if inter, int(remote trace id) or 0,
                    'service': if inter, the remote service URL or 0,
                    'status': 'running'|'complete'|'timeout'
                    }
                }
            Args:
                trace_id: trace ID
                entries: user's trace entries
        """
        active = dict()
        active[trace_id] = {}
        t_entries = entries['trace']
        sw = t_entries['switch']['dpid']
        port = t_entries['switch']['in_port']
        if self._is_border(sw, port):
            try:
                domain = t_entries['data']['inter_path'][-1]
                key = domain.keys()[0]
                rem_id = domain[key]['request_id']
                service = self.get_service_from_config(key)
                trace_type = 'inter'
            except Exception as error:
                print error
                rem_id = 0
                service = 0
                trace_type = 'intra'
            active[trace_id] = {'type': trace_type,
                                'remote_id': rem_id,
                                'service': service,
                                'status': 'running',
                                'timestamp': 0}
        else:
            trace_type = 'intra'
            active[trace_id] = {'type': trace_type,
                                'remote_id': 0,
                                'service': 0,
                                'status': 'running',
                                'timestamp': 0}
        self._active_traces[trace_id] = active[trace_id]

    def entry_validation(self, entries):
        """
            Make sure the switch selected by the user exists.
            In fact, this method has to validate all params inputed.
        Returns:
            True: all set
            False: switch requested doesn't exist

        """
        # TODO: improve with more tests
        dpid = entries['trace']['switch']['dpid']
        init_switch = self.obj.get_switch(dpid, by_name=True)
        if not isinstance(init_switch, bool):
            return True
        return False

    def is_interdomain(self, trace_id):
        """
            Return if trace is an interdomain
            Args:
                trace_id: trace id
            Returns:
                True: if it is
                False: it is is not
        """
        trace_type = self._active_traces[trace_id]['type']
        return True if trace_type is 'inter' else False

    def get_id(self):
        """
            ID generator for all traces
        Returns:
            integer to be the new request/trace id
        """
        self._id += 1
        return self._id

    def get_result(self, trace_id):
        """
            Used by external apps to get a trace result
            using the trace ID
        Returns:
            results
            0 if trace_id not found
        """
        trace_id = int(trace_id)
        try:
            return self._results_queue[trace_id]
        except:
            return 0

    def get_results(self):
        """
            Used by external apps to get all trace results.
        Returns:
            list of results
        """
        return self._results_queue

    def get_service_from_active_queue(self, trace_id):
        """
            If trace_id is an inter, return the remote_id
            and the service
            Args:
                trace_id: trace ID
            Returns:
                remote_id and service
        """
        remote_id = 0
        service = 0
        trace_type = self._active_traces[trace_id]['type']
        if trace_type is 'inter':
            remote_id = self._active_traces[trace_id]['remote_id']
            service = self._active_traces[trace_id]['service']
        return remote_id, service

    def get_service_from_config(self, domain):
        """
            Get the service URL of a specif domain
            Sooner config will become a class and this
            method will be available
            Args:
                domain: neighbor domain
            Returns:
                service url
        """
        return self.config.interdomain.get_service(domain)

    def new_trace(self, entries):
        """
            Receives external requests for traces. Sources
            could be REST (intra) or PacketIn (inter). Validates
            if dpid and ID are from an neighbor using self.neighbors
            and if the entries has a field of 'data' with the remote
            trace/request id.
        Args:
            entries: user's options for trace
        Returns:
            int with the request/trace id
        """
        if not self.entry_validation(entries):
            return 0

        trace_id = self.get_id()
        # Add to active_trace queue:
        self.add_to_active_traces(trace_id, entries)
        # Add to request_queue
        self._request_queue[trace_id] = entries
        return trace_id

    def upload_trace_interdomain(self, local_id, remote_id, service, forward=None):
        """
            If trace is interdomain, upload results to the source
            Args:
                local_id: trace ID of the intra domain
                remote_id: remote trace ID
                service: service URL
        """
        print('Uploading Inter-domain Trace Results...'),
        if forward is None:
            final_result = []
            final_result.append({"type": "intertrace", "domain": self._my_domain,
                                 "request_id": remote_id})
            final_result.append(self.get_result(local_id))
        else:
            final_result = forward

        # Now upload
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(service, data=json.dumps(final_result))
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: 'PUT'
        url = opener.open(request)
        print(' done!')
