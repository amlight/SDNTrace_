from datetime import datetime


class FormatRest:

    def __init__(self, sdntrace_class):
        self.obj = sdntrace_class
        self.start_time = self.current_time()

    def current_time(self):
        return datetime.now()

    def get_time(self, to_str=True):
        time_diff = self.current_time() - self.start_time
        return str(time_diff) if to_str else time_diff

    def add_trace_step(self, trace_result, trace_type, reason='done',
                       dpid=None, port=None, msg="none"):
        """
            Used to define the new REST interface.
                Use docs/trace_results.txt  for examples.
                Only this method should write to self.trace_result
            Args:
                trace_result: variable with results
                trace_type: type of trace
                reason: reason in case trace_type == last
                dpid: switch's dpid
                port: switch's OpenFlow port_no
                msg: message in case of reason == error
        """
        step = dict()
        step["type"] = trace_type
        # Get port name instead of port_no
        if dpid:
            new_switch = self.obj.get_switch(dpid, by_name=True)
            try:
                port_name = new_switch.ports[port]["name"]
            except:
                raise Exception('Restart Mininet: port Disappeared ')

        if trace_type == 'starting':
            step["dpid"] = new_switch.name
            step["port"] = port_name
            step["time"] = str(self.start_time)
        elif trace_type == 'trace':
            step["dpid"] = new_switch.name
            step["port"] = port_name
            step["time"] = self.get_time()
        elif trace_type == 'last':
            step["reason"] = reason
            step["msg"] = msg
            step["time"] = self.get_time()
        elif trace_type == 'intertrace':
            pass
        # Add to trace_result array
        trace_result.append(step)
