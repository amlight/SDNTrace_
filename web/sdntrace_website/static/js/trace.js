// Mock json trace
var MOCK_JSON_TRACE = '80001';
var MOCK_JSON_TRACE_RESULT = '{"total_time": "0:00:03.520170","start_time": "2017-03-21 13:30:42.024902",'+
    '"result": ['+
    '{"time": "2017-03-21 13:30:42.024902","type": "starting","port": "s1-eth1","dpid": "0000000000000001"},'+
    '{"time": "0:00:00.510086","type": "trace","port": "s2-eth2","dpid": "0000000000000002"},'+
    '{"time": "0:00:01.012277","type": "trace","port": "s3-eth2","dpid": "0000000000000003"},'+
    '{"time": "0:00:01.514501","type": "trace","port": "s4-eth2","dpid": "0000000000000004"},'+
    '{"msg": null,"reason": "done","type": "last","time": "0:00:03.519943"}],'+
    '"request_id": 80001}';

var MOCK_JSON_TRACE_RESULT = '{"total_time": "0:00:03.520170","start_time": "2017-03-21 13:30:42.024902",'+
    '"result": ['+
    '{"time": "2017-03-21 13:30:42.024902","type": "starting","port": "s1-eth1","dpid": "0000000000000001"},'+
    '{"time": "0:00:00.510086","type": "trace","port": "s2-eth2","dpid": "0000000000000002"},'+
    '{"time": "0:00:01.012277","type": "trace","port": "s3-eth2","dpid": "0000000000000003"},'+
    '{"time": "0:00:01.514501","type": "trace","port": "s4-eth2","dpid": "0000000000000004"},'+
    '{"msg": null,"reason": "done","type": "last","time": "0:00:03.519943"}],'+
    '"request_id": 80001}';

var MOCK_JSON_TRACE_RESULT_INTERDOMAIN = '{"total_time": "0:00:05.019943","start_time": "2017-03-21 13:30:42.024902",'+
    '"result": ['+
    '{"time": "2017-03-21 13:30:42.024902","type": "starting","port": "s1-eth1","dpid": "0000000000000001"},'+
    '{"time": "0:00:00.510086","type": "trace","port": "s2-eth2","dpid": "0000000000000002"},'+
    '{"time": "0:00:01.012277","type": "trace","port": "s3-eth2","dpid": "0000000000000003"},'+
    '{"time": "0:00:02.514501","type": "intertrace", "domain":"Domain B"},'+
    '{"time": "0:00:04.014501","type": "intertrace", "domain":"Domain C"},'+
    '{"time": "0:00:04.514501","type": "trace","port": "s8-eth1","dpid": "0000000000000101"},'+
    '{"msg": null,"reason": "done","type": "last","time": "0:00:05.019943"}],'+
    '"request_id": 80001}';

var MOCK_JSON_TRACE_RESULT_PART1 = '{"total_time": "0:00:00","start_time": "2017-03-21 13:30:42.024902",'+
    '"result": ['+
    '{"time": "2017-03-21 13:30:42.024902","type": "starting","port": "s1-eth1","dpid": "0000000000000001"}],'+
    '"request_id": 80001}';

var MOCK_JSON_TRACE_RESULT_PART2 = '{"total_time": "0:00.510086","start_time": "2017-03-21 13:30:42.024902",'+
    '"result": ['+
    '{"time": "2017-03-21 13:30:42.024902","type": "starting","port": "s1-eth1","dpid": "0000000000000001"},'+
    '{"time": "0:00:00.510086","type": "trace","port": "s2-eth2","dpid": "0000000000000002"}],'+
    '"request_id": 80001}';

var MOCK_JSON_TRACE_RESULT_PART3 = '{"total_time": "0:00:01.514501","start_time": "2017-03-21 13:30:42.024902",'+
    '"result": ['+
    '{"time": "2017-03-21 13:30:42.024902","type": "starting","port": "s1-eth1","dpid": "0000000000000001"},'+
    '{"time": "0:00:00.510086","type": "trace","port": "s2-eth2","dpid": "0000000000000002"},'+
    '{"time": "0:00:01.012277","type": "trace","port": "s3-eth2","dpid": "0000000000000003"},'+
    '{"time": "0:00:01.514501","type": "trace","port": "s4-eth2","dpid": "0000000000000004"}],'+
    '"request_id": 80001}';

var MOCK_JSON_TRACE_RESULT_PART4 = '{"total_time": "0:00:03.520170","start_time": "2017-03-21 13:30:42.024902",'+
    '"result": ['+
    '{"time": "2017-03-21 13:30:42.024902","type": "starting","port": "s1-eth1","dpid": "0000000000000001"},'+
    '{"time": "0:00:00.510086","type": "trace","port": "s2-eth2","dpid": "0000000000000002"},'+
    '{"time": "0:00:01.012277","type": "trace","port": "s3-eth2","dpid": "0000000000000003"},'+
    '{"time": "0:00:01.514501","type": "trace","port": "s4-eth2","dpid": "0000000000000004"},'+
    '{"msg": null,"reason": "done","type": "last","time": "0:00:03.519943"}],'+
    '"request_id": 80001}';
var MOCK_JSON_TRACE_RESULT_PART4_ERROR = '{"total_time": "0:00:03.520170","start_time": "2017-03-21 13:30:42.024902",'+
    '"result": ['+
    '{"time": "2017-03-21 13:30:42.024902","type": "starting","port": "s1-eth1","dpid": "0000000000000001"},'+
    '{"time": "0:00:00.510086","type": "trace","port": "s2-eth2","dpid": "0000000000000002"},'+
    '{"time": "0:00:01.012277","type": "trace","port": "s3-eth2","dpid": "0000000000000003"},'+
    '{"time": "0:00:01.514501","type": "trace","port": "s4-eth2","dpid": "0000000000000004"},'+
    '{"msg": "Unknown error","reason": "error","type": "last","time": "0:00:03.519943"}],'+
    '"request_id": 80001}';
var MOCK_JSON_TRACE_RESULT_PART4_LOOP = '{"total_time": "0:00:03.520170","start_time": "2017-03-21 13:30:42.024902",'+
    '"result": ['+
    '{"time": "2017-03-21 13:30:42.024902","type": "starting","port": "s1-eth1","dpid": "0000000000000001"},'+
    '{"time": "0:00:00.510086","type": "trace","port": "s2-eth2","dpid": "0000000000000002"},'+
    '{"time": "0:00:01.012277","type": "trace","port": "s3-eth2","dpid": "0000000000000003"},'+
    '{"time": "0:00:01.514501","type": "trace","port": "s4-eth2","dpid": "0000000000000004"},'+
    '{"msg": null,"reason": "loop","type": "last","time": "0:00:03.519943"}],'+
    '"request_id": 80001}';

// reference to the trace form dialog
var sdn_trace_form_dialog = '';

var sdntrace = '';

var SDNTrace = function() {

    var REST_TRACE_TYPE = {'STARTING':'starting', 'LAST':'last', 'TRACE':'trace', 'INTERTRACE':'intertrace'};
    var REST_TRACE_REASON = {'ERROR':'error', 'DONE':'done', 'LOOP':'loop'}


    // last trace id executing
    this.last_trace_id = "";

    this.clear_trace_interface = function() {
        /**
        * Clear trace forms, result, result pannel, dialog modal, graph highlight, graph trace
        */
        $('#trace-result-content').html('');
        $('#trace_panel_info .loading-icon-div').hide();

        // clear d3 graph highlight nodes, links
        forcegraph.exit_highlight();

        // clear d3 graph trace classes
        $("path").removeClass("node-trace-active");
        $("line").removeClass("link-trace-active");
        $("path").each(function() {
            if ($(this).attr("data-nodeid")) {
            }
        });

        // close modal trace form
        sdn_trace_form_dialog.dialog( "close" );

        $('#trace_panel_info').hide();
    }

    this.call_trace_request_id = function(json_data) {
        /**
         * Call ajax to trace.
         * Param:
         *    json_data: Data in json String format to send as PUT method.
         */
        sdntrace.clear_trace_interface();

        var ajax_done = function(json) {
            // Stopping any ongoing trace.
            sdntrace.trace_stop();
            sdntrace.trace_reset();

            // Trigger AJAX to retrieve the trace result
            sdntrace.trigger_trace_listener(json);
        }

        // show loading icon
        $('#trace_panel_info .loading-icon-div').show();

        // AJAX call
        if (DEBUG) {
            json = MOCK_JSON_TRACE;
            var jsonobj = $.parseJSON(json);
            ajax_done(jsonobj);
        } else {
            var jqxhr = $.ajax({
                url: SDNLG_CONF.trace_server + "/sdntrace/trace",
                type: 'PUT',
                dataType: 'json',
                data: json_data
            }).done(function(json) {
                ajax_done(json);
            })
            .fail(function(responseObj) {
                if (responseObj.responseJSON) {
                    $('#trace-result-content').html("<div class='bg-danger'>"+responseObj.responseJSON.error+"</div>");
                } else {
                    $('#trace-result-content').html("<div class='bg-danger'>Trace error.</div>");
                }
                sdntrace.trace_stop();
            })
            .always(function() {
                $('#trace_panel_info').show();
            });
        }
    }

    this._render_html_trace_form_ports = function(dpid, port_data) {
        /**
        Callback to be used with the AJAX that retrieve switch ports.
        */
        $('#sdn_trace_form__switch-hidden').val(dpid);
        $('#sdn_trace_form__switch-port-hidden').val('');
        $('#sdn_trace_form__switch-ports-content select').html('');

        $('#sdn_trace_form__switch-ports-content select').change(function() {
            $('#sdn_trace_form__switch-port-hidden').val(this.value);
        });

        $.each(port_data, function(index, value){
            $('<option/>', {
                'value': this.port_no,
                'text': this.port_no + " - " + this.name
            }).appendTo('#sdn_trace_form__switch-ports-content select');

            if (index == 1) {
                // insert port
                $('#sdn_trace_form__switch-port-hidden').val(this.port_no);
            }
        });
    }


    /**
     * Build json string from form fields to send to trace layer 2 ajax.
     */
    this._build_trace_layer2_json = function() {
        var layer2 = new Object();
        layer2.trace = new Object();

        layer2.trace.switch = new Object();
        layer2.trace.switch.dpid = $('#sdn_trace_form__switch-hidden').val();
        layer2.trace.switch.in_port = $('#sdn_trace_form__switch-port-hidden').val();
        if (layer2.trace.switch.in_port) {
            layer2.trace.switch.in_port = parseInt(layer2.trace.switch.in_port, 10);
        }

        layer2.trace.eth = new Object();
        layer2.trace.eth.dl_src = $('#l2_dl_src').val();
        layer2.trace.eth.dl_dst = $('#l2_dl_dst').val();
        layer2.trace.eth.dl_vlan = $('#l2_dl_vlan').val();
        if (layer2.trace.eth.dl_vlan) {
            layer2.trace.eth.dl_vlan = parseInt(layer2.trace.eth.dl_vlan, 10);
        }
        layer2.trace.eth.dl_type = $('#l2_dl_type').val();
        if (layer2.trace.eth.dl_type) {
            layer2.trace.eth.dl_type = parseInt(layer2.trace.eth.dl_type, 10);
        }

        layer2 = sdntrace._remove_empty_json_values(layer2);
        var layer2String = JSON.stringify(layer2);

        return layer2String;
    }

    /**
     * Build json string from form fields to send to trace layer 3 ajax.
     */
    this._build_trace_layer3_json = function() {
        var layer3 = new Object();
        layer3.trace = new Object();

        layer3.trace.switch = new Object();
        layer3.trace.switch.dpid = $('#sdn_trace_form__switch-hidden').val();
        layer3.trace.switch.in_port = $('#sdn_trace_form__switch-port-hidden').val();
        if (layer3.trace.switch.in_port) {
            layer3.trace.switch.in_port = parseInt(layer3.trace.switch.in_port, 10);
        }

        layer3.trace.eth = new Object();
        layer3.trace.eth.dl_vlan = $('#l3_dl_vlan').val();
        if (layer3.trace.eth.dl_vlan) {
            layer3.trace.eth.dl_vlan = parseInt(layer3.trace.eth.dl_vlan, 10);
        }

        layer3.trace.ip = new Object();
        layer3.trace.ip.nw_src = $('#l3_nw_src').val();
        layer3.trace.ip.nw_dst = $('#l3_nw_dst').val();
        layer3.trace.ip.nw_tos = $('#l3_nw_tos').val();
        if (layer3.trace.ip.nw_tos) {
            layer3.trace.ip.nw_tos = parseInt(layer3.trace.ip.nw_tos, 10);
        }

        layer3.trace.tp = new Object();
        layer3.trace.tp.tp_src = $('#l3_tp_src').val();
        layer3.trace.tp.tp_dst = $('#l3_tp_dst').val();
        if (layer3.trace.tp.tp_dst) {
            layer3.trace.tp.tp_dst = parseInt(layer3.trace.tp.tp_dst, 10);
        }
        layer3 = sdntrace._remove_empty_json_values(layer3);
        var layer3String = JSON.stringify(layer3);

        return layer3String;
    }

    /**
     * Build json string from form fields to send to full trace ajax.
     */
    this._build_trace_layerfull_json = function() {
        var layerfull = new Object();
        layerfull.trace = new Object();

        layerfull.trace.switch = new Object();
        layerfull.trace.switch.dpid = $('#sdn_trace_form__switch-hidden').val();
        layerfull.trace.switch.in_port = $('#sdn_trace_form__switch-port-hidden').val();
        if (layerfull.trace.switch.in_port) {
            layerfull.trace.switch.in_port = parseInt(layerfull.trace.switch.in_port, 10);
        }

        layerfull.trace.eth = new Object();
        layerfull.trace.eth.dl_src = $('#lf_dl_src').val();
        layerfull.trace.eth.dl_dst = $('#lf_dl_dst').val();
        layerfull.trace.eth.dl_vlan = $('#lf_dl_vlan').val();
        if (layerfull.trace.eth.dl_vlan) {
            layerfull.trace.eth.dl_vlan = parseInt(layerfull.trace.eth.dl_vlan, 10);
        }

        layerfull.trace.eth.dl_type = $('#lf_dl_type').val();
        if (layerfull.trace.eth.dl_type) {
            layerfull.trace.eth.dl_type = parseInt(layerfull.trace.eth.dl_type, 10);
        }

        layerfull.trace.ip = new Object();
        layerfull.trace.ip.nw_src = $('#lf_nw_src').val();
        layerfull.trace.ip.nw_dst = $('#lf_nw_dst').val();
        layerfull.trace.ip.nw_tos = $('#lf_nw_tos').val();
        if (layerfull.trace.ip.nw_tos) {
            layerfull.trace.ip.nw_tos = parseInt(layerfull.trace.ip.nw_tos, 10);
        }
        layerfull.trace.tp = new Object();
        layerfull.trace.tp.tp_src = $('#lf_tp_src').val();
        layerfull.trace.tp.tp_dst = $('#lf_tp_dst').val();
        if (layerfull.trace.tp.tp_dst) {
            layerfull.trace.tp.tp_dst = parseInt(layerfull.trace.tp.tp_dst, 10);
        }

        layerfull = sdntrace._remove_empty_json_values(layerfull);
        var layerfullString = JSON.stringify(layerfull);

        return layerfullString;
    }
    /**
     * Helper function to remove attributes with empty values from a json object.
     */
    this._remove_empty_json_values = function(obj) {
        for (var i in obj) {
            for (var j in obj[i]) {
                for (var w in obj[i][j]) {
                    if (obj[i][j][w] === null || obj[i][j][w] == '') {
                        delete obj[i][j][w];
                    }
                }
                if (jQuery.isEmptyObject(obj[i][j])) {
                    delete obj[i][j];
                }
            }
            if (jQuery.isEmptyObject(obj[i])) {
                delete obj[i];
            }
        }
        return obj;
    }


    // Timeout flag to stop the trace listener
    var _thread_trace_listener = "";
    // Time to trigger the next call in ms
    var _trace_timer_trigger_call = 1000;
    // Total time to trigger the call. After that trigger timeout method.
    var _trace_timer_max = 30000;

    var _trace_timer_counter = 0;

    this.trigger_trace_listener = function(trace_id) {
        sdntrace.last_trace_id = trace_id;

        // show load icon
        $('#trace_panel_info .loading-icon-div').show();

        // Clearing the trace panel
        $('#trace-result-content').html("");
        $('#trace_panel_info_collapse').collapse("hide");

        // Call to AJAX to retrieve the trace result
        this.call_trace_listener(trace_id);
    }

    // Reset all variables to start the trace
    this.trace_reset = function() {
        clearTimeout(_thread_trace_listener);
        _thread_trace_listener = "";
        _trace_timer_counter = 0;
        sdntrace._flag_call_trace_listener_again = true;
    }
    // Stop trace thread and block all variables.
    this.trace_stop = function() {
        console.log('TRACE STOP');

        clearTimeout(_thread_trace_listener);

        _thread_trace_listener = "";
        _trace_timer_counter = 100000;
        sdntrace._flag_call_trace_listener_again = false;

        // hide loading icon
        $('#trace_panel_info .loading-icon-div').hide();
    }

    var debug_trace_trigger_counter = 10;
    var debug_timeout_trace_trigger_counter = 0;

    this._flag_call_trace_listener_again = true;
    this._flag_call_trace_listener_again_counter = 0;

    this.call_trace_listener = function(trace_id) {
        var html_render = function(jsonObj) {
            /**
            * Render trace result html info.
            */
            html_content = ""
            html_content += "<div class='row'>";
            html_content += "<div class='col-sm-4'>";
            html_content += "<strong>Start from:</strong>";
            html_content += "</div>";
            if(jsonObj.result) {
                // FIXME workaround for multiple starting type
                var _flag_multiple_starting_counter = 0;
                for (var i = 0, len = jsonObj.result.length; i < len; i++) {
                    if (jsonObj.result[i].type == REST_TRACE_TYPE.STARTING && (_flag_multiple_starting_counter == 0)) {
                        html_content += "<div class='col-sm-5'>";
                        html_content += jsonObj.result[i].dpid;
                        html_content += "</div><div class='col-sm-3'>";
                        html_content += jsonObj.result[i].port;
                        html_content += "</div>";

                        _flag_multiple_starting_counter++;
                    }
                }
            } else {
                html_content += "<div class='col-sm-8'>---</div>";
            }
            html_content += "</div>";

            html_content += "<div class='row'><div class='col-sm-12'>";
            html_content += "<strong>Start time: </strong>" + (jsonObj.start_time || "---");
            html_content += "</div></div>";

            html_content += "<div class='row'><div class='col-sm-12'>";
            html_content += "<strong>Total time: </strong>" + (jsonObj.total_time || "---");
            html_content += "</div></div>";
            if(jsonObj.result) {
                html_content += "<hr>";
                html_content += "<div class='col-sm-12'>";
                html_content += "<table class='table table-striped'>";
                html_content += "<thead><tr><th></th><th>Switch/DPID</th><th>Incoming Port</th><th>Time</th></tr></thead>";
                html_content += "<tbody>";

                var _flag_multiple_starting_counter = 0;
                for (var i = 0, len = jsonObj.result.length; i < len; i++) {

                    // FIXME: workaround for multiple starting type
                    if (jsonObj.result[i].type != REST_TRACE_TYPE.STARTING || (jsonObj.result[i].type == REST_TRACE_TYPE.STARTING && _flag_multiple_starting_counter > 0)) {
                        html_content += "<tr data-type="+ jsonObj.result[i].type +">";
                        html_content += "<td>" + (i) + "</td>";
                    }

                    // FIXME: workaround for multiple starting type
                    if (jsonObj.result[i].type == REST_TRACE_TYPE.STARTING && (_flag_multiple_starting_counter == 0)) {
                        _flag_multiple_starting_counter = _flag_multiple_starting_counter + 1;
                    // FIXME: workaround for multiple starting type
                    } else if ((jsonObj.result[i].type == REST_TRACE_TYPE.STARTING && _flag_multiple_starting_counter > 0) || jsonObj.result[i].type == REST_TRACE_TYPE.TRACE) {
                        html_content += "<td>" + jsonObj.result[i].dpid + "</td>";
                        html_content += "<td>" + jsonObj.result[i].port + "</td>";
                        html_content += "<td>" + jsonObj.result[i].time + "</td>";
                    } else if (jsonObj.result[i].type == REST_TRACE_TYPE.INTERTRACE) {
                        html_content += "<td colspan='3'><strong>Interdomain: " + jsonObj.result[i].domain + "</strong></td>";
                    } else if (jsonObj.result[i].type == REST_TRACE_TYPE.LAST) {
                        html_content += "<td colspan='3'>";
                        if (jsonObj.result[i].reason == REST_TRACE_REASON.ERROR) {
                            html_content += "<span class='trace_result_item_error'>Error: ";
                            html_content += jsonObj.result[i].msg || "";
                            html_content += "</span>"
                        } else if (jsonObj.result[i].reason == REST_TRACE_REASON.DONE) {
                            html_content += "<span class='trace_result_item_done'>Trace completed. ";
                            if (jsonObj.result[i].msg != 'none') {
                                html_content += jsonObj.result[i].msg || "";
                            }
                            html_content += "</span>"
                        } else if (jsonObj.result[i].reason == REST_TRACE_REASON.LOOP) {
                            html_content += "<span class='trace_result_item_loop'>Trace completed with loop. ";
                            html_content += jsonObj.result[i].msg || "";
                            html_content += "</span>"
                        }
                        html_content += "</td>";
                    } else if (jsonObj.result[i].type == REST_TRACE_TYPE.ERROR) {
                        html_content += "<td colspan='3'>" + jsonObj.result[i].message + "</td>";
                    }
                    html_content += "</tr>";
                }

                html_content += "</tbody></table></div>";
            }
            html_content += "</div>"

            $('#trace-result-content').html(html_content);
            $('#trace_panel_info_collapse').collapse("show");
        }

        var _add_new_html_node = function(_id) {
            /**
            Add html data selector after add a new node
            */
            var html_selector = "#node-" + _id;
            $(html_selector).addClass("new-node node-trace-active");
            $(html_selector).attr("data-nodeid", _id);
        }

        var _add_new_html_link = function(_id_from, _id_to) {
            /**
            Add html data selector after add a new link
            */
            var html_selector = "#link-" + _id_from +"-"+ _id_to;
            $(html_selector).addClass("new-link link-trace-active");
            $(html_selector).attr("data-linkid", _id_from +"-"+ _id_to);
        }

        var ajax_done = function(jsonObj) {
            if (jsonObj && jsonObj == 0) {
                return;
            }

            try {
                if (jsonObj.result && jsonObj.result.length > 0) {
                    var flag_has_domain = false;
                    // temporary var to last node
                    var last_node_id = null;
                    // temporary var to last interdomain
                    var last_domain_id = null;

                    for (var i = 0, len = jsonObj.result.length; i < len; i++) {
                        var result_item = jsonObj.result[i];
                        var _id = null;

                        if (result_item.hasOwnProperty("domain")) {
                            // Add new domain node
                            _label = result_item.domain;
                            // add node data do d3
                            var node_domain = d3lib.add_new_node_domain(result_item.domain, _label);
                            _id = node_domain.id;
                            // add html data
                            _add_new_html_node(_id);

                            // Add new link
                            d3lib.add_new_link(last_node_id, _id);
                            _add_new_html_link(last_node_id, _id);

                            flag_has_domain = true;
                            last_domain_id = _id;
                        }
                        if (result_item.hasOwnProperty("dpid")) {
                            _id = result_item.dpid;
                            if (flag_has_domain) {
                                // Add new switch node related to new domain
                                d3lib.add_new_node(_id, "", last_domain_id);
                                _add_new_html_node(_id);

                                // Add new link
                                d3lib.add_new_link(last_node_id, _id);
                                _add_new_html_link(last_node_id, _id);
                            }
                            $("#node-" + _id).addClass("node-trace-active");
                        }


                        if (i > 0 && jsonObj.result[i-1].hasOwnProperty("dpid") && jsonObj.result[i].hasOwnProperty("dpid")) {
                            // Add new link between nodes
                            var css_selector = "#link-" + jsonObj.result[i-1].dpid +"-"+ jsonObj.result[i].dpid;
                            $(css_selector).addClass("new-link link-trace-active");
                            // Activate the return link too
                            css_selector = "#link-" + jsonObj.result[i].dpid +"-"+ jsonObj.result[i-1].dpid;
                            $(css_selector).addClass("new-link link-trace-active");
                        }

                        last_node_id = _id;
                    }

                    var last_result_item = jsonObj.result[jsonObj.result.length - 1];
                    if (last_result_item.type == REST_TRACE_TYPE.LAST) {
                        // FLAG to stop the trigger loop
                        if (sdntrace._flag_call_trace_listener_again_counter < 12) {
                            sdntrace._flag_call_trace_listener_again_counter = sdntrace._flag_call_trace_listener_again_counter + 1;
                        } else {
                            console.log('type last');
                            // stop the interval loop
                            sdntrace.trace_stop();
                        }
                    } else if (last_result_item.type == REST_TRACE_TYPE.ERROR) {
                        console.log('type error');
                        // stop the interval loop
                        sdntrace.trace_stop();
                    }
                }
                html_render(jsonObj);
                //forcegraph.draw();
            } catch(err) {
                sdntrace.trace_stop();
                throw err;
            }
        }

        // counting the trace time elapsed
        _trace_timer_counter = _trace_timer_counter + _trace_timer_trigger_call;

        // Timeout. Stopping the trace.
        if(_trace_timer_counter > _trace_timer_max) {
            sdntrace.trace_stop();
        }

        // AJAX call
        if (DEBUG) {

            json = "";
            debug_trace_trigger_counter = debug_trace_trigger_counter + 1;

            if (debug_trace_trigger_counter == 1) { json = MOCK_JSON_TRACE_RESULT_PART1; }
            else if (debug_trace_trigger_counter == 2) { json = MOCK_JSON_TRACE_RESULT_PART2; }
            else if (debug_trace_trigger_counter == 3) { json = MOCK_JSON_TRACE_RESULT_PART3; }
            else if (debug_trace_trigger_counter == 4) {
                 debug_timeout_trace_trigger_counter = debug_timeout_trace_trigger_counter + 1;

                 if (debug_timeout_trace_trigger_counter == 1) { json = MOCK_JSON_TRACE_RESULT_PART4; }
                 else if (debug_timeout_trace_trigger_counter == 2) { json = MOCK_JSON_TRACE_RESULT_PART4_ERROR; }
                 else if (debug_timeout_trace_trigger_counter == 3) { json = MOCK_JSON_TRACE_RESULT_PART4_LOOP; }
                 else {
                    json = MOCK_JSON_TRACE_RESULT_PART4;
                    debug_timeout_trace_trigger_counter = 0;
                 }
            } else if (debug_trace_trigger_counter == 5) {
                debug_trace_trigger_counter = 1;
                json = MOCK_JSON_TRACE_RESULT_PART1;
            } else if (debug_trace_trigger_counter > 5) {
                json = MOCK_JSON_TRACE_RESULT_INTERDOMAIN;
                debug_trace_trigger_counter = 0;
            }

            var jsonobj = $.parseJSON(json);
            ajax_done(jsonobj);

        } else {
            var jqxhr = $.ajax({
                url:"/sdntrace/trace/" + trace_id.request_id + "?q=" + Math.random(),
                type: 'GET',
                dataType: 'json',
                crossdomain:true
            }).done(function(json) {
                ajax_done(json);
                console.log('call_trace_listener  ajax done');
            })
            .fail(function() {
                console.log( "call_trace_listener ajax error" );
                // Stop trace
                sdntrace.trace_stop();
            })
            .always(function() {
                console.log( "call_trace_listener ajax complete" );
            });
        }

        if (sdntrace._flag_call_trace_listener_again) {
            _thread_trace_listener = setTimeout(sdntrace.call_trace_listener, _trace_timer_trigger_call, trace_id);
        }
    }

    /**
     * Call ajax to load trace result.
     */
    this.call_get_trace = function() {
        var ajax_done = function(jsonObj) {
            last_trace = jsonObj;
        }

        // AJAX call
        if (DEBUG) {
            json = MOCK_JSON_TRACE;
            var jsonobj = $.parseJSON(json);
            ajax_done(jsonobj);

            // render D3 force
            d3lib.render_topology();
            $('#topology__canvas').show();
        } else {
            var jqxhr = $.ajax({
                url:"/sdntrace/trace",
                dataType: 'json',
                crossdomain:true,
            }).done(function(json) {
                ajax_done(json);
            })
            .fail(function() {
                console.log( "call_get_switches ajax error" );
                sdntrace.trace_stop();
            })
            .always(function() {
                console.log( "call_get_switches ajax complete" );
            });
        }
    }
 } // SDNTrace


/* Initial load */
$(function() {
    sdntrace = new SDNTrace();

    // Trace form modal
    sdn_trace_form_dialog = $( "#sdn_trace_form" ).dialog({
      autoOpen: false,
      height: 600,
      width: 750,
      modal: true,
      buttons: {
        Cancel: function() {
          sdn_trace_form_dialog.dialog( "close" );
        }
      },
      close: function() {
        sdn_trace_form_dialog.dialog( "close" );
      }
    });

    // Trace form click events to submit forms
    $('#layer2_btn').click(function() {
        jsonStr = sdntrace._build_trace_layer2_json();
        sdntrace.call_trace_request_id(jsonStr);
    });
    $('#layer3_btn').click(function() {
        jsonStr = sdntrace._build_trace_layer3_json();
        sdntrace.call_trace_request_id(jsonStr);
    });
    $('#layerfull_btn').click(function() {
        jsonStr = sdntrace._build_trace_layerfull_json();
        sdntrace.call_trace_request_id(jsonStr);
    });
});