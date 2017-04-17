"""
    This is the core of the SDNTrace
    Here all OpenFlow events are received and handled
"""
from ryu import cfg
from ryu import utils
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import DEAD_DISPATCHER
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.ofproto import ofproto_v1_0, ofproto_v1_3
from ryu.topology import event

from libs.coloring.auxiliary import prepare_lldp_packet, define_colors
from libs.core.read_config import read_config
from libs.openflow.new_switch import new_switch
from libs.tracing import tracing
from libs.tracing.trace_pkt import generate_entries_from_packet_in
from libs.coloring.links import Links
from libs.tracing.trace_manager import TraceManager


# Used to get the configuration file
# entry trace_config in the config file provided
# by the user
CONF = cfg.CONF
CONF.register_opts([cfg.StrOpt('trace_config')])


class SDNTrace(app_manager.RyuApp):

    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION, ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SDNTrace, self).__init__(*args, **kwargs)
        self.sw_addrs = dict()  # Dict for switches' IP addresses
        self.switches = dict()  # Dict for OFSwitch1* classes
        self.links = Links()     # List of links detected
        self.colors = []        # List of current colors in use
        self.old_colors = []    # List of old colors used
        # Threads
        self.topo_disc = hub.spawn(self._topology_discovery)
        self.push_colors = hub.spawn(self._push_colors)
        self.flows = hub.spawn(self.get_all_flows)
        self.trace_pktIn = []  # list of received PacketIn non LLDP
        # Other variables
        self.config_vars = read_config(CONF.trace_config)  # Read configuration
        self.print_ready = False  # Just to print System Ready once

        # Trace_Manager
        self.tracer = TraceManager(self, self.config_vars)

    # Auxiliary Threads
    def _topology_discovery(self):
        """
            Keeps looping self.switches every PACKET_OUT_INTERVAL seconds
            Send a packet_out w/ LLDP to every port found
            Args:
                self
        """
        vlan = self.config_vars['topo_discovery']['vlan_discovery']
        while True:
            # Only send PacketOut + LLDP when more than one switch exists
            if len(self.switches) > 1:
                for _, switch in self.switches.items():
                    for port in switch.ports:
                        pkt = prepare_lldp_packet(switch, port, vlan)
                        switch.send_packet_out(port, pkt.data, lldp=True)
            hub.sleep(self.config_vars['topo_discovery']['packet_out_interval'])

    def _push_colors(self):
        """
            This routine will run every PUSH_COLORS_INTERVAL interval
            and process the self.links to associate colors to OFSwitches.
            Flows will be pushed to switches with the dl_src field set
            to the defined color outputting to controller
            Args:
                self
        """
        while True:
            if len(self.switches) > 1:
                if len(self.links) is not 0:
                    self.install_colored_flows()
            hub.sleep(self.config_vars['trace']['push_color_interval'])

    def get_all_flows(self):
        """
            Keep asking for flow entries of each switch

        """
        while True:
            for s in self.switches.values():
                s.get_flows()
            hub.sleep(self.config_vars['statistics']['flowstats_interval'])

    # Main thread
    def add_switch(self, ev):
        """
            Add the new switch to the self.switches dict
            Args:
                ev: FeatureReply
        """
        self.switches[ev.msg.datapath_id] = new_switch(ev, self.config_vars)

    def del_switch(self, ev):
        """
            In case of DEAD_DISPATCH, remove the switch from
            the self.switches dict
            Args:
                ev: DEAD_DISPATCH event
        """
        switch = self.get_switch(ev.datapath)
        if switch is not False:
            self.links.remove_switch(switch.name)
            switch.print_removed()
            self.switches.pop(switch.dpid)

    def get_switch(self, datapath, by_name=False):
        """
            Query the self.switches
            Args:
                datapath: datapath object <'str'> 16 digits
                by_name: if search is by datapath id

            Returns:
                OFSwitch10 or OFSwitch13 objects
                False if not found
        """
        for _, switch in self.switches.items():
            if by_name:
                if switch.name == datapath:
                    return switch
            else:
                if switch.obj.msg.datapath == datapath:
                    return switch
        return False

    def update_switch_address(self, switch_dp):
        """"
            Add tuple (IP, Port) to the OFSwitch class
        """
        dpid = '%016x' % switch_dp.id
        sw = self.get_switch(dpid, True)
        sw.update_addr(switch_dp.address)

    # Event Listeners
    @set_ev_cls(event.EventSwitchEnter)
    def get_topology_data(self, ev):
        """
            Get switches' IPs and ports. This method is
            detected after EventOFPSwitchFeatures, so we just
            update the switch address.
        Args:
            ev: EventSwitchEnter
        """
        self.update_switch_address(ev.switch.dp)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """
            FeatureReply - For each new switch that connects, add to the
            switches dictionary. This dict will be used for sending packetOut
            and generate topology and colors.
            When instantiating a switch, clears old colored flows
            and adds the default LLDP flow
            Args:
                ev: FeatureReply received
        """
        self.add_switch(ev)

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status(self, ev):
        """
            Process OFP_Port_Status
            Add or Remove ports from OFSwitch.ports
            Args:
                ev: PortStatus received
        """
        switch = self.get_switch(ev.msg.datapath)
        switch.port_status(ev)

    @set_ev_cls(ofp_event.EventOFPStateChange, DEAD_DISPATCHER)
    def remove_switch(self, ev):
        """
            If DEAD_DISPATCHER received, remove switch from self.switches
            Args:
                ev: packet captured
        """
        self.del_switch(ev)

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_stats_reply_handler(self, ev):
        """
            Multipart Port Stats Description
            Only used for OF1.3
            Args:
                ev: FeatureReply received
        """
        switch = self.get_switch(ev.msg.datapath)
        switch.process_port_desc_stats_reply(ev)

    @set_ev_cls(ofp_event.EventOFPDescStatsReply, MAIN_DISPATCHER)
    def description_stats_reply_handler(self, ev):
        """
            Multipart Description Stats Description
            Only used for OF1.3
            Args:
                ev: FeatureReply received
        """
        switch = self.get_switch(ev.msg.datapath)
        switch.process_description_stats_reply(ev)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """
            Process PacketIn
            PacketIN messages are used for topology discovery and traces
            Args:
                ev: PacketIn message
        """
        switch = self.get_switch('%016x' % ev.msg.datapath.id, by_name=True)
        action, result, in_port = switch.process_packetIn(ev, self.links)

        if action is 1:  # LLDP
            self.links.add_link(result)
            self.create_adjacencies(self.links)
        elif action is 2:  # Probe packets
            trace_type, pkt = tracing.process_probe_packet(ev, result, in_port,
                                                           self.config_vars,
                                                           switch)
            if trace_type is 'Intra' and pkt is not False:
                # This list is store all PacketIn message received
                self.trace_pktIn.append(pkt)
            elif trace_type is 'Inter':
                print('Inter-domain probe received')
                # Convert pkt.data to entries
                new_entries = generate_entries_from_packet_in(ev,
                                                              switch.datapath_id,
                                                              in_port)
                # add new_entries to the trace_request_queue
                #r_id = self.get_request_id()
                #self.trace_request_queue[r_id] = new_entries
                self.tracer.new_trace(new_entries)

    @set_ev_cls(ofp_event.EventOFPErrorMsg, MAIN_DISPATCHER)
    def openflow_error(self, ev):
        """
            Print Error Received. Useful for troubleshooting
            Args:
                ev: event
        """
        msg = ev.msg
        print('OFPErrorMsg received: type=0x%02x code=0x%02x message=%s' %
              (msg.type, msg.code, utils.hex_array(msg.data)))

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def handle_flow_stats(self, ev):
        """
            Process OFPFlowStatsReply saving all the flows
            associated with a switch. These flows will be used for
            the inter-domain trace
            Args:
                ev: EventOFPFlowStatsReply message
        """
        flows = ev.msg.body

        switch = self.get_switch(ev.msg.datapath)
        switch.flows = sorted(flows, key=lambda f: f.priority, reverse=True)

    # Other methods
    def create_adjacencies(self, links):
        """
            Everytime self.links is updated, update all
            adjacencies between switches
            Args:
                links: self.links
        """
        for _, switch in self.switches.items():
            switch.create_adjacencies(self, links)

    def install_colored_flows(self):
        """
            First define colors for each node
            Delete old flows
            Then push new flows
        """
        colors = define_colors(self.switches)
        # Compare received colors with self.old_colors
        # If the same, ignore
        if colors is not None:
            self.colors = colors
            if len(self.old_colors) is 0:
                self.old_colors = self.colors
            else:
                if self.colors == self.old_colors:
                    if not self.print_ready:
                        self.print_ready = True
                        print('SDNTrace Ready!')
                    return

        # Check all colors in use
        # For each switch:
        # 1 - Delete colored flows
        # 2 - For each switch, check colors of neighbors
        # 3 - Install all neighbors' colors
        for _, switch in self.switches.items():
            # 1 - Delete old colored flows
            switch.delete_colored_flows()
            # 2 - Check colors of all other switches
            neighbor_colors = []
            for color in self.colors:
                # Get Dict Key. Just one Key
                for key in color:
                    if key != switch.name:
                        neighbor = self.get_switch(key, by_name=True)
                        if neighbor in switch.adjacencies_list:
                            neighbor_colors.append(color[key])
            # 3 - Install all colors from other switches
            # in some cases, if two neighbors have the same color, the same flow
            # will be installed twice. It is not an issue.
            for color in neighbor_colors:
                switch.install_color(color)
            del neighbor_colors
            switch.old_color = switch.color
        self.old_colors = self.colors
