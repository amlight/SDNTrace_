
/* global Switch, DEBUG, d3, d3lib, MOCK */

/**
 * SDNColor utility to transform SDN color codes to CSS names.
 */
var SDNColor = function() {
    this.colors = {'1':'darkseagreen', '10':'dodgerblue', '11':'chocolate', '100':'darkorange', '101':'darkviolet', '110':'darkturquoise', '111':'black' };
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
     * @param {type} code binary color code
     * @returns {val} CSS color name
     */
    this.get_color = function(code) {
        var result = null;
        $.each( this.colors, function( key, val ) {
            if (key === code) {
                result = val;
            }
        });
        return result;
    };
};


var SDNTopology = function() {
    // switches list. It is used to help render the topology nodes.
    this.switches = [];
    // topology link list
    this.topology = [];
    // topology domains
    this.domains = [];
    
    var _self = this;

    // Map to optimize the topology connections verification by index.
    var _linkedByIndex = new Map();

    /**
     * Add two nodes as connections to the verification Map.
     * @param {type} nodeA Source node
     * @param {type} nodeB Target node
     */
    var addTopologyConnection = function(nodeA, nodeB) {
        _linkedByIndex.set(nodeA.id + "-" + nodeB.id, true);
    };
    
    /**
     * Verify if node A and node B are connected.
     * @param {type} nodeA
     * @param {type} nodeB
     * @returns {Boolean}
     */
    var isTopologyConnected = function(nodeA, nodeB) {
        return _linkedByIndex.has(nodeA.id + "-" + nodeB.id) ||
               _linkedByIndex.has(nodeB.id + "-" + nodeA.id) || 
               nodeA.id === nodeB.id;
    };

    /**
     * Call ajax to load the switch list.
     */
    this.callGetSwitches = function() {
        var ajaxDone = function(jsonObj) {
            for (var x = 0; x < jsonObj.length; x++) {
                // storing switch values
                var switchObj = new Switch(jsonObj[x].dpid);
                switchObj.n_ports = jsonObj[x].n_ports;
                switchObj.n_tables = jsonObj[x].n_tables;
                switchObj.name = jsonObj[x].switch_name;
                switchObj.switch_color = jsonObj[x].switch_color;
                switchObj.tcp_port = jsonObj[x].tcp_port;
                switchObj.openflow_version = jsonObj[x].openflow_version;
                switchObj.switch_vendor = jsonObj[x].switch_vendor;
                switchObj.ip_address = jsonObj[x].ip_address;
                //switch_obj.number_flows = jsonObj[x].number_flows;

                this.switches.push(switchObj);
            }
            // sort
            this.switches = this.switches.sort();
            // deduplication
            this.switches = arrayRemoveDuplicates(this.switches);
        };

        // AJAX call
        if (DEBUG) {
            json = MOCK.JSON_SWITCHES;
            var jsonobj = $.parseJSON(json);
            ajaxDone(jsonobj);
        } else {
            $.ajax({
                url:"/sdnlg/switches",
                dataType: 'json',
                crossdomain:true
            })
            .done(function(json) {
                ajaxDone(json);
            })
            .fail(function() {
                console.log( "call_get_switches ajax error" );
            })
            .always(function() {
                console.log( "call_get_switches ajax complete" );
            });
        }
    };

    this.callSdntraceGetSwitches = function(callback=null) {
        var ajaxDone = function(jsonObj, p_callback) {
            for (var x = 0; x < jsonObj.length; x++) {
                // storing switch values
                var switch_obj = new Switch(jsonObj[x]);
                _self.switches.push(switch_obj);

                var info_callback = null;
                // if is the last info retrieve, pass the callback to the call
                if (x === jsonObj.length - 1) {
                    info_callback = p_callback;
                }
                _self.callSdntraceGetSwitchInfo(jsonObj[x], info_callback);

                _self.callSdntraceGetSwitchFlows(jsonObj[x]);
            }

            // sort
            _self.switches = _self.switches.sort();
            // deduplication
            _self.switches = arrayRemoveDuplicates(_self.switches);

            if (callback !== null) {
                try {
                    //callback();
                } catch(err) {
                    console.log("Error callback function: " + callback);
                    throw err;
                }
            }
        };

        // AJAX call
        if (DEBUG) {
            json = MOCK.JSON_SDNTRACE_SWITCHES;
            var jsonobj = $.parseJSON(json);
            ajaxDone(jsonobj, callback);
        } else {
            $.ajax({
                url:"/sdntrace/switches",
                dataType: 'json',
                crossdomain:true
            })
            .done(function(json) {
                ajaxDone(json, callback);
            })
            .fail(function() {
                console.log( "callSdntraceGetSwitches ajax error" );
            })
            .always(function() {
                console.log( "callSdntraceGetSwitches ajax complete" );
            });
        }
    };

    this.callSdntraceGetSwitchInfo = function(p_dpid, callback=null) {
        var ajaxDone = function(jsonObj, p_callback) {
            var switch_obj = _self.get_node_by_id(p_dpid);

            switch_obj.n_ports = jsonObj.n_ports;
            switch_obj.n_tables = jsonObj.n_tables;

            switch_obj.name = jsonObj.switch_name;
            switch_obj.switch_color = jsonObj.switch_color;
            switch_obj.tcp_port = jsonObj.tcp_port;
            switch_obj.openflow_version = jsonObj.openflow_version;
            switch_obj.switch_vendor = jsonObj.switch_vendor;
            switch_obj.ip_address = jsonObj.ip_address;
            //switch_obj.number_flows = jsonObj.number_flows;

            _self.callSdntraceGetSwitchPorts(p_dpid, p_callback);

            if (p_callback !== null) {
                console.log('callSdntraceGetSwitchInfo callback');
                try {
                    //callback();
                } catch(err) {
                    console.log("Error callback function: " + callback);
                    throw err;
                }
            }
        };

        // AJAX call
        if (DEBUG) {
            json = MOCK.JSON_SDNTRACE_SWITCH_INFO;
            var jsonobj = $.parseJSON(json);
            ajaxDone(jsonobj, callback);
        } else {
            $.ajax({
                url:"/sdntrace/switches/" + p_dpid + "/info",
                dataType: 'json',
                crossdomain:true
            })
            .done(function(json) {
                ajaxDone(json, callback);
            })
            .fail(function() {
                console.log( "callSdntraceGetSwitchInfo ajax error" );
            })
            .always(function() {
                console.log( "callSdntraceGetSwitchInfo ajax complete" );
            });
        }
    };
    
    this.callSdntraceGetSwitchFlows = function(p_dpid, callback=null) {
        var ajax_done = function(jsonObj, p_callback) {
            var switch_obj = _self.get_node_by_id(p_dpid);

            switch_obj.number_flows = jsonObj.number_flows;

            switch_obj.flow_stat = {};
            switch_obj.flow_stat.dpid = p_dpid;
            switch_obj.flow_stat.flows = [];

            for(var x in jsonObj.flows) {
                var jsonFlow = jsonObj.flows[x];

                var flowObj = {};
                flowObj.idle_timeout = jsonFlow.idle_timeout;
                flowObj.cookie = jsonFlow.cookie;
                flowObj.priority = jsonFlow.priority;
                flowObj.hard_timeout = jsonFlow.hard_timeout;
                flowObj.byte_count = jsonFlow.byte_count;
                flowObj.duration_nsec = jsonFlow.duration_nsec;
                flowObj.packet_count= jsonFlow.packet_count;
                flowObj.duration_sec = jsonFlow.duration_sec;
                flowObj.table_id = jsonFlow.table_id;

                flowObj.actions = [];
                for(var y in jsonFlow.actions) {
                    var jsonAction = jsonFlow.actions[y];

                    var flowActionObj = {};
                    flowActionObj.max_len = jsonAction.max_len;
                    flowActionObj.type = jsonAction.type;
                    flowActionObj.port = jsonAction.port;
                    flowActionObj.vlan_vid = jsonAction.vlan_vid;
                    flowObj.actions.push(flowActionObj);
                }

                flowObj.match = {};
                flowObj.match.wildcards = jsonFlow.match.wildcards;
                flowObj.match.in_port = jsonFlow.match.in_port;
                flowObj.match.dl_vlan = jsonFlow.match.dl_vlan;
                flowObj.match.dl_src = jsonFlow.match.dl_src;
                flowObj.match.dl_dst = jsonFlow.match.dl_dst;
                flowObj.match.dl_type = jsonFlow.match.dl_type;

                switch_obj.flow_stat.flows.push(flowObj);
            }

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
                            pivot.action__vlan_vid = pivot.action__vlan_vid +"<br>"+ (jsonAction.vlan_vid || '--');
                        } else {
                            pivot.action__max_len = (jsonAction.max_len || '--');
                            pivot.action__type = (jsonAction.type || '--');
                            pivot.action__port = (jsonAction.port || '--');
                            pivot.action__vlan_vid = (jsonAction.vlan_vid || '--');
                        }
                    }
                }
                switch_obj.flow_pivot.push(pivot);
            }

            if (p_callback !== null) {
                console.log('callSdntraceGetSwitchFlows callback');
                try {
                    //callback();
                } catch(err) {
                    console.log("Error callback function: " + callback);
                    throw err;
                }
            }
        };

        // AJAX call
        if (DEBUG) {
            json = MOCK.JSON_FLOWS;
            var jsonobj = $.parseJSON(json);
            ajax_done(jsonobj, callback);
        } else {
            $.ajax({
                url:"/sdntrace/switches/" + p_dpid + "/flows",
                dataType: 'json',
                crossdomain:true
            })
            .done(function(json) {
                ajax_done(json, callback);
            })
            .fail(function() {
                console.log( "callSdntraceGetSwitchFlows ajax error" );
            })
            .always(function() {
                console.log( "callSdntraceGetSwitchFlows ajax complete" );
            });
        }
    };

    /**
     * Get node by id.
     * Returns Switch, Domain or Host
     * @param {type} p_id Node id
     * @returns {Node}
     */
    this.get_node_by_id = function(p_id) {
        // add to topology list to render the html
        for (var key in this.switches) {
            if (this.switches[key].id === p_id) {
                return this.switches[key];
            }
        }
        
        for (var key in this.domains) {
            if (this.domains[key].id === p_id) {
                return this.domains[key];
            }
        }
    };

   /**
    * Use this function instead of access the topology attribute.
    * @param {Link} link Link object
    */
    this.add_topology = function(link) {
        if (isTopologyConnected(link.node1, link.node2) === false) {
            addTopologyConnection(link.node1, link.node2);
            // add to topology list to render the html
            this.topology.push(link);
        }
    };

   /**
    * Use this function to get the topology link object.
    * Nodes parameters can be in any order.
    * 
    * @param {Node} node1 Node object
    * @param {Node} node2 Node object
    * @returns {Link} Link object
    */
    this.get_topology_link = function(node1, node2) {
        if (isTopologyConnected(node1, node2)) {
            for (var x in this.topology) {
                if ((this.topology[x].node1.id === node1.id && this.topology[x].node2.id === node2.id) ||
                   (this.topology[x].node1.id === node2.id && this.topology[x].node2.id === node1.id)) {

                    return this.topology[x];
                }
            }
        }
        return null;
    };

    /**
     * Call ajax to load the switch topology.
     * 
     * @param {function} callback Callback function
     */
    this.callSdntraceGetTopology = function(callback=null) {
        // hiding topology graphic panel
        $('#topology__canvas').hide();

        var ajaxDone = function(json) {
            var jsonObj = json;

            // verify if the json is not a '{}' response
            if (!jQuery.isEmptyObject(jsonObj)) {
                $.each( jsonObj, function( p_dpid1, p_node_a ) {
                    var dpid1 = p_dpid1;

                    $.each( p_node_a, function( p_port_id, p_neighbor ) {

                        var port1 = p_port_id;
                        if (p_neighbor.type === "link") {
                            var dpid2 = p_neighbor.neighbor_dpid;
                            var port2 = p_neighbor.neighbor_port;

                            var linkObj = new Link();

                            // creating switch
                            var _switch1 = _self.get_node_by_id(dpid1);
                            var _switch2 = _self.get_node_by_id(dpid2);

                            var switch1 = Switch.clone_obj(_switch1);
                            var switch2 = Switch.clone_obj(_switch2);

                            if(isTopologyConnected(switch1, switch2)) {
                                linkObj = _self.get_topology_link(switch1, switch2);
                            } else {
                                linkObj.node1 = switch1;
                                linkObj.node2 = switch2;

                                linkObj.node1.ports = [];
                                linkObj.node2.ports = [];
                            }
                            // creating switch ports from node1
                            var node1_port = _switch1.get_port_by_id(dpid1, port1);
                            if (node1_port === null) {
                                node1_port = new Port(dpid1, port1, port1, port1);
                                linkObj.node1.ports.push(node1_port);
                            } else {
                                linkObj.node1.ports.push(node1_port);
                            }
                            linkObj.label1 = node1_port.label;

                            // creating switch ports from node2
                            var node2_port = _switch2.get_port_by_id(dpid2, port2);
                            if (node2_port === null) {
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
                        } else if (p_neighbor.type === "host") {
                            // Add new host node
                            var _host_label = "";
                            if (typeof(p_neighbor.neighbor_name)!=='undefined') {
                                _host_label = p_neighbor.neighbor_name;
                            }

                            var linkObj = new Link();

                            // add node data do d3
                            var _switch1 = _self.get_node_by_id(dpid1);
                            var switch1 = Switch.clone_obj(_switch1);
                            linkObj.node1 = switch1;
                            linkObj.node1.ports = [];

                            // creating switch ports from node1
                            var node1_port = _switch1.get_port_by_id(dpid1, port1);
                            if (node1_port === null) {
                                node1_port = new Port(dpid1, port1, port1, port1);
                                linkObj.node1.ports.push(node1_port);
                            } else {
                                linkObj.node1.ports.push(node1_port);
                            }
                            linkObj.label1 = node1_port.label;

                            var host_obj = d3lib.addNewNodeHost(dpid1, port1, _host_label);

                            linkObj.node2 = host_obj;

                            // creating host ports
                            var port2 = p_neighbor.neighbor_port;
                            var node2_port = new Port(host_obj.id +'_'+ port2, port2, "");

                            linkObj.node2.ports = [node2_port];
                            linkObj.label_num2 = port2;
                        } else if (p_neighbor.type === "interdomain") {
                            // Add new host node
                            var _domain_label = "";
                            if (typeof(p_neighbor.domain_name)!=='undefined') {
                                _domain_label = p_neighbor.domain_name;
                            }

                            // add node data do d3
                            var linkObj = new Link();

                            var _switch1 = _self.get_node_by_id(dpid1);
                            var switch1 = Switch.clone_obj(_switch1);
                            linkObj.node1 = switch1;
                            linkObj.node1.ports = [];

                            // creating switch ports from node1
                            var node1_port = _switch1.get_port_by_id(dpid1, port1);
                            if (node1_port === null) {
                                node1_port = new Port(dpid1, port1, port1, port1);
                                linkObj.node1.ports.push(node1_port);
                            } else {
                                linkObj.node1.ports.push(node1_port);
                            }
                            linkObj.label1 = node1_port.label;

                            var domainObj = d3lib.addNewNodeDomain(_domain_label, _domain_label);
                            linkObj.node2 = domainObj;
                        }
                        // Add the node the the topology
                        if (linkObj) {
                            _self.add_topology(linkObj);
                        }
                    });
                });

                // render D3 force
                d3lib.render_topology();
                _self.showTopologyCanvas();
            }
        };

        // AJAX call
        if (DEBUG) {
            json = MOCK.JSON_TOPOLOGY_TRACE;
            var jsonobj = $.parseJSON(json);
            ajaxDone(jsonobj);
        } else {
            $.ajax({
                url: "/sdntrace/switches/topology",
                dataType: 'json'
            })
            .done(function(json) {
                ajaxDone(json);
            })
            .fail(function() {
                console.log( "call_get_topology ajax error" );
            })
            .always(function() {
                console.log( "call_get_topology ajax complete" );
            });
        }
    };

    /**
     * Call ajax to load the switch ports data.
     */
    this.callGetSwitchPorts = function(dpid, callback=null) {
        var ajaxDone = function(json) {
            var jsonObj = json;

            // verify if the json is not a '{}' response
            if (callback !== null && !jQuery.isEmptyObject(jsonObj)) {
                // render D3 popup
                try {
                    callback(dpid, jsonObj);
                }
                catch(err) {
                    console.log("Error callback function: " + callback);
                    throw err;
                }
            }
        };

        // AJAX call
        if (DEBUG) {
            json = MOCK.JSON_SWITCH_PORTS;
            var jsonobj = $.parseJSON(json);
            ajaxDone(jsonobj);
        } else {
            $.ajax({
                url: "/sdnlg/switches/" + dpid + "/ports",
                dataType: 'json'
            })
            .done(function(json) {
                ajaxDone(json);
            })
            .fail(function() {
                console.log( "callGetSwitchPorts ajax error" );
            })
            .always(function() {
                console.log( "callGetSwitchPorts ajax complete" );
            });
        }
    };

    /**
     * Call ajax to load the switch ports data.
     */
    this.callSdntraceGetSwitchPorts = function(p_dpid, callback=null) {
        var ajaxDone = function(json, p_callback) {
            var jsonObj= json;
            var switchObj = _self.get_node_by_id(p_dpid);

            if (switchObj) {
                $.each(jsonObj, function( key, p_port_data ) {
                    var portObj = switchObj.get_port_by_id(p_dpid, p_port_data.port_no);
                    if (portObj === null) {
                        portObj = new Port(p_dpid, p_port_data.port_no, p_port_data.port_no, p_port_data.name);

                        // create Port object and push to the switch ports
                        if (switchObj.ports === null) { switchObj.ports = []; }
                        switchObj.ports.push(portObj);
                    }
                    portObj.speed = p_port_data.speed;
                    portObj.label = p_port_data.name;
                    portObj.number = p_port_data.port_no;
                    portObj.status = p_port_data.status;
                });

                // verify if the json is not a '{}' response
                if (p_callback !== null && !jQuery.isEmptyObject(jsonObj)) {
                    // render D3 popup
                    try {
                        p_callback(p_dpid, jsonObj);
                    } catch(err) {
                        console.log("Error callback function: " + p_callback);
                        throw err;
                    }

                }
            }
        };

        // AJAX call
        if (DEBUG) {
            json = MOCK.JSON_SDNTRACE_SWITCH_PORTS;
            var jsonobj = $.parseJSON(json);
            ajaxDone(jsonobj, callback);
        } else {
            $.ajax({
                url: "/sdntrace/switches/" + p_dpid + "/ports",
                dataType: 'json'
            })
            .done(function(json) {
                ajaxDone(json, callback);
            })
            .fail(function() {
                console.log( "callSdntraceGetSwitchPorts ajax error" );
            })
            .always(function() {
                console.log( "callSdntraceGetSwitchPorts ajax complete" );
            });
        }
    };

    /**
     * Callback to be used with the AJAX that retrieve switch ports.
     * @param {type} nodeId Node Id that contains the ports
     * @param {type} jsonObj JSON object with port data
     */
    this._render_html_popup_ports = function(nodeId, jsonObj) {
        var popupSwitch = function(nodeId, data) {
            // remove possible popups
            d3.select(".canvas")
                .selectAll(".popup")
                .remove();

             // Build the popup
            var popup = d3.select(".canvas")
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
            // popup content Header
            popup.append("div")
                .attr("class","popup_header")
                .text(nodeId);
            popup.append("div")
                .attr("class","popup_header")
                .text("Interfaces (" + data.length + "):");
            // popup header separator
            popup.append("hr");
            // popup content
            var popupBody = popup
                .append("div")
                .attr("class","popup_body");
            var updatePopupBody = popupBody
                .selectAll("p")
                .data(data)
                .enter()
                    .append("p")
                        .append("a")
                            // adding click function
                            .on("click", function(d) {
                                popup.selectAll(".popup_body").remove();
                                var popup_body = popup.append("div").attr("class","popup_body");
                                popup_body.append("p").text("Port n.: " + d.port_no);
                                popup_body.append("p").text("Port name: " + d.name);
                                popup_body.append("p").text("Port speed: " + SDNTopology.formatSpeed(d.speed));
                                popup_body.append("p").text("Port uptime: " + d.uptime);
                                // adding back button
                                popup_body.append("p")
                                    .append("a")
                                    .text("back")
                                    .on("click", function() { popupSwitch(nodeId, data); });
                             })
                            .text(function(d) { return d.port_no + " - " + d.name; });
            updatePopupBody.exit();
        };
        
        popupSwitch(nodeId, jsonObj);
    };

    /**
     * Render HTML of the topology.
     */
    this.renderHtmlTopology = function() {
        if (this.topology) {
            $('#topology__canvas').show();
            $('#topology__elements').show();

            var htmlContent = "";
            htmlContent += "<div class='row'>";
            htmlContent += "<div class='col-sm-12 col-md-12'>";
            htmlContent += "<table id='switches_topology_table' class='table'><tbody>";

            for (var x = 0; x < this.topology.length; x++) {
                htmlContent += "<tr>";
                htmlContent += "<td>";

                // display nice switch name
                var tempSwitch = new Switch(this.topology[x].node1);
                htmlContent += tempSwitch.getNameOrId();

                // start left content, origin switch
                htmlContent += "</td><td>";
                htmlContent += "</td>";
                // end left content, origin switch

                htmlContent += "<td><span class='glyphicon glyphicon-arrow-right' aria-hidden='true'></span></td>";
                htmlContent += "<td>";

                // start right content, destination switch
                if (this.topology[x].node2) {
                    htmlContent += "<li>";
                    // display nice switch name
                    var tempSwitch = this.topology[x].node2;
                    htmlContent += tempSwitch.getNameOrId();
                    htmlContent += "</li>";
                    htmlContent += "</td><td>";
                } else {
                    htmlContent += "</td><td>";
                }
                htmlContent += "</td></tr>";
                // end right content, destination switch
            }
            htmlContent += "</tbody></table>";
            htmlContent += "</div>";

            $('#topology__elements__list').html(htmlContent);
        }
    };

    /**
     * Show the trace form to trigger the SDN Trace.
     * It has three forms, to L2, L3 and full trace.
     * We use modal forms over the layout.
     */
    this.showTraceForm = function(d) {
        // setting switch label
        $('#sdn_trace_form__switch-content').html(d.label + " - " + d.dpid);

        this.callSdntraceGetSwitchPorts(d.dpid, sdntrace.renderHtmlTraceFormPorts);

        // open modal dialog
        sdn_trace_form_dialog.dialog("open");
    };

    this.showTopologyCanvas = function() {
        $('#topology__canvas').show();
    };
};

/**
 * Format link speed.
 * @param {type} speed
 * @returns {String}
 */
SDNTopology.formatSpeed = function(speed) {
    if (speed % 1000000000 >= 0) {
        return (speed / 1000000000) + "GB";
    } else if (speed % 1000000 >= 0) {
        return (speed / 1000000) + "MB";
    } else if (speed % 1000 >= 0) {
        return (speed / 1000) + "KB";
    }
};
