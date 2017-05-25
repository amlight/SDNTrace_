var DEBUG = false;
// Mock json switch list structures. Used for testing purposes.
var MOCK_JSON_SWITCHES = '[' +
    '{"capabilities": "", "dpid": "0000000000000001", "n_ports": 8, "n_tables": 5},' +
    '{"capabilities": "", "dpid": "0000000000000002", "n_ports": 16, "n_tables": 5},' +
    '{"capabilities": "", "dpid": "0000000000000003", "n_ports": 23, "n_tables": 5},' +
    '{"capabilities": "", "dpid": "0000000000000004", "n_ports": 8, "n_tables": 5},' +
    '{"capabilities": "", "dpid": "0000000000000005", "n_ports": 8, "n_tables": 5},' +
    '{"capabilities": "", "dpid": "0000000000000006", "n_ports": 16, "n_tables": 5},' +
    '{"capabilities": "", "dpid": "0000000000000007", "n_ports": 8, "n_tables": 5}' +
    ']';

var MOCK_JSON_SDNTRACE_SWITCHES = '[' +
    '"0000000000000001", "0000000000000002", "0000000000000003", "0000000000000004", "0000000000000005", "0000000000000006"' +
    ']';


var MOCK_JSON_SDNTRACE_SWITCH_INFO =
    '{"switch_color": "1", "datapath_id": "0000000000000001", "openflow_version": "1.0", "number_flows": 0, "switch_vendor": "Nicira, Inc.", "tcp_port": 52320, "ip_address": "190.103.187.56", "switch_name": "s1"}';

// Mock json topology structure. Used for testing purposes.
var MOCK_JSON_TOPOLOGY = '[' +
    '{   "node1": { "dpid": "0000000000000001", "port": { "name": "10Gigabit3", "port_no": 3 } },' +
    '    "node2": { "dpid": "0000000000000002", "port": { "name": "10Gigabit6", "port_no": 6 } },' +
    '    "speed": 10000000000 },' +
    '{   "node1": { "dpid": "0000000000000001", "port": { "name": "10Gigabit5", "port_no": 5 } },' +
    '    "node2": { "dpid": "0000000000000006", "port": { "name": "Gigabit3", "port_no": 3 } },' +
    '    "speed": 1000000000 },' +
    '{   "node1": { "dpid": "0000000000000001", "port": { "name": "10Gigabit8", "port_no": 8 } },' +
    '    "node2": { "dpid": "0000000000000007", "port": { "name": "100Gigabit6", "port_no": 6 } },' +
    '    "speed": 10000000000 },' +
    '{   "node1": { "dpid": "0000000000000002", "port": { "name": "10Gigabit3", "port_no": 3 } },' +
    '    "node2": { "dpid": "0000000000000003", "port": { "name": "10Gigabit4", "port_no": 4 } },' +
    '    "speed": 1000000000 },' +
    '{   "node1": { "dpid": "0000000000000003", "port": { "name": "Gigabit22", "port_no": 22 } },' +
    '    "node2": { "dpid": "0000000000000004", "port": { "name": "Gigabit6", "port_no": 6 } },' +
    '    "speed": 1000000000 },' +
    '{   "node1": { "dpid": "0000000000000003", "port": { "name": "10Gigabit3", "port_no": 3 } },' +
    '    "node2": { "dpid": "0000000000000007", "port": { "name": "100Gigabit4", "port_no": 4 } },' +
    '    "speed": 10000000000 },' +
    '{   "node1": { "dpid": "0000000000000004", "port": { "name": "Gigabit8", "port_no": 8 } },' +
    '    "node2": { "dpid": "0000000000000005", "port": { "name": "Gigabit6", "port_no": 6 } },' +
    '    "speed": 1000000000 },' +
    '{   "node1": { "dpid": "0000000000000005", "port": { "name": "Gigabit3", "port_no": 3 } },' +
    '    "node2": { "dpid": "0000000000000006", "port": { "name": "Gigabit6", "port_no": 6 } },' +
    '    "speed": 1000000000 },' +
    '{   "node1": { "dpid": "0000000000000005", "port": { "name": "Gigabit7", "port_no": 7 } },' +
    '    "node2": { "dpid": "0000000000000007", "port": { "name": "100Gigabit2", "port_no": 2 } },' +
    '    "speed": 1000000000 }' +
    ']';

//var MOCK_JSON_TOPOLOGY_TRACE = '{' +
//    '"0000000000000001": ["0000000000000002"], ' +
//    '"0000000000000002": ["0000000000000001", "0000000000000003"], ' +
//    '"0000000000000003": ["0000000000000004", "0000000000000002"], ' +
//    '"0000000000000004": ["0000000000000005", "0000000000000003"], ' +
//    '"0000000000000005": ["0000000000000006", "0000000000000004"], ' +
//    '"0000000000000006": ["0000000000000005"]' +
//    '}';

var MOCK_JSON_TOPOLOGY_TRACE = '{' +
    '"0000000000000001": {' +
//        '"2": {"type": "link", "neighbor_port": 1, "neighbor_dpid": "0000000000000002"}' +
        '"2": {"type": "link", "neighbor_port": 1, "neighbor_dpid": "0000000000000002"},' +
        '"3": {"type": "host", "neighbor_name": "HOST1"},' +
        '"4": {"type": "host", "neighbor_name": "HOST2"}' +
    '}},' +
    '{"0000000000000002": {' +
        '"2": {"type": "link", "neighbor_port": 1, "neighbor_dpid": "0000000000000003"}' +
    '}},' +
    '{"0000000000000003": {' +
        '"2": {"type": "link", "neighbor_port": 1, "neighbor_dpid": "0000000000000004"}' +
    '}},' +
    '{"0000000000000004": {' +
        '"2": {"type": "link", "neighbor_port": 1, "neighbor_dpid": "0000000000000005"}' +
    '}},' +
    '{"0000000000000005": {' +
        '"2": {"type": "link", "neighbor_port": 1, "neighbor_dpid": "0000000000000006"}' +
    '}}';




// Mock json port list
var MOCK_JSON_SWITCH_PORTS = '[' +
    '{ "name": "10Gigabit1", "port_no": 1, "speed": 10000000000, "uptime": 726558 },' +
    '{ "name": "10Gigabit2", "port_no": 2, "speed": 10000000000, "uptime": 614493 },' +
    '{ "name": "10Gigabit3", "port_no": 3, "speed": 10000000000, "uptime": 464014 },' +
    '{ "name": "10Gigabit4", "port_no": 4, "speed": 10000000000, "uptime": 997827 },' +
    '{ "name": "10Gigabit5", "port_no": 5, "speed": 10000000000, "uptime": 632296 },' +
    '{ "name": "10Gigabit6", "port_no": 6, "speed": 10000000000, "uptime": 482803 },' +
    '{ "name": "10Gigabit7", "port_no": 7, "speed": 10000000000, "uptime": 1007698},' +
    '{ "name": "10Gigabit8", "port_no": 8, "speed": 10000000000, "uptime": 418707 }' +
    ']';


var MOCK_JSON_SDNTRACE_SWITCH_PORTS = '{' +
    '"1": {"speed": "10GB_FD", "name": "s1-eth1", "port_no": 1, "status": "up" },' +
    '"2": {"speed": "10GB_FD", "name": "s1-eth2", "port_no": 2, "status": "up" },' +
    '"3": {"speed": "10GB_FD", "name": "s1-eth3", "port_no": 3, "status": "up"},' +
    '"4": {"speed": "10GB_FD", "name": "s1-eth4", "port_no": 4, "status": "up"}' +
    '}';


var MOCK_JSON_FLOWS = '{"number_flows": 4, "flows": [{"actions": [{"max_len": 65509, "type": "OFPActionOutput(0)", "port": 65533}], "idle_timeout": 0, "cookie": 2000002, "priority": 50000, "hard_timeout": 0, "byte_count": 0, "duration_nsec": 6000000, "packet_count": 0, "duration_sec": 100, "table_id": 0, "match": {"wildcards": 3678459, "dl_src": "ee:ee:ee:ee:ee:02"}}, {"actions": [{"type": "OFPActionStripVlan(3)"}, {"max_len": 0, "type": "OFPActionOutput(0)", "port": 1}], "idle_timeout": 0, "cookie": 0, "priority": 32768, "hard_timeout": 0, "byte_count": 0, "duration_nsec": 906000000, "packet_count": 0, "duration_sec": 142, "table_id": 0, "match": {"wildcards": 3678460, "dl_vlan": 200, "in_port": 2}}, {"actions": [{"type": "OFPActionVlanVid(1)", "vlan_vid": 200}, {"max_len": 0, "type": "OFPActionOutput(0)", "port": 2}], "idle_timeout": 0, "cookie": 0, "priority": 32768, "hard_timeout": 0, "byte_count": 0, "duration_nsec": 933000000, "packet_count": 0, "duration_sec": 142, "table_id": 0, "match": {"wildcards": 3678462, "in_port": 1}}, {"actions": [{"max_len": 65509, "type": "OFPActionOutput(0)", "port": 65533}], "idle_timeout": 0, "cookie": 0, "priority": 1, "hard_timeout": 0, "byte_count": 2760, "duration_nsec": 492000000, "packet_count": 46, "duration_sec": 112, "table_id": 0, "match": {"wildcards": 3678437, "dl_type": 35020, "dl_dst": "01:80:c2:00:00:0e", "dl_vlan": 100}}], "dpid": "0000000000000001"}';



var SPEED_100GB = 100000000000;
var SPEED_10GB = 10000000000;
var SPEED_1GB = 1000000000;



var SIZE = {'switch': 16,
            'domain': 3,
            'port': 8,
            'host': 16};

var SIZE_PATH = {'switch': 700,
            'domain': 700,
            'port': 80,
            'host': 700};


var DISTANCE = {'domain': 10 * SIZE['switch'],
                'switch': 10 * SIZE['switch'],
                'port': SIZE['switch'] + 16,
                'host': 10 * SIZE['switch']};


/**
This is the class that will create a graph.
*/
var ForceGraph = function(p_selector, p_data) {
    // Local variable representing the forceGraph data
    var _data = ''
    _data = p_data



    // Define contextual menu over the circles
    var node_context_menu = function(data) {
        forcegraph.exit_highlight();
        return [
            {
                title: function(d) {
                    var sw = sdntopology.get_node_by_id(d.name);
                    return sw.id;
                },
                disabled: true
            },
            {
                divider: true
            },
            {
                title: function(d) {
                    var sw = sdntopology.get_node_by_id(d.name);
                    return 'Name: ' + sw.get_name();
                },
                disabled: true
            },
// TODO: Expecting new info services
//            {
//                title: 'Interfaces (' + data.data.n_ports + ')',
//                action: function(elm, d, i) {
//                    sdntopology.call_get_switch_ports(d.dpid, sdntopology._render_html_popup_ports);
//                }
//            },
//            {
//                title: 'Total traffic: 000',
//                action: function() {}
//            },
            {

                title: 'Flows',
                action: function(elm, d, i) {
                    forcegraph.set_switch_flow_focus_panel_data(d);

                    sdnflowtable.setData(d.data.dpid, d.data.flow_pivot);
                    sdnflowtable.dialogOpen();
                }
            },
            {
                title: 'Trace',
                action: function(elm, d, i) {
                    sdntopology.show_trace_form(d);
                }
            }
        ];
    };

    var width = 960,
        height = 600;

    var highlight_transparency = 0.1;
    // highlight var helpers
    // highlight var helpers
    var focus_node = null;

    var min_zoom = 0.1;
    var max_zoom = 7;

    // flag to outline drawing during ondrag
    var outline = false;

    // node/circle size
    var size = d3.scaleLinear()
      .domain([1,100])
      .range([8,24]);
    var nominal_base_node_size = 8;
    var nominal_stroke = 1.5;

    var _linkedByIndex = new Map();

    function addConnection(a, b) {
        /**
         a: source switch dpid
         b: target switch dpid
        */
        _linkedByIndex.set(a + "-" + b, true);
    }

	function isConnected(a, b) {
        return _linkedByIndex.has(a.id + "-" + b.id) || _linkedByIndex.has(b.id + "-" + a.id) || a.id == b.id;
    }

    // zoom behavior
    var zoomed = function(d) {
        container.attr("transform", "translate(" + d3.event.transform.x + "," + d3.event.transform.y + ")scale(" + d3.event.transform.k + ")");
    }
    // zoom configuration
    var zoom = d3.zoom()
        .scaleExtent([min_zoom, max_zoom])
        .on("zoom", zoomed);
/*
    svg = d3.select(selector)
        .append("div")
        .classed("svg-container", true) //container class to make it responsive
        .append('svg')
        .attr("width", width)
        .attr("height", height)
        .attr("preserveAspectRatio", "xMinYMin meet")
        .attr("viewBox", "0 0 " + width +" "+ height)
        //class to make it responsive
        .classed("svg-content-responsive", true)
        .append("g")
        .call(zoom);
        ;
    */
    var svg = d3.select(p_selector)
        .append("svg")
            .attr("width", "100%")
            .attr("height", "100%")
            .call(zoom);

    var container = svg.append("g");

    // ForceGraph set data. Remember to redraw the simulation after the set.
    this.data = function(value) {
        if ( typeof value === 'undefined') {
            // accessor
            return _data;
        }
        _data = value;

        return this;
    }

    var collisionForce = d3.forceCollide(12).strength(10).iterations(20);
    var force = d3.forceSimulation()
        .force("link",
            d3.forceLink()
                .id(function(d) { return d.id })
                .distance(function(d) {
                    if (d.edgetype == 's_p') {
                        return 0;
                    }
                    return DISTANCE['switch'];
                })
                .strength(0.1)
        )
        .force("collisionForce",collisionForce)
        .force("charge", d3.forceManyBody())
        .on("tick", ticked);

    // OBS: SVG Document order is important!
    // Draw order:
    //     links
    //     nodes
    //     labels

    // draw link paths
    var path = container.append("g")
        .attr("class", "paths")
        .selectAll("path");
    // switch node
    var node = container
        .append("g")
        .attr("class", "nodes")
        .selectAll("circle")
    // domain node
    var rect = container
        .append("g")
        .attr("class", "domains")
        .selectAll("rect")
    // draw switch label
    var text = container.append("g").selectAll("text");
    // draw link label
    var link_label = container.append("g").selectAll("text");


    // Hide node context menu.
    var _hide_context_menu = function() {
        $('.d3-context-menu').hide();
    }

    var _nodeDragstarted = function (d) {
        if (d.type == 'port') { return " node_port"; }
        if (!d3.event.active) force.alphaTarget(0.3).restart()
        d.fx = d.x;
        d.fy = d.y;

        if (d.type == 'domain') {
            var xx = d.fx;
            var yy = d.fy;

            d3.select(this)
                .attr("transform", function(d) {
                  return "translate(" + xx + ", " + yy + ")";
                });
        }
        // if node context menu is open, close it.
        _hide_context_menu();
    }

    var _nodeDragged = function (d) {
        if (d.type == 'port') { return " node_port"; }
        d.fx = d3.event.x;
        d.fy = d3.event.y;

        if (d.type == 'domain') {
            var xx = d.fx;
            var yy = d.fy;
            d3.select(this)
                .attr("transform", function(d) {
                  return "translate(" + xx + ", " + yy + ")";
                });
        }
    }

    var _nodeDragended = function (d) {
        if (d.type == 'port') { return " node_port"; }
        if (!d3.event.active) force.alphaTarget(0);
        focus_node = null;
        forcegraph.exit_highlight(d);
    }


    // Highlight onclick functions
    function set_highlight(d) {
        svg.style("cursor","pointer");
        if (focus_node!==null)
            d = focus_node;
        node.attr("fill", function(o) {
                return isConnected(d, o) ? sdncolor.NODE_COLOR_HIGHLIGHT[o.type] : sdncolor.NODE_COLOR[o.type];});
        text.style("font-weight", function(o) {
            return isConnected(d, o) ? "bold" : "normal";});
        path.style("stroke", function(o) {
            return o.source.index == d.index || o.target.index == d.index ? sdncolor.LINK_COLOR_HIGHLIGHT['switch'] : sdncolor.LINK_COLOR['switch'];
        });
    }


    this.exit_highlight = function(d) {
        svg.style("cursor","move");
        node.attr("fill", function(o) { return o.background_color; })
            .style("opacity", 1);
            //.style(towhite, "white");
        path.style("opacity", 1)
            .style("stroke", function(o) { return sdncolor.LINK_COLOR[o.type]; });
        text.style("opacity", 1)
            .style("font-weight", "bold");
    }

    // Show topology colors for Switches that are used to Trace
    // It is just to identify the difference in color field
    this.show_topology_colors = function() {
        var nodes = d3.selectAll(".node");
        nodes.attr("fill", function(d) {
                if(d.type == "switch") {
                    for (var x in sdncolor.colors) {
                        if (x == d.data.switch_color) {
                            return sdncolor.colors[d.data.switch_color];
                        }
                    }
                }
                return d.background_color;
            });
    }
    this.restore_topology_colors = function() {
        var nodes = d3.selectAll(".node");
        nodes.attr("fill", function(d) {
            return d.background_color;
        });
    }



    // focus highlight (on node mousedown)
    function set_switch_focus(d) {
        // Set data info panel
        if(d && d.data) {
            $('#port_panel_info').hide();
            $('#switch_to_panel_info').hide();
            $('#switch_flows_panel').hide();
            $('#domain_panel_info').hide();

            _set_switch_focus_panel_data(d);
        }

        // Set nodes and links opacity to all of them that are not connected to the clicked node
        if (highlight_transparency < 1) {
            node.style("opacity", function(o) {
                return isConnected(d, o) ? 1 : highlight_transparency;
            });
            text.style("opacity", function(o) {
                return isConnected(d, o) ? 1 : highlight_transparency;
            });
            path.style("opacity", function(o) {
                return o.source.index == d.index || o.target.index == d.index ? 1 : highlight_transparency;
            });
        }
        // Set the focused node to the highlight color
        node.attr("fill", function(o) {
                return isConnected(d, o) ? sdncolor.NODE_COLOR_HIGHLIGHT[o.type] : sdncolor.NODE_COLOR[o.type];})
            .style("opacity", function(o) {
                return isConnected(d, o) ? 1 : highlight_transparency;
            });
    }

    // focus highlight (on node mousedown)
    function set_port_focus(d) {
        $('#domain_panel_info').hide();
        $('#switch_flows_panel').hide();

        // Set data info panel
        if(d && d.data) {
            $('#port_panel_info').show();
            var name = d.data.label;
            $('#port_panel_info_collapse').collapse("show");

            if (name && name.length > 0) {
                $('#port_panel_info_name').show();
                $('#port_panel_info_name_value').html(name);
            } else {
                $('#port_panel_info_name').hide();
            }

            $('#port_panel_info_number_value').html(d.data.number);
            $('#port_panel_info_speed_value').html(d.data.speed);
            $('#port_panel_info_status_value').html(d.data.status);
            _set_switch_focus_panel_data(d.from_sw);
        }
    }

    // focus highlight (on node mousedown)
    function set_domain_focus(d) {
        // Set data info panel
        if(d && d.data) {
            // hide switch info
            $('#switch_to_panel_info').hide();
            // hide port info
            $('#port_panel_info').hide();

            $('#switch_flows_panel').hide();

            // show domain info
            _set_domain_focus_panel_data(d);
            $('#domain_panel_info_collapse').collapse("show");
        }
    }

    /** use with set_switch_focus to set the lateral panel data  */
    function _set_domain_focus_panel_data(d) {
        $('#domain_panel_info').show();
        $('#domain_panel_info_collapse').collapse("show");
        $('#domain_panel_info_dpid_value').html(d.data.domain);
        var name = d.data.get_name();

        if (name && name.length > 0) {
            $('#domain_panel_info_name').show();
            $('#domain_panel_info_name_value').html(name);
        } else {
            $('#domain_panel_info_name').hide();
        }
    }


    /** use with set_switch_focus to set the lateral panel data  */
    function _set_switch_focus_panel_data(d) {
        // display panel
        $('#switch_panel_info').show();
        // animation to open panel
        $('#switch_panel_info_collapse').collapse("show");
        // fill html content
        $('#switch_panel_info_dpid_value').html(d.data.dpid);
        var name = d.data.get_name();
        if (name && name.length > 0) {
            $('#switch_panel_info_name').show();
            $('#switch_panel_info_name_value').html(name);
        } else {
            $('#switch_panel_info_name').hide();
        }

        $('#switch_panel_info_flows_value').html(d.data.number_flows);
        if (d.data.number_flows && d.data.number_flows > 0) {
            // Open flow panel clicking the flow number
            $('#switch_panel_info_flows').css('cursor', 'pointer');
            $('#switch_panel_info_flows').css('text-decoration', 'underline');
            $('#switch_panel_info_flows').click(function() {
                forcegraph.set_switch_flow_focus_panel_data(d);
            });
        }


        if (d.data.domain) {
            $('#switch_panel_info_domain').show();
            $('#switch_panel_info_domain_value').html(d.data.domain);
        } else {
            $('#switch_panel_info_domain').hide();
        }
        $('#switch_panel_info_tcp_port_value').html(d.data.tcp_port);
        $('#switch_panel_info_openflow_version_value').html(d.data.openflow_version);
        $('#switch_panel_info_switch_vendor_value').html(d.data.switch_vendor);
        $('#switch_panel_info_ip_address_value').html(d.data.ip_address);
        $('#switch_panel_info_color_value').html(d.data.switch_color);
    }

    /** use with set_switch_focus to set the lateral panel data  */
    this.set_switch_flow_focus_panel_data = function(d) {
        // Helper function to create <li> tags to display flow attributes
        var _create_li = function(d_ul, label, value) {
            var d_ul_li = $('<li></li>');
            d_ul.append(d_ul_li);
            d_ul_li.append($('<span>' + label + ': </span>'));
            d_ul_li.append($('<span>' + value + '</span>'));
        }

        // display panel
        $('#switch_flows_panel').show();
        // animation to open panel
        $('#switch_flows_panel_collapse').collapse("show");
        // fill html content
        $('#switch_flows_panel_dpid_value').html(d.data.dpid);
        var name = d.data.get_name();

        var _flow_stat = d.data.flow_stat;

        // Clear panel
        $('#switch_flows_panel_collapse > .panel-body').empty();
        // Prepare to create panel content
        var d = $('<div></div>');
        $('#switch_flows_panel_collapse > .panel-body').append(d);


        for(var x in _flow_stat.flows) {
            var flowObj = _flow_stat.flows[x];

            // Flow actions
            var actionStr = '<table class="table-bordered table-condensed"><thead><tr><th>Type</th><th>Max Len.</th><th>Port</th></tr></thead><tbody>';
            for(var y in flowObj.actions) {
                var actionObj = flowObj.actions[y];
                actionStr += '<tr><td>' + actionObj.type + '</td><td>' + (actionObj.max_len || '') + '</td><td>' + (actionObj.port || '') + '</td></tr>';
            }
            actionStr += '</tbody></table><br>';
            d.append($(actionStr));

            // Flow attributes
            var d_ul = $('<ul></ul>');
            d.append(d_ul);

            _create_li(d_ul, 'Idle timeout', flowObj.idle_timeout);
            _create_li(d_ul, 'Cookie', flowObj.cookie);
            _create_li(d_ul, 'Priority', flowObj.priority);
            _create_li(d_ul, 'Hard timeout', flowObj.hard_timeout);
            _create_li(d_ul, 'Byte count', flowObj.byte_count);
            _create_li(d_ul, 'Duration (ns)', flowObj.duration_nsec);
            _create_li(d_ul, 'Packet count', flowObj.packet_count);
            _create_li(d_ul, 'Duration (s)', flowObj.duration_sec);
            _create_li(d_ul, 'Table ID', flowObj.table_id);

            d_ul = $('<ul></ul>');
            d.append(d_ul);

            // Flow matches
            _create_li(d_ul, '<u>Match</u>', '');
            if(flowObj.match.wildcards) { _create_li(d_ul, 'wildcards', flowObj.match.wildcards || ''); }
            if(flowObj.match.in_port) { _create_li(d_ul, 'in_port', flowObj.match.in_port || ''); }
            if(flowObj.match.dl_vlan) { _create_li(d_ul, 'dl_vlan', flowObj.match.dl_vlan || ''); }
            if(flowObj.match.dl_type) { _create_li(d_ul, 'dl_type', flowObj.match.dl_type || ''); }
            if(flowObj.match.dl_src) { _create_li(d_ul, 'dl_src', flowObj.match.dl_src || ''); }
            if(flowObj.match.dl_dst) { _create_li(d_ul, 'dl_dst', flowObj.match.dl_dst || ''); }

            d.append($("<hr>"));
        }
    }

    function linkArc(d) {
        d3.selectAll("line")
            .attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });
    }

    function transform(d) {
        return "translate(" + d.x + "," + d.y + ")";
    }
    function transformNode(d) {
        return_val = '';
        if (d.type == "port") {
            var new_positions = radius_positioning(d.from_sw.x, d.from_sw.y, d.to_sw.x, d.to_sw.y);
            var dx = new_positions[0];
            var dy = new_positions[1];
            return_val = "translate(" + dx + "," + dy + ")";
        } else {
            return_val = "translate(" + d.x + "," + d.y + ")";
        }
        return return_val;
    }
    function transformLabel(d) {
        var dx = d.x;
        var dy = d.y;
        if (d.type == "port") {
            var new_positions = radius_positioning(d.from_sw.x, d.from_sw.y, d.to_sw.x, d.to_sw.y);
            dx = new_positions[0];
            dy = new_positions[1];
            return_val = "translate(" + dx + "," + dy + ")";
        } else {
            dx = dx - SIZE[d.type] / 2.0;
            return_val = "translate(" + dx + "," + dy + ")";
        }
        return return_val;
    }
    function transformLinkSourceLabel(d) {
        var new_positions = radius_positioning(d.source.x, d.source.y, d.target.x, d.target.y);
        var dx = new_positions[0] - SIZE['port'];
        var dy = new_positions[1] + SIZE['port']/2.0;
        return "translate(" + dx + "," + dy + ")";
    }
    function transformLinkTargetLabel(d) {
        var new_positions = radius_positioning(d.target.x, d.target.y, d.source.x, d.source.y);
        var dx = new_positions[0]
        var dy = new_positions[1]
        return "translate(" + dx + "," + dy + ")";
    }
    function transformLinkSpeedLabel(d) {
        // Do not move if the label is empty.
        if (d.speed) {
            dx = (d.source.x - d.target.x) * 0.5;
            dy = (d.source.y - d.target.y) * 0.5;
            return "translate(" + (d.target.x + dx) + "," + (d.target.y + dy) + ")";
        }
    }

    // Use elliptical arc path segments to doubly-encode directionality.
    function ticked(d) {
        d3.selectAll("line").attr("d", linkArc);
        d3.selectAll(".node").attr("transform", transformNode);
        d3.selectAll(".domain").attr("transform", transform);
        d3.selectAll(".node_text").attr("transform", transformLabel);
        d3.selectAll(".speed-label").attr("transform", transformLinkSpeedLabel);
    }

    this.draw = function() {
        force.stop();

        // Check to know if two nodes are connected
        for (var x in _data.links) {
            if (!isConnected(_data.links[x].source, _data.links[x].target)) {
                addConnection(_data.links[x].source, _data.links[x].target);
            }
        }

        // draw link paths
        path = path.data(_data.links, function(d) { return d.id; });
        path.exit().remove();
        path = path
            .enter()
                .append("line")
                    .attr("id", function(d) {
                        return "link-" + d.id;
                    })
                    .attr("class", function(d) {
                        var return_var = "";
                        if (d.speed >= SPEED_100GB) {
                            return_var = return_var + " link-path link-large";
                        } else if (d.speed >= SPEED_10GB) {
                            return_var = return_var + " link-path link-medium";
                        } else if (d.speed >= SPEED_1GB) {
                            return_var = return_var + " link-path link-thin";
                        }
                        return_var = return_var + " link-path link " + d.type;
                        return return_var;
                    })
                    .attr("marker-end", function(d) { return "url(#" + d.type + ")"; })
                    .style("stroke", function(d) {
                        if (d.edgetype == 's_p') {
                            return '#fff';
                        }
                        return d.color;
                    })
                    .merge(path);

        // switch draw
        node = node.data(_data.nodes, function(d) { return d.id;});
        node.exit().remove();
        node = node
            .enter()
                .append("path")
                .attr("d", d3.symbol()
                    .type(function(d) {
                        if (d.type == 'domain') { return d3.symbolWye; }
                        else if (d.type == 'host') { return d3.symbolSquare; }
                        return d3.symbolCircle;
                    })
                    .size(function(d) { return (SIZE_PATH[d.type]); }))
                .attr("id", function(d) { return "node-" + d.id; })
                .attr("r", function(d) { return SIZE[d.type]||nominal_base_node_size; })
                .attr("fill", function(d) { return d.background_color; })
                .attr("class", function(d) {
                    if (d.type == 'port') { return " node node_port"; }
                    return "node";
                })
                .style("display", function(d) {
                    if (d.type == 'port') { return "none"; }
                    return "";
                })
                .on('contextmenu', d3.contextMenu(node_context_menu)) // attach menu to element
                .on("mouseover", function(d) {
                    if (d.type == 'port') { return; }
                    if (d.type == 'switch') { set_highlight(d); }
                })
                .on("mousedown", function(d) {
                    d3.event.stopPropagation();

                    if (d.type == 'port') {
                        set_port_focus(d);
                    } else if (d.type == 'switch') {
                        // focus_node to control highlight events
                        focus_node = d;
                        set_switch_focus(d)
                    } else if (d.type == 'domain') {
                        // focus_node to control highlight events
                        focus_node = d;
                        set_domain_focus(d)
                    }
                })
                .on("mouseout", function(d) {
                    if (d.type == 'port') { return; }
                    if (focus_node === null) { forcegraph.exit_highlight(d); }
                })
                .on("click", function(d) {
                    if (d.type == 'port') { return; }
                    focus_node = null;
                    forcegraph.exit_highlight(d);
                })
                .on("dblclick.zoom", function(d) {
                    d3.event.stopPropagation();
                })
                .call(d3.drag()
                    .on("start", _nodeDragstarted)
                    .on("drag", _nodeDragged)
                    .on("end", _nodeDragended))
                .merge(node);

        // draw switch label
        text = text.data(_data.nodes, function(d) { return d.id;});
        text.exit().remove();
        text = text
            .enter()
                .append("text")
                    .attr("class", function(d) {
                        if (d.type == 'port') { return "node_text text_port"; }
                        return "node_text";
                    })
                    .attr("x", 0)
                    .attr("y", ".1em")
                    .style("display", function(d) {
                        if (d.type == 'port') { return "none"; }
                        return "";
                    })
                    .text(function(d) { if(d.label) return d.label; return d.name; })
                    .merge(text);

        // draw link label
        link_label = link_label.data(_data.links);
        link_label.exit().remove();
        link_label = link_label
            .enter()
                .append("text")
                    .attr("class", "speed-label")
                    .text(function(d) { return d.speed; })
                    .merge(link_label);

        // setting data
        force.force("link").links(_data.links, function(d) { return d.source.id + "-" + d.target.id; });
        force.nodes(_data.nodes, function(d) { return d.id;});

        force.restart();
    }
}

function radius_positioning(cx, cy, x, y) {
  delta_x = x - cx;
  delta_y = y - cy;
  rad = Math.atan2(delta_y, delta_x);
  new_x = cx + Math.cos(rad) * DISTANCE['port'];
  new_y = cy + Math.sin(rad) * DISTANCE['port'];

  return [new_x, new_y];
}


/**
 * SDNColor utility to transform SDN color codes to CSS names.
 */
var SDNColor = function() {
    this.colors = {'1':'darkseagreen', '10':'dodgerblue', '11':'chocolate', '100':'darkorange', '101':'darkviolet', '110':'darkturquoise', '111':'black' }
    this.trace_color_on = '#1AC91A';
    this.trace_color_off = 'lightgray';

    this.color_default = '#8EB5EA';

    this.NODE_COLOR = {'host': 'rgb(192,231,255)',
                       'domain': '#847DAF',
                       'switch': '#8EB5EA',
                       'port': "#0cc"};
    this.NODE_COLOR_HIGHLIGHT = {'domain': "#4D7C9D",
                                 'host': "#4D7C9D",
                                 'switch': "#4D7C9D",
                                 'port': "#007C9D"};

    //var NODE_BORDER_COLOR = {'switch': 30,
    //                         'port': 5};

    this.LINK_COLOR = {'domain': "#888",
                       'host': "#888",
                       'switch': "#888",
                       'port': "#888"};
    //var NODE_BORDER_COLOR_HIGHLIGHT = {'switch': 30,
    //                                   'port': 5};
    this.LINK_COLOR_HIGHLIGHT = {'domain': "#4D7C9D", 'host': "#4D7C9D", 'switch': "#4D7C9D"};
    this.LINK_COLOR_HIDE = {'domain': 'white', 'host': 'white', 'switch': 'white'};

    /**
     * Get color CSS name.
     *     param code: binary color code
     *     return: CSS color name
     */
    this.get_color = function(code) {
        var result = null;
        $.each( this.colors, function( key, val ) {
            if (key == code) {
                result = val;
            }
        });
        return result;
    }
}


var SDNTopology = function() {
    // switches list. It is used to help render the topology nodes.
    this.switches = [];
    // topology link list
    this.topology = [];
    // topology domains
    this.domains = []

    // topology check by index
    var _linkedByIndex = new Map();


    function addTopologyConnection(a, b) {
        /**
         a: source switch dpid
         b: target switch dpid
        */
        _linkedByIndex.set(a.id + "-" + b.id, true);
    }

	function isTopologyConnected(a, b) {
	    /**
	    * Check if node a and node b are connected.
	    */
        return _linkedByIndex.has(a.id + "-" + b.id) || _linkedByIndex.has(b.id + "-" + a.id) || a.id == b.id;
    }

    /**
     * Call ajax to load the switch list.
     */
    this.call_get_switches = function() {
        var ajax_done = function(jsonObj) {
            for (var x = 0; x < jsonObj.length; x++) {
                // storing switch values
                var switch_obj = new Switch(jsonObj[x].dpid);
                switch_obj.n_ports = jsonObj[x].n_ports;
                switch_obj.n_tables = jsonObj[x].n_tables;

                switch_obj.name = jsonObj[x].switch_name;
                switch_obj.switch_color = jsonObj[x].switch_color;
                switch_obj.tcp_port = jsonObj[x].tcp_port;
                switch_obj.openflow_version = jsonObj[x].openflow_version;
                switch_obj.switch_vendor = jsonObj[x].switch_vendor;
                switch_obj.ip_address = jsonObj[x].ip_address;
                //switch_obj.number_flows = jsonObj[x].number_flows;

                sdntopology.switches.push(switch_obj);
            }
            // sort
            sdntopology.switches = sdntopology.switches.sort();
            // deduplication
            sdntopology.switches = array_unique_fast(sdntopology.switches);
        }

        // AJAX call
        if (DEBUG) {
            json = MOCK_JSON_SWITCHES;
            var jsonobj = $.parseJSON(json);
            ajax_done(jsonobj);
        } else {
            var jqxhr = $.ajax({
                url:"/sdnlg/switches",
                dataType: 'json',
                crossdomain:true,
            }).done(function(json) {
                ajax_done(json);
            })
            .fail(function() {
                console.log( "call_get_switches ajax error" );
            })
            .always(function() {
                console.log( "call_get_switches ajax complete" );
            });
        }
    }

    this.call_sdntrace_get_switches = function(callback=null) {
        var ajax_done = function(jsonObj, p_callback) {
            for (var x = 0; x < jsonObj.length; x++) {
                // storing switch values
                var switch_obj = new Switch(jsonObj[x]);
                sdntopology.switches.push(switch_obj);

                var info_callback = null;
                // if is the last info retrieve, pass the callback to the call
                if (x == jsonObj.length - 1) {
                    info_callback = p_callback;
                }
                sdntopology.call_sdntrace_get_switch_info(jsonObj[x], info_callback);

                sdntopology.call_sdntrace_get_switch_flows(jsonObj[x]);
            }

            // sort
            sdntopology.switches = sdntopology.switches.sort();
            // deduplication
            sdntopology.switches = array_unique_fast(sdntopology.switches);

            if (callback != null) {
                try {
                    //callback();
                }
                catch(err) {
                    console.log("Error callback function: " + callback);
                    throw err;
                }
            }
        }

        // AJAX call
        if (DEBUG) {
            json = MOCK_JSON_SDNTRACE_SWITCHES;
            var jsonobj = $.parseJSON(json);

            ajax_done(jsonobj, callback);
        } else {
            var jqxhr = $.ajax({
                url:"/sdntrace/switches",
                dataType: 'json',
                crossdomain:true,
            }).done(function(json) {
                ajax_done(json, callback);
            })
            .fail(function() {
                console.log( "call_sdntrace_get_switches ajax error" );
            })
            .always(function() {
                console.log( "call_sdntrace_get_switches ajax complete" );
            });
        }
    }
    this.call_sdntrace_get_switch_info = function(p_dpid, callback=null) {
        var ajax_done = function(jsonObj, p_callback) {
            var switch_obj = sdntopology.get_node_by_id(p_dpid);

            switch_obj.n_ports = jsonObj.n_ports;
            switch_obj.n_tables = jsonObj.n_tables;

            switch_obj.name = jsonObj.switch_name;
            switch_obj.switch_color = jsonObj.switch_color;
            switch_obj.tcp_port = jsonObj.tcp_port;
            switch_obj.openflow_version = jsonObj.openflow_version;
            switch_obj.switch_vendor = jsonObj.switch_vendor;
            switch_obj.ip_address = jsonObj.ip_address;
            //switch_obj.number_flows = jsonObj.number_flows;

            sdntopology.call_sdntrace_get_switch_ports(p_dpid, p_callback);


            if (p_callback != null) {
                console.log('call_sdntrace_get_switch_info callback');
                try {
                    //callback();
                }
                catch(err) {
                    console.log("Error callback function: " + callback);
                    throw err;
                }
            }
        }

        // AJAX call
        if (DEBUG) {
            json = MOCK_JSON_SDNTRACE_SWITCH_INFO;
            var jsonobj = $.parseJSON(json);

            ajax_done(jsonobj, callback);
        } else {
            var jqxhr = $.ajax({
                url:"/sdntrace/switches/" + p_dpid + "/info",
                dataType: 'json',
                crossdomain:true,
            }).done(function(json) {
                ajax_done(json, callback);
            })
            .fail(function() {
                console.log( "call_sdntrace_get_switch_info ajax error" );
            })
            .always(function() {
                console.log( "call_sdntrace_get_switch_info ajax complete" );
            });
        }
    }
    this.call_sdntrace_get_switch_flows = function(p_dpid, callback=null) {
        var ajax_done = function(jsonObj, p_callback) {
            var switch_obj = sdntopology.get_node_by_id(p_dpid);

            switch_obj.number_flows = jsonObj.number_flows;

            switch_obj.flow_stat = {};

            switch_obj.flow_stat.dpid = p_dpid;
            switch_obj.flow_stat.flows = [];

            for(var x in jsonObj.flows) {
                var jsonFlow = jsonObj.flows[x];

                var flow_1 = {};
                flow_1.idle_timeout = jsonFlow.idle_timeout;
                flow_1.cookie = jsonFlow.cookie;
                flow_1.priority = jsonFlow.priority;
                flow_1.hard_timeout = jsonFlow.hard_timeout;
                flow_1.byte_count = jsonFlow.byte_count;
                flow_1.duration_nsec = jsonFlow.duration_nsec;
                flow_1.packet_count= jsonFlow.packet_count;
                flow_1.duration_sec = jsonFlow.duration_sec;
                flow_1.table_id = jsonFlow.table_id;

                flow_1.actions = [];
                for(var y in jsonFlow.actions) {
                    var jsonAction = jsonFlow.actions[y];

                    var flow_1_action_1 = {};
                    flow_1_action_1.max_len = jsonAction.max_len;
                    flow_1_action_1.type = jsonAction.type;
                    flow_1_action_1.port = jsonAction.port;
                    flow_1.actions.push(flow_1_action_1);
                }

                flow_1.match = {};
                flow_1.match.wildcards = jsonFlow.match.wildcards;
                flow_1.match.in_port = jsonFlow.match.in_port;
                flow_1.match.dl_vlan = jsonFlow.match.dl_vlan;
                flow_1.match.dl_src = jsonFlow.match.dl_src;
                flow_1.match.dl_dst = jsonFlow.match.dl_dst;
                flow_1.match.dl_type = jsonFlow.match.dl_type;

                switch_obj.flow_stat.flows.push(flow_1);
            }

            // TODO: test pivot table

            switch_obj.flow_pivot = [];


            for(var x in jsonObj.flows) {
                var jsonFlow = jsonObj.flows[x];

                var pivot = {};
                pivot.dpid = p_dpid;

                pivot.idle_timeout = jsonFlow.idle_timeout;
                pivot.cookie = jsonFlow.cookie;
                pivot.priority = jsonFlow.priority;
                pivot.hard_timeout = jsonFlow.hard_timeout;
                pivot.byte_count = jsonFlow.byte_count;
                //pivot.duration_nsec = jsonFlow.duration_nsec;
                pivot.packet_count= jsonFlow.packet_count;
                pivot.duration_sec = jsonFlow.duration_sec + (jsonFlow.duration_nsec / 1000000000.0);
                console.log(pivot.duration_sec);

                pivot.table_id = jsonFlow.table_id || '';

                pivot.match__wildcards = jsonFlow.match.wildcards || '';
                pivot.match__in_port = jsonFlow.match.in_port || ' ';
                pivot.match__dl_vlan = jsonFlow.match.dl_vlan || '';
                pivot.match__dl_src = jsonFlow.match.dl_src || '';
                pivot.match__dl_dst = jsonFlow.match.dl_dst || '';
                pivot.match__dl_type = jsonFlow.match.dl_type || '';

                if (jsonFlow.actions) {
                    for(var y in jsonFlow.actions) {
                        var jsonAction = jsonFlow.actions[y];

                        if(y > 0) {
                            pivot.action__max_len = pivot.action__max_len +"<br>"+ (jsonAction.max_len || '--');
                            pivot.action__type = pivot.action__type +"<br>"+ (jsonAction.type || '--');
                            pivot.action__port = pivot.action__port +"<br>"+ (jsonAction.port || '--');
                        } else {
                            pivot.action__max_len = (jsonAction.max_len || '--');
                            pivot.action__type = (jsonAction.type || '--');
                            pivot.action__port = (jsonAction.port || '--');
                        }
                    }
                }
                switch_obj.flow_pivot.push(pivot);
            }

            if (p_callback != null) {
                console.log('call_sdntrace_get_switch_info callback');
                try {
                    //callback();
                }
                catch(err) {
                    console.log("Error callback function: " + callback);
                    throw err;
                }
            }
        }

        // AJAX call
        if (DEBUG) {
            json = MOCK_JSON_FLOWS;
            var jsonobj = $.parseJSON(json);

            ajax_done(jsonobj, callback);
        } else {
            var jqxhr = $.ajax({
                url:"/sdntrace/switches/" + p_dpid + "/flows",
                dataType: 'json',
                crossdomain:true,
            }).done(function(json) {
                ajax_done(json, callback);
            })
            .fail(function() {
                console.log( "call_sdntrace_get_switch_info ajax error" );
            })
            .always(function() {
                console.log( "call_sdntrace_get_switch_info ajax complete" );
            });
        }
    }



    this.get_node_by_id = function(p_id) {
        /**
        Get node by id.
        Returns Switch and Domain
        */
        // add to topology list to render the html
        for (var key in sdntopology.switches) {
            if (sdntopology.switches[key].id == p_id) {
                return sdntopology.switches[key];
            }
        }
        //
        for (var key in sdntopology.domains) {
            if (sdntopology.domains[key].id == p_id) {
                return sdntopology.domains[key];
            }
        }
    }

    /**
    * Use this function instead of access the topology attribute.
    */
    this.add_topology = function(link) {
        if (isTopologyConnected(link.node1, link.node2) == false) {
            addTopologyConnection(link.node1, link.node2);
            // add to topology list to render the html
            this.topology.push(link);
        }
    }
    /**
    * Use this function to get the topology link object
    */
    this.get_topology_link = function(node1, node2) {
        if (isTopologyConnected(node1, node2)) {
            for (var x in this.topology) {
                if ((this.topology[x].node1.id == node1.id && this.topology[x].node2.id == node2.id) ||
                   (this.topology[x].node1.id == node2.id && this.topology[x].node2.id == node1.id)) {

                    return this.topology[x];
                }
            }
        }
        return null;
    }

    /**
     * Call ajax to load the switch topology.
     */
    this.call_sdntrace_get_topology = function(callback=null) {
        // hiding topology graphic panel
        $('#topology__canvas').hide();

        var ajax_done = function(json) {
            var jsonObj;
            jsonObj= json;

            // verify if the json is not a '{}' response
            if (!jQuery.isEmptyObject(jsonObj)) {
                $.each( jsonObj, function( p_dpid1, p_node_a ) {
                    var dpid1 = p_dpid1;

                    $.each( p_node_a, function( p_port_id, p_neighbor ) {

                        var port1 = p_port_id;
                        if (p_neighbor.type == "link") {
                            var dpid2 = p_neighbor.neighbor_dpid;
                            var port2 = p_neighbor.neighbor_port;

                            var linkObj = new Link();

                            // creating switch
                            var _switch1 = sdntopology.get_node_by_id(dpid1);
                            var _switch2 = sdntopology.get_node_by_id(dpid2);

                            var switch1 = Switch.clone_obj(_switch1);
                            var switch2 = Switch.clone_obj(_switch2);

                            if(isTopologyConnected(switch1, switch2)) {
                                linkObj = sdntopology.get_topology_link(switch1, switch2);
                            } else {
                                linkObj.node1 = switch1;
                                linkObj.node2 = switch2;
//
                                linkObj.node1.ports = [];
                                linkObj.node2.ports = [];
                            }
                            // creating switch ports from node1
                            var node1_port = _switch1.get_port_by_id(dpid1, port1);
                            if (node1_port == null) {
                                node1_port = new Port(dpid1, port1, port1, port1);
                                linkObj.node1.ports.push(node1_port);
                            } else {
                                linkObj.node1.ports.push(node1_port);
                            }
                            linkObj.label1 = node1_port.label;

                            // creating switch ports from node2
                            var node2_port = _switch2.get_port_by_id(dpid2, port2);
                            if (node2_port == null) {
                                node2_port = new Port(dpid2, port2, port2, port2);
                                linkObj.node2.ports.push(node2_port);
                            } else {
                                linkObj.node2.ports.push(node2_port);
                            }
                            linkObj.label2 = node2_port.label;

                            // link speed
                            if(node1_port && node1_port.speed) {
                                linkObj.speed = node1_port.speed;
                            } else if(node2_port && node2_port.speed) {
                                linkObj.speed = node2_port.speed;
                            }
                        } else if (p_neighbor.type == "host") {
                            // Add new host node
                            var _host_label = "";
                            if (typeof(p_neighbor.neighbor_name)!=='undefined') {
                                _host_label = p_neighbor.neighbor_name;
                            }

                            var linkObj = new Link();

                            // add node data do d3
                            var _switch1 = sdntopology.get_node_by_id(dpid1);
                            var switch1 = Switch.clone_obj(_switch1);
                            linkObj.node1 = switch1;
                            linkObj.node1.ports = [];

                            // creating switch ports from node1
                            var node1_port = _switch1.get_port_by_id(dpid1, port1);
                            if (node1_port == null) {
                                node1_port = new Port(dpid1, port1, port1, port1);
                                linkObj.node1.ports.push(node1_port);
                            } else {
                                linkObj.node1.ports.push(node1_port);
                            }
                            linkObj.label1 = node1_port.label;


                            var host_obj = d3lib.add_new_node_host(dpid1, port1, _host_label);

//                            linkObj.node1 = sdntopology.get_node_by_id(dpid1);
                            linkObj.node2 = host_obj;

                            // creating host ports
                            var port2 = p_neighbor.neighbor_port;
                            var node2_port = new Port(host_obj.id +'_'+ port2, port2, "");

                            linkObj.node2.ports = [node2_port];
                            linkObj.label_num2 = port2;
                        } else if (p_neighbor.type == "interdomain") {
                            // Add new host node
                            var _domain_label = "";
                            if (typeof(p_neighbor.domain_name)!=='undefined') {
                                _domain_label = p_neighbor.domain_name;
                            }

                            // add node data do d3

                            var linkObj = new Link();

                            var _switch1 = sdntopology.get_node_by_id(dpid1);
                            var switch1 = Switch.clone_obj(_switch1);
                            linkObj.node1 = switch1;
                            linkObj.node1.ports = [];

                            // creating switch ports from node1
                            var node1_port = _switch1.get_port_by_id(dpid1, port1);
                            if (node1_port == null) {
                                node1_port = new Port(dpid1, port1, port1, port1);
                                linkObj.node1.ports.push(node1_port);
                            } else {
                                linkObj.node1.ports.push(node1_port);
                            }
                            linkObj.label1 = node1_port.label;



                            var domain_obj = d3lib.add_new_node_domain(_domain_label, _domain_label);
                            linkObj.node2 = domain_obj;
                        }
                        // Add the node the the topology
                        if (linkObj) {
                            sdntopology.add_topology(linkObj);
                        }
                    });
                });

                // render HTML data
//                sdntopology.render_html_topology();

                // render D3 force
                d3lib.render_topology();
                sdntopology.show_topology_canvas();
            }
        }

        // AJAX call
        if (DEBUG) {
            json = MOCK_JSON_TOPOLOGY_TRACE;
            var jsonobj = $.parseJSON(json);
            ajax_done(jsonobj);
        } else {
            var jqxhr = $.ajax({
                url: "/sdntrace/switches/topology",
                dataType: 'json',
            }).done(function(json) {
                ajax_done(json);
            })
            .fail(function() {
                console.log( "call_get_topology ajax error" );
            })
            .always(function() {
                console.log( "call_get_topology ajax complete" );
            });
        }
    }

    /**
     * Call ajax to load the switch ports data.
     */
    this.call_get_switch_ports = function(dpid, callback=null) {
        var ajax_done = function(json) {
            var jsonObj;
            jsonObj= json;

            // verify if the json is not a '{}' response
            if (callback != null && !jQuery.isEmptyObject(jsonObj)) {
                // render D3 popup
                try {
                    callback(dpid, jsonObj);
                }
                catch(err) {
                    console.log("Error callback function: " + callback);
                    throw err;
                }
            }
        }

        // AJAX call
        if (DEBUG) {
            json = MOCK_JSON_SWITCH_PORTS;
            var jsonobj = $.parseJSON(json);
            ajax_done(jsonobj);
        } else {
            var jqxhr = $.ajax({
                url: "/sdnlg/switches/" + dpid + "/ports",
                dataType: 'json',
            }).done(function(json) {
                ajax_done(json);
            })
            .fail(function() {
                console.log( "call_get_switch_ports ajax error" );
            })
            .always(function() {
                console.log( "call_get_switch_ports ajax complete" );
            });
        }
    }


    /**
     * Call ajax to load the switch ports data.
     */
    this.call_sdntrace_get_switch_ports = function(p_dpid, callback=null) {
        var ajax_done = function(json, p_callback) {
            var jsonObj;
            jsonObj= json;

            var switch_obj = sdntopology.get_node_by_id(p_dpid);

            if (switch_obj) {
                $.each(jsonObj, function( key, p_port_data ) {
                    var port_obj = switch_obj.get_port_by_id(p_dpid, p_port_data.port_no);
                    if (port_obj == null) {
                        port_obj = new Port(p_dpid, p_port_data.port_no, p_port_data.port_no, p_port_data.name, p_port_data.speed, p_port_data.uptime, p_port_data.status);

                        // create Port object and push to the switch ports
                        if (switch_obj.ports == null) { switch_obj.ports = []; }
                        switch_obj.ports.push(port_obj);
                    }

                    port_obj.speed = p_port_data.speed;
                    port_obj.label = p_port_data.name;
                    port_obj.number = p_port_data.port_no;
                    port_obj.status = p_port_data.status;

                });

                // verify if the json is not a '{}' response
                if (p_callback != null && !jQuery.isEmptyObject(jsonObj)) {
                    // render D3 popup
                    try {
                        p_callback(p_dpid, jsonObj);
                    }
                    catch(err) {
                        console.log("Error callback function: " + p_callback);
                        throw err;
                    }

                }
            }
        }

        // AJAX call
        if (DEBUG) {
            json = MOCK_JSON_SDNTRACE_SWITCH_PORTS;
            var jsonobj = $.parseJSON(json);
            ajax_done(jsonobj, callback);
        } else {
            var jqxhr = $.ajax({
                url: "/sdntrace/switches/" + p_dpid + "/ports",
                dataType: 'json',
            }).done(function(json) {
                ajax_done(json, callback);
            })
            .fail(function() {
                console.log( "call_get_switch_ports ajax error" );
            })
            .always(function() {
                console.log( "call_get_switch_ports ajax complete" );
            });
        }
    }

    this._render_html_popup_ports = function(dpid, jsonObj) {
        /**
        Callback to be used with the AJAX that retrieve switch ports.
        */

        var popup_switch = function(dpid, data) {
            // remove possible popups
            d3.select(".canvas")
                .selectAll(".popup")
                .remove();

             // Build the popup
            popup = d3.select(".canvas")
                .append("div")
                .attr("class", "popup")
                .attr("id", "switch_popup");
            // close icon
            popup.append("button")
                .attr("type", "button")
                .attr("class", "close")
                .append("span")
                    .html('&times;')
                    // removing the popup
                    .on("click", function(d) {
                        d3.select(".canvas")
                        .selectAll(".popup")
                        .remove();
                    });
            // popup content
            popup.append("div")
                .attr("class","popup_header")
                .text(dpid);
            popup.append("div")
                .attr("class","popup_header")
                .text("Interfaces (" + data.length + "):")
            popup.append("hr");
            var popup_body = popup
                .append("div")
                .attr("class","popup_body")

            var update_popup_body = popup_body
                .selectAll("p")
                .data(data)
                .enter()
                    .append("p")
                        .append("a")
                            // adding click function
                            .on("click", function(d) {
                                popup.selectAll(".popup_body").remove();
                                var popup_body = popup.append("div").attr("class","popup_body")
                                popup_body.append("p").text("Port n.: " + d.port_no);
                                popup_body.append("p").text("Port name: " + d.name);
                                popup_body.append("p").text("Port speed: " + format_speed(d.speed));
                                popup_body.append("p").text("Port uptime: " + d.uptime);
                                // adding back button
                                popup_body.append("p")
                                    .append("a")
                                    .text("back")
                                    .on("click", function() { popup_switch(dpid, data); });
                             })
                            .text(function(d) { return d.port_no + " - " + d.name; });
            update_popup_body.exit();
        }

        popup_switch(dpid, jsonObj);

    }


    /**
     * Render HTML of the topology.
     */
    this.render_html_topology = function() {
        if (sdntopology.topology) {

            $('#topology__canvas').show();
            $('#topology__elements').show();

            html_content = ""
            html_content += "<div class='row'>";
            html_content += "<div class='col-sm-12 col-md-12'>"
            html_content += "<table id='switches_topology_table' class='table'><tbody>"

            for (var x = 0; x < sdntopology.topology.length; x++) {
                html_content += "<tr>"
                html_content += "<td>";

                // display nice switch name
                var temp_switch = new Switch(sdntopology.topology[x].node1);
                html_content += temp_switch.get_name_or_id();

                // start left content, origin switch
                html_content += "</td><td>";
                html_content += "</td>";
                // end left content, origin switch

                html_content += "<td><span class='glyphicon glyphicon-arrow-right' aria-hidden='true'></span></td>";
                html_content += "<td>"

                // start right content, destination switch
                if (sdntopology.topology[x].node2) {
                    html_content += "<li>"
                    // display nice switch name
                    var temp_switch = sdntopology.topology[x].node2;
                    html_content += temp_switch.get_name_or_id();
                    html_content += "</li>"
                    html_content += "</td><td>";
                } else {
                    html_content += "</td><td>";
                }
                html_content += "</td></tr>"
                // end right content, destination switch
            }
            html_content += "</tbody></table>";
            html_content += "</div>";

            $('#topology__elements__list').html(html_content);
        }
    }

    /**
     * Show the trace form to trigger the SDN Trace.
     * It has three forms, to L2, L3 and full trace.
     * We use modal forms over the layout.
     */
    this.show_trace_form = function(d) {
        // setting switch label
        $('#sdn_trace_form__switch-content').html(d.label + " - " + d.dpid);

//        sdntopology.call_get_switch_ports(d.dpid, sdntrace._render_html_trace_form_ports);
        sdntopology.call_sdntrace_get_switch_ports(d.dpid, sdntrace._render_html_trace_form_ports);

        // open modal dialog
        sdn_trace_form_dialog.dialog("open");
    }

    this.show_topology_canvas = function() {
        $('#topology__canvas').show();
    }

}

var D3JS = function() {
    this.nodes = null;
    this.edges = null;

    this.find_node = function(p_id) {
        var id = '';
        // Check if the p_id is an object or the real ID attribute
        if ( typeof p_id.id === 'undefined') {
            id = p_id;
        } else {
            id = p_id.id;
        }

        for (var k in this.nodes){
            if (this.nodes.hasOwnProperty(k) && this.nodes[k] && this.nodes[k].id == id) {
                 return this.nodes[k];
            }
        }
        return null;
    }

    this.hasNode = function(p_id) {
        var find_node_obj =  this.find_node(p_id);
        if (find_node_obj == null) {
            return false;
        } else {
            return true;
        }
    }

    this.removeNode = function(id) {
        // Delete the node from the array
        for (var k in this.nodes){
            if (this.nodes.hasOwnProperty(k) && this.nodes[k] && this.nodes[k].id == id) {
                 this.nodes.splice(k, 1);
            }
        }
        // Delete the edges related to the deleted node
        for (var k in this.edges){
            if (this.edges.hasOwnProperty(k) && this.edges[k]) {
                if (this.edges[k].source.id == id || this.edges[k].target.id == id)
                 this.edges.splice(k, 1);
            }
        }
        return null;
    }

    /**
     * Render topology using topology data saved in sdntopology object.
     * It uses the vis.js graph library.
     * You must load the sdntopology switch and topology data before trying to render the topology.
     */
    this.render_topology = function() {
        this._render_network(false, false);
    }

    /**
     * Create D3JS network nodes.
     * We use the sdntopology.switch list to create the nodes and expect that the topology will have the same
     * node identification to draw the network edges.
     */
    this._create_network_nodes = function(with_colors, with_trace, update_current=false) {
        // create an array with nodes
        var nodesArray = [];
        for (x = 0; x < sdntopology.switches.length; x++) {
            // positioning in spiral mode to help the physics animation and prevent crossing lines
            node_obj = sdntopology.switches[x].get_d3js_data()

            if (update_current) {
                for (y = 0; y < this.nodes.length; y++) {
                    if (this.nodes[y].id == node_obj.id) {
                        node_obj = this.nodes[y];
                    }
                }
            }

            nodesArray.push(node_obj);
        }
        for (x = 0; x < sdntopology.domains.length; x++) {
            // positioning in spiral mode to help the physics animation and prevent crossing lines
            node_obj = sdntopology.domains[x].get_d3js_data()

            if (update_current) {
                for (y = 0; y < this.nodes.length; y++) {
                    if (this.nodes[y].id == node_obj.id) {
                        node_obj = this.nodes[y];
                    }
                }
            }
            nodesArray.push(node_obj);
        }
        this.nodes = nodesArray;
    }


    /**
     * Check if edge object already exists inside an array of edges.
     * It check from->to and to->from edges.
     * Returns the array object if exists, or false.
     */
    this._has_edge_path = function(edge_array, edge) {
        for (var x = 0; x < edge_array.length; x++) {
            if ((edge.from == edge_array[x].from && edge.to == edge_array[x].to) ||
                (edge.to == edge_array[x].from && edge.from == edge_array[x].to)) {

                return edge_array[x];
            }
        }
        return false;
    }

    /**
     * Create D3JS network edges.
     * This function can be used to create the topology, topology with color and
     * topology with tracing.
     */
    this._create_network_edges = function(with_colors, with_trace, update_current=false) {
        var edgesArray = [];

        // verify topology to create edges
        for (var x = 0; x < sdntopology.topology.length; x++) {
            node_from_id = sdntopology.topology[x].node1;
            node_to_id = sdntopology.topology[x].node2;

            label_from = sdntopology.topology[x].label1;
            label_to = sdntopology.topology[x].label2;

            label_num_from = sdntopology.topology[x].label_num1;
            label_num_to = sdntopology.topology[x].label_num2;

            speed = sdntopology.topology[x].speed;

            source = this.find_node(node_from_id) || this.nodes.push({id:node_from_id, dpid:node_from_id, name: node_from_id});
            target = this.find_node(node_to_id) || this.nodes.push({id:node_to_id, dpid:node_to_id, name: node_to_id});

            source_label = {name: label_from, num: label_num_from};
            target_label = {name: label_to, num: label_num_to};

            id = source.id + "-" + target.id;

            edgeObj = {id:id, name:x, source: source, target: target, source_label:source_label, target_label:target_label, speed:speed, arrows:'to', type: "suit"};
            edgeObj.color = sdncolor.LINK_COLOR['switch'];


            // Verify trace to change edge colors and labels.
            has_edge_path_obj = this._has_edge_path(edgesArray, edgeObj);

            // Update current link instead of creating a new one
            if (update_current) {
                for (y = 0; y < this.edges.length; y++) {
                    if (this.edges[y].id == edgeObj.id) {
                        edgeObj = this.edges[y];
                    }
                }
            }

            edgesArray.push(edgeObj);

            // adding port as a node
            var node_port_obj_from;
            var node_port_obj_to;
            if (node_from_id.ports && node_from_id.ports.length > 0 && node_from_id.ports[0]) {
                node_port_obj_from = node_from_id.ports[0].get_d3js_data()
                node_port_obj_from.from_sw = source;
                node_port_obj_from.to_sw = target;

                if(!this.hasNode(node_port_obj_from.id)) {
                    this.nodes.push(node_port_obj_from);
                }
            }

            if (node_to_id.ports && node_to_id.ports.length > 0 && node_to_id.ports[0]) {
                node_port_obj_to = node_to_id.ports[0].get_d3js_data()
                node_port_obj_to.from_sw = target;
                node_port_obj_to.to_sw = source;

                if(!this.hasNode(node_port_obj_to.id)) {
                    this.nodes.push(node_port_obj_to);
                }
            }
        }

        this.edges = edgesArray;
    }

    this._render_network = function(with_colors, with_trace) {
        with_colors = typeof with_colors !== 'undefined' ? with_colors : true;
        with_trace = typeof with_trace !== 'undefined' ? with_trace : true;

        // create a network
        var selector = "#topology__canvas";

        // create an array with nodes
        this._create_network_nodes(with_colors, with_trace);

        // create an array with edges
        this._create_network_edges(with_colors, with_trace);

        var data = {
            nodes: this.nodes,
            links: this.edges,
            edges_data: this.edges
        };

        // creating Force Graph nodes
        // Set the new data
        forcegraph.data(data);
        // Create the graph object
        // Having myGraph in the global scope makes it easier to call it from a json function or anywhere in the code (even other js files).
        forcegraph.draw();
        // Draw the graph for the first time
    }

    this.add_new_node_host = function(p_dpid, p_port_id, p_label="") {
        if (this.nodes) {
            var _host_id = Host.create_id(p_dpid, p_port_id);
            for (y = 0; y < this.nodes.length; y++) {
                if(this.nodes[y].id == _host_id) {
                    // do nothing
                    return this.nodes[y];
                }
            }
        } else {
            this.nodes = [];
        }

        var host_obj = new Host(p_dpid, p_port_id, p_label);

        sdntopology.domains.push(host_obj);

        if (this.nodes) {

            // create an array with nodes
            this._create_network_nodes(false, false, true);

            var data = forcegraph.data();
            data.nodes = this.nodes;

            // Draw the d3js graph
            forcegraph.draw();
        }

        return host_obj;
    }

    this.add_new_node_domain = function(id=null, label="") {
        var domain_id = Domain.create_id(id);

        if(this.nodes) {
            for (y = 0; y < this.nodes.length; y++) {
                if(this.nodes[y].id == domain_id) {
                    // do nothing
                    return this.nodes[y];
                }
            }
        } else {
            this.nodes = [];
        }

        var domain_obj = new Domain(domain_id);
        domain_obj.label = label;

        sdntopology.domains.push(domain_obj);

        // create an array with nodes
        this._create_network_nodes(false, false, true);

        var data = forcegraph.data();
        data.nodes = this.nodes;

        // Draw the d3js graph
        forcegraph.draw();

        return domain_obj;
    }

    this.add_new_link = function(id_from, id_to, label="") {

        var node_from = sdntopology.get_node_by_id(id_from);
        var node_to = sdntopology.get_node_by_id(id_to);

        var _link = sdntopology.get_topology_link(node_from, node_to);
        if (_link == null) {
            _link = {node1: node_from , node2:node_to, label1:label, label2:label, speed:""}

            sdntopology.add_topology(_link);

            // create an array with edges
            this._create_network_edges(false, false, true);

            var data = forcegraph.data();
            data.links = this.edges;
            data.edges_data = this.edges;

            // Draw the d3js graph
            forcegraph.draw();
        }
    }

    this.add_new_node = function(p_dpid=null, p_label="", p_domain=null) {
        with_colors = typeof with_colors !== 'undefined' ? with_colors : true;
        with_trace = typeof with_trace !== 'undefined' ? with_trace : true;

        var _dpid = "";
        if (p_dpid) {
            _dpid = p_dpid;
        }

        if (d3lib.has_switch(_dpid)) {
            return;
        }

        var _switch_obj = new Switch(_dpid);
        if (p_label) { _switch_obj.name = p_label; }
        if (p_domain) { _switch_obj.domain = p_domain; }

        sdntopology.switches.push(_switch_obj);

        // create an array with nodes
        this._create_network_nodes(with_colors, with_trace, true);

        var data = forcegraph.data();
        data.nodes = this.nodes;

        forcegraph.draw();
    }

    this.has_switch = function(p_id) {
        for(var x in sdntopology.switches) {
            if(sdntopology.switches[x].id == p_id) {
                return true;
            }
        }
        return false;
    }


    this.resetAllNodes = function() {
        if (this.nodes) {
            this.nodes = [];
        }
        if (this.edges) {
            this.edges = [];
        }
    }
}




var forcegraph = '';
var sdntopology = '';
var sdncolor = '';
var sdnflowtable = '';

/* Initial data load */
/* Call ajax to load switches and topology */
var _initial_data_load = function() {
    // Clearing contents
    $('#switches_select').html("<option>---</option>");
    $('#switch-ports-content').html('');
    $('#topology__elements__list').html('');

    // Hiding panels
    $('#switch-ports').hide();
    $('#trace-result-panel').hide();
    $('#topology__elements').hide();
    $('#topology__canvas').hide();

    // create the topology after loading the switches data
    var get_switches_callback = sdntopology.call_sdntrace_get_topology;

    // load switches data
    // Pass load topology function as a callback
    sdntopology.call_sdntrace_get_switches(get_switches_callback);
}

/* Initial load */
$(function() {
    // Configure toolbar handlers
    // Topology port labels handler
    $('#topology__toolbar__btn__label__link').click(function() {
        if ($(this).hasClass("active")) {
            $('.target-label').hide();
            $('.source-label').hide();
            d3.selectAll(".node_port").style("display", "none");
            d3.selectAll(".text_port").style("display", "none");
        } else {
            $('.target-label').show();
            $('.source-label').show();
            d3.selectAll(".node_port").style("display", "");
            d3.selectAll(".text_port").style("display", "");
        }
    });
    // Topology speed link labels handler
    $('#topology__toolbar__btn__label__speed').click(function() {
        if ($(this).hasClass("active")) {
            $('.speed-label').hide();
        } else {
            $('.speed-label').show();
        }
    });

    // Button to clear trace elements
    $('#topology__toolbar__btn__clear_trace').click(function() {
        // clear interface trace elements
        sdntrace.clear_trace_interface();

        // redraw the graph
        forcegraph.draw();
    });

    // Button to show topology color
    $('#topology__toolbar__btn__colors').click(function() {
        if ($(this).hasClass("active")) {
            forcegraph.restore_topology_colors();
        } else {
            forcegraph.show_topology_colors();
        }
    });



    // Initialize classes
    sdncolor = new SDNColor();

    sdntopology = new SDNTopology();

    // Initialize D3 Topology force graph
    d3lib = new D3JS();
    var selector = "#topology__canvas";
    var data = {
        nodes: [],
        links: []
    };
    forcegraph = new ForceGraph(selector,data);

    sdnflowtable = new SdnFlowTable();

    // initial data load (switch list, topology, colors)
    _initial_data_load();


});




