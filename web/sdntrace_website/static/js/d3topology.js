
/* global sdntopology, forcegraph, sdnflowtable, d3, sdncolor, Port, Domain, Switch, Host */
/** @constant */
var SPEED_100GB = 100000000000;
/** @constant */
var SPEED_10GB = 10000000000;
/** @constant */
var SPEED_1GB = 1000000000;

/** @constant */
var SIZE = {'switch': 16,
            'domain': 3,
            'port': 8,
            'host': 16};

/** @constant */
var SIZE_PATH = {'switch': 700,
            'domain': 700,
            'port': 80,
            'host': 700};

/** @constant */
var DISTANCE = {'domain': 10 * SIZE['switch'],
                'switch': 10 * SIZE['switch'],
                'port': SIZE['switch'] + 16,
                'host': 10 * SIZE['switch']};


var ForceGraphContextMenu = function() {
    // Define contextual menu over the circles
    this.nodeContextMenu = function(data) {
        forcegraph.endHighlight();
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
                    return 'Name: ' + sw.getName();
                },
                disabled: true
            },
// TODO: Expecting new info services
//            {
//                title: 'Interfaces (' + data.data.n_ports + ')',
//                action: function(elm, d, i) {
//                    sdntopology.callGetSwitchPorts(d.dpid, sdntopology._render_html_popup_ports);
//                }
//            },
//            {
//                title: 'Total traffic: 000',
//                action: function() {}
//            },
            {

                title: 'Flows',
                action: function(elm, d, i) {
                    sdnflowtable.setSwitchFlowPanelData(d.data.dpid, d.data.flow_stat);
                    sdnflowtable.setData(d.data.dpid, d.data.flow_pivot);
                    sdnflowtable.dialogOpen();
                }
            },
            {
                title: 'Trace',
                action: function(elm, d, i) {
                    sdntopology.showTraceForm(d);
                }
            }
        ];
    };
    
    // Hide node context menu.
    this.hideContextMenu = function() {
        $('.d3-context-menu').hide();
    };
};


/**
 * This is the class that will create a D3 Forcegraph.
 * @param {type} p_selector HTML selector to create the SVG graph
 * @param {type} p_data Graph data
 * @returns {ForceGraph}
 */
var ForceGraph = function(p_selector, p_data) {
    
    var _self = this;
    
    // Local variable representing the forceGraph data
    var _data = p_data;

    var highlight_transparency = 0.1;
    // highlight var helpers
    var focus_node = null;

    var min_zoom = 0.1;
    var max_zoom = 7;

    // node/circle size
    var size = d3.scaleLinear()
      .domain([1,100])
      .range([8,24]);
    var nominal_base_node_size = 8;

    var _linkedByIndex = new Map();

    var addConnection = function(a, b) {
        /**
         a: source switch dpid
         b: target switch dpid
        */
        _linkedByIndex.set(a + "-" + b, true);
    };

    var isConnected = function(a, b) {
        return _linkedByIndex.has(a.id + "-" + b.id) || _linkedByIndex.has(b.id + "-" + a.id) || a.id === b.id;
    };
    
    
    // context menu manager
    var forceGraphContextMenu = new ForceGraphContextMenu();

    // zoom behavior
    var zoomed = function(d) {
        container.attr("transform", "translate(" + d3.event.transform.x + "," + d3.event.transform.y + ") scale(" + d3.event.transform.k + ")");
    };
    // zoom configuration
    var zoom = d3.zoom()
        .scaleExtent([min_zoom, max_zoom])
        .on("zoom", zoomed);

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

        return _data;
    };

    var collisionForce = d3.forceCollide(12)
        .strength(10)
        .iterations(20);

    var force = d3.forceSimulation()
        .force("link",
            d3.forceLink()
                .id(function(d) { return d.id; })
                .distance(function(d) {
                    if (d.edgetype === 's_p') {
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
        .selectAll("circle");
    // domain node
    container
        .append("g")
        .attr("class", "domains")
        .selectAll("rect");
    // draw switch label
    var text = container.append("g").selectAll("text");
    // draw link label
    var link_label = container.append("g").selectAll("text");


    /**
     * Node drag start event handler.
     * @param {type} d
     */
    var _nodeDragstarted = function (d) {
        // Prevent the Port node to be dragged.
        if (d.type === Port.TYPE) { return; }
        // Change the nodes alpha color to signal the user the drag event.
        if (!d3.event.active) { force.alphaTarget(0.3).restart(); }
        
        // if node context menu is open, close it.
        forceGraphContextMenu.hideContextMenu();
    };

    /**
     * Node drag event handler.
     * @param {type} d
     */
    var _nodeDragged = function (d) {
        // Prevent the Port node to be dragged.
        if (d.type === Port.TYPE) { return; }
        
        // Fix pin down X and Y coordinates.
        // Transform translate will not affect the position anymore.
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    };

    /**
     * Node drag end event handler.
     * @param {type} d
     */
    var _nodeDragended = function (d) {
        // Prevent the Port node to be dragged.
        if (d.type === Port.TYPE) { return; }
        // Reset the nodes alpha color
        if (!d3.event.active) force.alphaTarget(0);
        
        focus_node = null;
        _self.endHighlight(d);
    };

    /**
     * Start highlight node handler.
     * @param {type} d
     */
    var _startHighlight = function(d) {
        svg.style("cursor","pointer");
        if (focus_node !== null) {
            d = focus_node;
        }
        node.attr("fill", function(o) {
            return isConnected(d, o) ? sdncolor.NODE_COLOR_HIGHLIGHT[o.type] : sdncolor.NODE_COLOR[o.type];});
        text.style("font-weight", function(o) {
            return isConnected(d, o) ? "bold" : "normal";});
        path.style("stroke", function(o) {
            return o.source.index === d.index || o.target.index === d.index ? sdncolor.LINK_COLOR_HIGHLIGHT['switch'] : sdncolor.LINK_COLOR['switch'];
        });
    };

    /**
     * End highlight node handler.
     * @param {type} d
     * @returns {undefined}
     */
    this.endHighlight = function(d) {
        svg.style("cursor","move");
        node.attr("fill", function(o) { return o.background_color; })
            .style("opacity", 1);
            //.style(towhite, "white");
        path.style("opacity", 1)
            .style("stroke", function(o) { return sdncolor.LINK_COLOR[o.type]; });
        text.style("opacity", 1)
            .style("font-weight", "bold");
    };

    // Show topology colors for Switches that are used to Trace
    // It is just to identify the difference in color field
    this.show_topology_colors = function() {
        var nodes = d3.selectAll(".node");
        nodes.attr("fill", function(d) {
            if(d.type === Switch.TYPE) {
                for (var x in sdncolor.colors) {
                    if (x === d.data.switch_color) {
                        return sdncolor.colors[d.data.switch_color];
                    }
                }
            }
            return d.background_color;
        });
    };
    
    this.restore_topology_colors = function() {
        var nodes = d3.selectAll(".node");
        nodes.attr("fill", function(d) {
            return d.background_color;
        });
    };


    // focus highlight (on node mousedown)
    var setSwitchFocus = function(d) {
        // Set data info panel
        if(d && d.data) {
            $('#port_panel_info').hide();
            $('#switch_to_panel_info').hide();
            $('#switch_flows_panel').hide();
            $('#domain_panel_info').hide();

            _setSwitchFocusPanelData(d);
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
                return o.source.index === d.index || o.target.index === d.index ? 1 : highlight_transparency;
            });
        }
        // Set the focused node to the highlight color
        node.attr("fill", function(o) {
                return isConnected(d, o) ? sdncolor.NODE_COLOR_HIGHLIGHT[o.type] : sdncolor.NODE_COLOR[o.type];})
            .style("opacity", function(o) {
                return isConnected(d, o) ? 1 : highlight_transparency;
            });
    };

    // focus highlight (on node mousedown)
    var setPortFocus = function(d) {
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
            _setSwitchFocusPanelData(d.from_sw);
        }
    };

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
            _setDomainFocusPanelData(d);
            $('#domain_panel_info_collapse').collapse("show");
        }
    };

    /**
     * Focus and show to the lateral domain panel data.
     * Use with setSwitchFocus to set the lateral panel data
     * @param {type} d
     */
    var _setDomainFocusPanelData = function(d) {
        $('#domain_panel_info').show();
        $('#domain_panel_info_collapse').collapse("show");
        $('#domain_panel_info_dpid_value').html(d.data.domain);
        var name = d.data.getName();

        if (name && name.length > 0) {
            $('#domain_panel_info_name').show();
            $('#domain_panel_info_name_value').html(name);
        } else {
            $('#domain_panel_info_name').hide();
        }
    };

    /**
     * Focus and show to the lateral switch panel data.
     * Use with set_switch_focus to set the lateral panel data
     * @param {type} d
     * @returns {undefined}
     */
    var _setSwitchFocusPanelData = function(d) {
        // display panel
        $('#switch_panel_info').show();
        // animation to open panel
        $('#switch_panel_info_collapse').collapse("show");
        // fill html content
        $('#switch_panel_info_dpid_value').html(d.data.dpid);
        var name = d.data.getName();
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
                sdnflowtable.setSwitchFlowPanelData(d.data.dpid, d.data.flow_stat);
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
    };

    /**
     * Function to calculate the radius position from point C to point D.
     * 
     * @param {type} cx
     * @param {type} cy
     * @param {type} dx
     * @param {type} dy
     * @returns {Array}
     */
    var radiusPositioning = function(cx, cy, dx, dy) {
        var delta_x = dx - cx;
        var delta_y = dy - cy;
        var rad = Math.atan2(delta_y, delta_x);
        var new_x = cx + Math.cos(rad) * DISTANCE['port'];
        var new_y = cy + Math.sin(rad) * DISTANCE['port'];

        return [new_x, new_y];
    };

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
        var return_val = '';
        if (d.type === Port.TYPE) {
            var new_positions = radiusPositioning(d.from_sw.x, d.from_sw.y, d.to_sw.x, d.to_sw.y);
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
        if (d.type === Port.TYPE) {
            var new_positions = radiusPositioning(d.from_sw.x, d.from_sw.y, d.to_sw.x, d.to_sw.y);
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
        var new_positions = radiusPositioning(d.source.x, d.source.y, d.target.x, d.target.y);
        var dx = new_positions[0] - SIZE['port'];
        var dy = new_positions[1] + SIZE['port']/2.0;
        return "translate(" + dx + "," + dy + ")";
    }
    function transformLinkTargetLabel(d) {
        var new_positions = radiusPositioning(d.target.x, d.target.y, d.source.x, d.source.y);
        var dx = new_positions[0];
        var dy = new_positions[1];
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
                        if (d.edgetype === 's_p') {
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
                        if (d.type === Domain.TYPE) { return d3.symbolWye; }
                        else if (d.type === Host.TYPE) { return d3.symbolSquare; }
                        return d3.symbolCircle;
                    })
                    .size(function(d) { return (SIZE_PATH[d.type]); }))
                .attr("id", function(d) { return "node-" + d.id; })
                .attr("r", function(d) { return SIZE[d.type]||nominal_base_node_size; })
                .attr("fill", function(d) { return d.background_color; })
                .attr("class", function(d) {
                    if (d.type === Port.TYPE) { return " node node_port"; }
                    return "node";
                })
                .style("display", function(d) {
                    if (d.type === Port.TYPE) { return "none"; }
                    return "";
                })
                .on('contextmenu', d3.contextMenu(forceGraphContextMenu.nodeContextMenu)) // attach menu to element
                .on("mouseover", function(d) {
                    if (d.type === Port.TYPE) { return; }
                    if (d.type === Switch.TYPE) { _startHighlight(d); }
                })
                .on("mousedown", function(d) {
                    d3.event.stopPropagation();

                    if (d.type === Port.TYPE) {
                        setPortFocus(d);
                    } else if (d.type === Switch.TYPE) {
                        // focus_node to control highlight events
                        focus_node = d;
                        setSwitchFocus(d);
                    } else if (d.type === Domain.TYPE) {
                        // focus_node to control highlight events
                        focus_node = d;
                        set_domain_focus(d);
                    };
                })
                .on("mouseout", function(d) {
                    if (d.type === Port.TYPE) { return; }
                    if (focus_node === null) { _self.endHighlight(d); }
                })
                .on("click", function(d) {
                    if (d.type === Port.TYPE) { return; }
                    focus_node = null;
                    _self.endHighlight(d);
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
                        if (d.type === Port.TYPE) { return "node_text text_port"; }
                        return "node_text";
                    })
                    .attr("x", 0)
                    .attr("y", ".1em")
                    .style("display", function(d) {
                        if (d.type === Port.TYPE) { return "none"; }
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
    };
};


/**
 * Class to intermediate the communication between D3 library and other scripts.
 * It manages the data related to nodes and edges and prepare all data to 
 * be sendo forward to the D3 lib.
 * 
 * @returns {D3JS}
 */
var D3JS = function() {
    var _self = this;
    
    this.nodes = null;
    this.edges = null;

    this.findNode = function(p_id) {
        var id = '';
        // Check if the p_id is an object or the real ID attribute
        if ( typeof p_id.id === 'undefined') {
            id = p_id;
        } else {
            id = p_id.id;
        }

        // looking for existing node.
        for (var k in this.nodes){
            if (this.nodes.hasOwnProperty(k) && this.nodes[k] && this.nodes[k].id === id) {
                 return this.nodes[k];
            }
        }
        return null;
    };

    this.hasNode = function(p_id) {
        var findNodeObj = this.findNode(p_id);
        if (findNodeObj === null) {
            return false;
        } else {
            return true;
        }
    };

    this.removeNode = function(id) {
        // Delete the node from the array
        for (var k in this.nodes){
            if (this.nodes.hasOwnProperty(k) && this.nodes[k] && this.nodes[k].id === id) {
                 this.nodes.splice(k, 1);
            }
        }
        // Delete the edges related to the deleted node
        for (var k in this.edges){
            if (this.edges.hasOwnProperty(k) && this.edges[k]) {
                if (this.edges[k].source.id === id || this.edges[k].target.id === id)
                 this.edges.splice(k, 1);
            }
        }
        return null;
    };
    
    
    this.addNewNodeHost = function(p_dpid, p_port_id, p_label="") {
        if (this.nodes) {
            var _host_id = Host.createId(p_dpid, p_port_id);
            for (var y = 0; y < this.nodes.length; y++) {
                if(this.nodes[y].id === _host_id) {
                    // do nothing
                    return this.nodes[y];
                }
            }
        } else {
            this.nodes = [];
        }

        var host_id = Host.createId(p_dpid, p_port_id);
        var host_obj = new Host(host_id, p_label);

        sdntopology.domains.push(host_obj);

        if (this.nodes) {

            // create an array with nodes
            _createNetworkNodes(false, false, true);

            var data = forcegraph.data();
            data.nodes = this.nodes;

            // Draw the d3js graph
            forcegraph.draw();
        }

        return host_obj;
    };

    this.addNewNodeDomain = function(id=null, label="") {
        var domain_id = Domain.createId(id);

        if(this.nodes) {
            for (var y = 0; y < this.nodes.length; y++) {
                if(this.nodes[y].id === domain_id) {
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
        _createNetworkNodes(false, false, true);

        var data = forcegraph.data();
        data.nodes = this.nodes;

        // Draw the d3js graph
        forcegraph.draw();

        return domain_obj;
    };

    this.addNewLink = function(id_from, id_to, label="") {

        var node_from = sdntopology.get_node_by_id(id_from);
        var node_to = sdntopology.get_node_by_id(id_to);

        var _link = sdntopology.get_topology_link(node_from, node_to);
        if (_link === null) {
            _link = {node1: node_from , node2:node_to, label1:label, label2:label, speed:""};

            sdntopology.add_topology(_link);

            // create an array with edges
            _createNetworkEdges(false, false, true);

            var data = forcegraph.data();
            data.links = this.edges;
            data.edges_data = this.edges;

            // Draw the d3js graph
            forcegraph.draw();
        }
    };

    this.addNewNode = function(p_dpid=null, p_label="", p_domain=null) {
        var _hasSwitch = function(p_id) {
            for(var x in sdntopology.switches) {
                if(sdntopology.switches[x].id === p_id) {
                    return true;
                }
            }
            return false;
        };
        var with_colors = typeof with_colors !== 'undefined' ? with_colors : true;
        var with_trace = typeof with_trace !== 'undefined' ? with_trace : true;

        var _dpid = "";
        if (p_dpid) {
            _dpid = p_dpid;
        }

        if (_hasSwitch(_dpid)) {
            return;
        }

        var _switch_obj = new Switch(_dpid);
        if (p_label) { _switch_obj.name = p_label; }
        if (p_domain) { _switch_obj.domain = p_domain; }

        sdntopology.switches.push(_switch_obj);

        // create an array with nodes
        _createNetworkNodes(with_colors, with_trace, true);

        var data = forcegraph.data();
        data.nodes = this.nodes;

        forcegraph.draw();
    };

    this.resetAllNodes = function() {
        if (this.nodes) {
            this.nodes = [];
        }
        if (this.edges) {
            this.edges = [];
        }
    };

    /**
     * Create D3JS network nodes.
     * We use the sdntopology.switch list to create the nodes and expect that the topology will have the same
     * node identification to draw the network edges.
     * @param {type} with_colors
     * @param {type} with_trace
     * @param {type} p_updateCurrent Flag to signal to update the internal node data.
     */
    var _createNetworkNodes = function(with_colors, with_trace, p_updateCurrent=false) {
        // create an array with nodes
        var nodesArray = [];
        for (var x = 0; x < sdntopology.switches.length; x++) {
            // positioning in spiral mode to help the physics animation and prevent crossing lines
            var nodeObj = sdntopology.switches[x].getD3jsData();

            if (p_updateCurrent) {
                for (var y = 0; y < _self.nodes.length; y++) {
                    if (_self.nodes[y].id === nodeObj.id) {
                        nodeObj = _self.nodes[y];
                    }
                }
            }

            nodesArray.push(nodeObj);
        }
        for (var x = 0; x < sdntopology.domains.length; x++) {
            // positioning in spiral mode to help the physics animation and prevent crossing lines
            var nodeObj = sdntopology.domains[x].getD3jsData();

            if (p_updateCurrent) {
                for (var y = 0; y < _self.nodes.length; y++) {
                    if (_self.nodes[y].id === nodeObj.id) {
                        nodeObj = _self.nodes[y];
                    }
                }
            }
            nodesArray.push(nodeObj);
        }
        _self.nodes = nodesArray;
    };

    /**
     * Create D3JS network edges.
     * This function can be used to create the topology, topology with color and
     * topology with tracing.
     * @param {type} with_colors
     * @param {type} with_trace
     * @param {type} p_updateCurrent Flag to signal to update the internal node data.
     * @returns {undefined}
     */
    var _createNetworkEdges = function(with_colors, with_trace, p_updateCurrent=false) {
        var edgesArray = [];

        // verify topology to create edges
        for (var x = 0; x < sdntopology.topology.length; x++) {
            var nodeFromId = sdntopology.topology[x].node1;
            var nodeToId = sdntopology.topology[x].node2;

            var labelFrom = sdntopology.topology[x].label1;
            var labelTo = sdntopology.topology[x].label2;

            var labelNumberFrom = sdntopology.topology[x].label_num1;
            var labelNumberTo = sdntopology.topology[x].label_num2;

            var speed = sdntopology.topology[x].speed;

            var source = _self.findNode(nodeFromId) || _self.nodes.push({id:nodeFromId, dpid:nodeFromId, name: nodeFromId});
            var target = _self.findNode(nodeToId) || _self.nodes.push({id:nodeToId, dpid:nodeToId, name: nodeToId});

            var edgeId = source.id + "-" + target.id;
            var sourceLabel = {name: labelFrom, num: labelNumberFrom};
            var targetLabel = {name: labelTo, num: labelNumberTo};

            var edgeObj = {id:edgeId, name:x, source: source, target: target, source_label:sourceLabel, target_label:targetLabel, speed:speed};
            edgeObj.color = sdncolor.LINK_COLOR['switch'];

            // Update current link instead of creating a new one
            if (p_updateCurrent) {
                for (var y = 0; y < _self.edges.length; y++) {
                    if (_self.edges[y].id === edgeObj.id) {
                        edgeObj = _self.edges[y];
                    }
                }
            }

            edgesArray.push(edgeObj);

            // adding port as a node
            var node_port_obj_from = null;
            var node_port_obj_to = null;
            if (nodeFromId.ports && nodeFromId.ports.length > 0 && nodeFromId.ports[0]) {
                node_port_obj_from = nodeFromId.ports[0].getD3jsData();
                node_port_obj_from.from_sw = source;
                node_port_obj_from.to_sw = target;

                if(!_self.hasNode(node_port_obj_from.id)) {
                    _self.nodes.push(node_port_obj_from);
                }
            }

            if (nodeToId.ports && nodeToId.ports.length > 0 && nodeToId.ports[0]) {
                node_port_obj_to = nodeToId.ports[0].getD3jsData();
                node_port_obj_to.from_sw = target;
                node_port_obj_to.to_sw = source;

                if(!_self.hasNode(node_port_obj_to.id)) {
                    _self.nodes.push(node_port_obj_to);
                }
            }
        }

        _self.edges = edgesArray;
    };

    var _renderNetwork = function(with_colors, with_trace) {
        with_colors = typeof with_colors !== 'undefined' ? with_colors : true;
        with_trace = typeof with_trace !== 'undefined' ? with_trace : true;

        // create an array with nodes
        _createNetworkNodes(with_colors, with_trace);

        // create an array with edges
        _createNetworkEdges(with_colors, with_trace);

        var data = {
            nodes: _self.nodes,
            links: _self.edges,
            edges_data: _self.edges
        };

        // creating Force Graph nodes
        // Set the new data
        forcegraph.data(data);
        // Create the graph object
        // Having myGraph in the global scope makes it easier to call it from a json function or anywhere in the code (even other js files).
        forcegraph.draw();
        // Draw the graph for the first time
    };

    /**
     * Render topology using topology data saved in sdntopology object.
     * It uses the vis.js graph library.
     * You must load the sdntopology switch and topology data before trying to render the topology.
     */
    this.render_topology = function() {
        _renderNetwork(false, false);
    };
    
};



