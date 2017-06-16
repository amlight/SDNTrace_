
/* global DEBUG, forcegraph, MOCK, SDNLG_CONF, d3lib */

// reference to the trace form dialog
var sdn_trace_form_dialog = '';

var sdntrace = '';

var SDNTrace = function() {
    /** @constant */
    var REST_TRACE_TYPE = {'STARTING':'starting', 'LAST':'last', 'TRACE':'trace', 'INTERTRACE':'intertrace'};
    /** @constant */
    var REST_TRACE_REASON = {'ERROR':'error', 'DONE':'done', 'LOOP':'loop'};
    
    var _self = this;

    // last trace id executing
    this.lastTraceID = "";


    this.clearTraceInterface = function() {
        /**
        * Clear trace forms, result, result pannel, dialog modal, graph highlight, graph trace
        */
        $('#trace-result-content').html('');
        $('#trace_panel_info .loading-icon-div').hide();

        // clear d3 graph highlight nodes, links
        forcegraph.endHighlight();

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
    };

    this.callTraceRequestId = function(json_data) {
        /**
         * Call ajax to trace.
         * Param:
         *    json_data: Data in json String format to send as PUT method.
         */
        _self.clearTraceInterface();

        var ajaxDone = function(json) {
            // Stopping any ongoing trace.
            _self.traceStop();
            _self.traceReset();

            // Trigger AJAX to retrieve the trace result
            _self.triggerTraceListener(json);
        };

        // show loading icon
        $('#trace_panel_info .loading-icon-div').show();

        // AJAX call
        if (DEBUG) {
            json = MOCK.JSON_TRACE;
            var jsonobj = $.parseJSON(json);
            ajaxDone(jsonobj);
        } else {
            $.ajax({
                url: SDNLG_CONF.trace_server + "/sdntrace/trace",
                type: 'PUT',
                dataType: 'json',
                data: json_data
            })
            .done(function(json) {
                ajaxDone(json);
            })
            .fail(function(responseObj) {
                if (responseObj.responseJSON) {
                    $('#trace-result-content').html("<div class='bg-danger'>"+responseObj.responseJSON.error+"</div>");
                } else {
                    $('#trace-result-content').html("<div class='bg-danger'>Trace error.</div>");
                }
                _self.traceStop();
                console.warn("call_trace_request_id ajax error" );
            })
            .always(function() {
                $('#trace_panel_info').show();
            });
        }
    };

    this.renderHtmlTraceFormPorts = function(dpid, port_data) {
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

            if (index === "1") {
                // insert port
                $('#sdn_trace_form__switch-port-hidden').val(this.port_no);
            }
        });
    };

    /**
     * Build json string from form fields to send to trace layer 2 ajax.
     */
    this.buildTraceLayer2JSON = function() {
        var layer2 = new Object();
        var l2Trace = new Object();

        var l2Switch = new Object();
        l2Switch.dpid = $('#sdn_trace_form__switch-hidden').val();
        l2Switch.in_port = $('#sdn_trace_form__switch-port-hidden').val();
        if (l2Switch.in_port) {
            l2Switch.in_port = parseInt(l2Switch.in_port, 10);
        }
        l2Trace.switch = l2Switch;

        var l2Eth = new Object();
        l2Eth.dl_src = $('#l2_dl_src').val();
        l2Eth.dl_dst = $('#l2_dl_dst').val();
        l2Eth.dl_vlan = $('#l2_dl_vlan').val();
        if (l2Eth.dl_vlan) {
            l2Eth.dl_vlan = parseInt(l2Eth.dl_vlan, 10);
        }
        l2Eth.dl_type = $('#l2_dl_type').val();
        if (l2Eth.dl_type) {
            l2Eth.dl_type = parseInt(l2Eth.dl_type, 10);
        }
        l2Trace.eth = l2Eth;
        
        layer2.trace = l2Trace;

        layer2 = removeEmptyJsonValues(layer2);
        var layer2String = JSON.stringify(layer2);

        return layer2String;
    };

    /**
     * Build json string from form fields to send to trace layer 3 ajax.
     */
    this._build_trace_layer3_json = function() {
        var layer3 = new Object();
        var l3Trace = new Object();

        var l3Switch = new Object();
        l3Switch.dpid = $('#sdn_trace_form__switch-hidden').val();
        l3Switch.in_port = $('#sdn_trace_form__switch-port-hidden').val();
        if (l3Switch.in_port) {
            l3Switch.in_port = parseInt(l3Switch.in_port, 10);
        }
        l3Trace.switch = l3Switch;
        

        var l3Eth = new Object();
        l3Eth.dl_vlan = $('#l3_dl_vlan').val();
        if (l3Eth.dl_vlan) {
            l3Eth.dl_vlan = parseInt(l3Eth.dl_vlan, 10);
        }
        l3Trace.eth = l3Eth;

        var l3Ip = new Object();
        l3Ip.nw_src = $('#l3_nw_src').val();
        l3Ip.nw_dst = $('#l3_nw_dst').val();
        l3Ip.nw_tos = $('#l3_nw_tos').val();
        if (l3Ip.nw_tos) {
            l3Ip.nw_tos = parseInt(l3Ip.nw_tos, 10);
        }
        l3Trace.ip = l3Ip;

        var l3Tp = new Object();
        l3Tp.tp_src = $('#l3_tp_src').val();
        l3Tp.tp_dst = $('#l3_tp_dst').val();
        if (l3Tp.tp_dst) {
            l3Tp.tp_dst = parseInt(l3Tp.tp_dst, 10);
        }
        l3Trace.tp = l3Tp;
        
        layer3 = removeEmptyJsonValues(layer3);
        var layer3String = JSON.stringify(layer3);

        return layer3String;
    };

    /**
     * Build json string from form fields to send to full trace ajax.
     */
    this._build_trace_layerfull_json = function() {
        var layerfull = new Object();
        var lfTrace = new Object();

        var lfSwitch = new Object();
        lfSwitch.dpid = $('#sdn_trace_form__switch-hidden').val();
        lfSwitch.in_port = $('#sdn_trace_form__switch-port-hidden').val();
        if (lfSwitch.in_port) {
            lfSwitch.in_port = parseInt(lfSwitch.in_port, 10);
        }
        lfTrace.switch = lfSwitch;

        var lfEth = new Object();
        lfEth.dl_src = $('#lf_dl_src').val();
        lfEth.dl_dst = $('#lf_dl_dst').val();
        lfEth.dl_vlan = $('#lf_dl_vlan').val();
        if (lfEth.dl_vlan) {
            lfEth.dl_vlan = parseInt(lfEth.dl_vlan, 10);
        }
        lfEth.dl_type = $('#lf_dl_type').val();
        if (lfEth.dl_type) {
            lfEth.dl_type = parseInt(lfEth.dl_type, 10);
        }
        lfTrace.eth = lfEth;

        var lfIp = new Object();
        lfIp.nw_src = $('#lf_nw_src').val();
        lfIp.nw_dst = $('#lf_nw_dst').val();
        lfIp.nw_tos = $('#lf_nw_tos').val();
        if (lfIp.nw_tos) {
            lfIp.nw_tos = parseInt(lfIp.nw_tos, 10);
        }
        lfTrace.ip = lfIp;
        
        var lfTp = new Object();
        lfTp.tp_src = $('#lf_tp_src').val();
        lfTp.tp_dst = $('#lf_tp_dst').val();
        if (lfTp.tp_dst) {
            lfTp.tp_dst = parseInt(lfTp.tp_dst, 10);
        }
        lfTrace.tp = lfTp;
        
        layerfull.trace = lfTrace;

        layerfull = removeEmptyJsonValues(layerfull);
        var layerfullString = JSON.stringify(layerfull);

        return layerfullString;
    };
    


    // Timeout flag to stop the trace listener
    var _threadTraceListener = "";
    // Time to trigger the next call in ms
    var _traceTimerTriggerCall = 1000;
    // Total time to trigger the call. After that trigger timeout method.
    var _traceTimerMax = 30000;

    var _traceTimerCounter = 0;

    this.triggerTraceListener = function(traceId) {
        _self.lastTraceID = traceId;

        // show load icon
        $('#trace_panel_info .loading-icon-div').show();

        // Clearing the trace panel
        $('#trace-result-content').html("");
        $('#trace_panel_info_collapse').collapse("hide");

        // Call to AJAX to retrieve the trace result
        this.callTraceListener(traceId);
    };

    // Reset all variables to start the trace
    this.traceReset = function() {
        clearTimeout(_threadTraceListener);
        _threadTraceListener = "";
        _traceTimerCounter = 0;
        _flagCallTraceListenerAgain = true;
    };
    
    // Stop trace thread and block all variables.
    this.traceStop = function() {
        console.log('TRACE STOP');

        clearTimeout(_threadTraceListener);

        _threadTraceListener = "";
        _traceTimerCounter = 100000;
        _flagCallTraceListenerAgain = false;

        // hide loading icon
        $('#trace_panel_info .loading-icon-div').hide();
    };

    var debugTraceTriggerCounter = 10;
    var debugTimeoutTraceTriggerCounter = 0;

    var _flagCallTraceListenerAgain = true;

    this.callTraceListener = function(traceId) {
        var htmlRender = function(jsonObj) {
            /**
            * Render trace result html info.
            */
            var htmlContent = "";
            htmlContent += "<div class='row'>";
            htmlContent += "<div class='col-sm-4'>";
            htmlContent += "<strong>Start from:</strong>";
            htmlContent += "</div>";
            if(jsonObj.result) {
                // FIXME workaround for multiple starting type
                var _flag_multiple_starting_counter = 0;
                for (var i = 0, len = jsonObj.result.length; i < len; i++) {
                    if (jsonObj.result[i].type === REST_TRACE_TYPE.STARTING && (_flag_multiple_starting_counter === 0)) {
                        htmlContent += "<div class='col-sm-5'>";
                        htmlContent += jsonObj.result[i].dpid;
                        htmlContent += "</div><div class='col-sm-3'>";
                        htmlContent += jsonObj.result[i].port;
                        htmlContent += "</div>";

                        _flag_multiple_starting_counter++;
                    }
                }
            } else {
                htmlContent += "<div class='col-sm-8'>---</div>";
            }
            htmlContent += "</div>";

            htmlContent += "<div class='row'><div class='col-sm-12'>";
            htmlContent += "<strong>Start time: </strong>" + (jsonObj.start_time || "---");
            htmlContent += "</div></div>";

            htmlContent += "<div class='row'><div class='col-sm-12'>";
            htmlContent += "<strong>Total time: </strong>" + (jsonObj.total_time || "---");
            htmlContent += "</div></div>";
            if(jsonObj.result) {
                htmlContent += "<hr>";
                htmlContent += "<div class='col-sm-12'>";
                htmlContent += "<table class='table table-striped'>";
                htmlContent += "<thead><tr><th></th><th>Switch/DPID</th><th>Incoming Port</th><th>Time</th></tr></thead>";
                htmlContent += "<tbody>";

                var _flag_multiple_starting_counter = 0;
                for (var i = 0, len = jsonObj.result.length; i < len; i++) {

                    // FIXME: workaround for multiple starting type
                    if (jsonObj.result[i].type !== REST_TRACE_TYPE.STARTING || (jsonObj.result[i].type === REST_TRACE_TYPE.STARTING && _flag_multiple_starting_counter > 0)) {
                        htmlContent += "<tr data-type="+ jsonObj.result[i].type +">";
                        htmlContent += "<td>" + (i) + "</td>";
                    }

                    // FIXME: workaround for multiple starting type
                    if (jsonObj.result[i].type === REST_TRACE_TYPE.STARTING && (_flag_multiple_starting_counter === 0)) {
                        _flag_multiple_starting_counter = _flag_multiple_starting_counter + 1;
                    // FIXME: workaround for multiple starting type
                    } else if ((jsonObj.result[i].type === REST_TRACE_TYPE.STARTING && _flag_multiple_starting_counter > 0) || jsonObj.result[i].type === REST_TRACE_TYPE.TRACE) {
                        htmlContent += "<td>" + jsonObj.result[i].dpid + "</td>";
                        htmlContent += "<td>" + jsonObj.result[i].port + "</td>";
                        htmlContent += "<td>" + jsonObj.result[i].time + "</td>";
                    } else if (jsonObj.result[i].type === REST_TRACE_TYPE.INTERTRACE) {
                        htmlContent += "<td colspan='3'><strong>Interdomain: " + jsonObj.result[i].domain + "</strong></td>";
                    } else if (jsonObj.result[i].type === REST_TRACE_TYPE.LAST) {
                        htmlContent += "<td colspan='3'>";
                        if (jsonObj.result[i].reason === REST_TRACE_REASON.ERROR) {
                            htmlContent += "<span class='trace_result_item_error'>Error: ";
                            htmlContent += jsonObj.result[i].msg || "";
                            htmlContent += "</span>";
                        } else if (jsonObj.result[i].reason === REST_TRACE_REASON.DONE) {
                            htmlContent += "<span class='trace_result_item_done'>Trace completed. ";
                            if (jsonObj.result[i].msg !== 'none') {
                                htmlContent += jsonObj.result[i].msg || "";
                            }
                            htmlContent += "</span>";
                        } else if (jsonObj.result[i].reason === REST_TRACE_REASON.LOOP) {
                            htmlContent += "<span class='trace_result_item_loop'>Trace completed with loop. ";
                            htmlContent += jsonObj.result[i].msg || "";
                            htmlContent += "</span>";
                        }
                        htmlContent += "</td>";
                    } else if (jsonObj.result[i].type === REST_TRACE_TYPE.ERROR) {
                        htmlContent += "<td colspan='3'>" + jsonObj.result[i].message + "</td>";
                    }
                    htmlContent += "</tr>";
                }

                htmlContent += "</tbody></table></div>";
            }
            htmlContent += "</div>";

            $('#trace-result-content').html(htmlContent);
            $('#trace_panel_info_collapse').collapse("show");
        };

        var _addNewHtmlNode = function(_id) {
            /**
            Add html data selector after add a new node
            */
            var html_selector = "#node-" + _id;
            $(html_selector).addClass("new-node node-trace-active");
            $(html_selector).attr("data-nodeid", _id);
        };

        var _addNewHtmlLink = function(_idFrom, _idTo) {
            /**
            Add html data selector after add a new link
            */
            var html_selector = "#link-" + _idFrom +"-"+ _idTo;
            $(html_selector).addClass("new-link link-trace-active");
            $(html_selector).attr("data-linkid", _idFrom +"-"+ _idTo);
        };

        var ajaxDone = function(jsonObj) {
            if (jsonObj && jsonObj === "0") {
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
                            var node_domain = d3lib.addNewNodeDomain(result_item.domain, _label);
                            _id = node_domain.id;
                            // add html data
                            _addNewHtmlNode(_id);

                            // Add new link
                            d3lib.addNewLink(last_node_id, _id);
                            _addNewHtmlLink(last_node_id, _id);

                            flag_has_domain = true;
                            last_domain_id = _id;
                        }
                        if (result_item.hasOwnProperty("dpid")) {
                            _id = result_item.dpid;
                            if (flag_has_domain) {
                                // Add new switch node related to new domain
                                d3lib.addNewNode(_id, "", last_domain_id);
                                _addNewHtmlNode(_id);

                                // Add new link
                                d3lib.addNewLink(last_node_id, _id);
                                _addNewHtmlLink(last_node_id, _id);
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
                    if (last_result_item.type === REST_TRACE_TYPE.LAST) {
                        // FLAG to stop the trigger loop
                        if (_self._flagCallTraceListenerAgainCounter < 12) {
                            _self._flagCallTraceListenerAgainCounter = _self._flagCallTraceListenerAgainCounter + 1;
                        } else {
                            console.log('type last');
                            // stop the interval loop
                            _self.traceStop();
                        }
                    } else if (last_result_item.type === REST_TRACE_TYPE.ERROR) {
                        console.log('type error');
                        // stop the interval loop
                        _self.traceStop();
                    }
                }
                htmlRender(jsonObj);
            } catch(err) {
                _self.traceStop();
                console.error(err);
                throw err;
            }
        };

        // counting the trace time elapsed
        _traceTimerCounter = _traceTimerCounter + _traceTimerTriggerCall;

        // Timeout. Stopping the trace.
        if(_traceTimerCounter > _traceTimerMax) {
            _self.traceStop();
        }

        // AJAX call
        if (DEBUG) {
            var json = "";
            debugTraceTriggerCounter = debugTraceTriggerCounter + 1;

            if (debugTraceTriggerCounter === 1) { json = MOCK.JSON_TRACE_RESULT_PART1; }
            else if (debugTraceTriggerCounter === 2) { json = MOCK.JSON_TRACE_RESULT_PART2; }
            else if (debugTraceTriggerCounter === 3) { json = MOCK.JSON_TRACE_RESULT_PART3; }
            else if (debugTraceTriggerCounter === 4) {
                 debugTimeoutTraceTriggerCounter = debugTimeoutTraceTriggerCounter + 1;

                 if (debugTimeoutTraceTriggerCounter === 1) { json = MOCK.JSON_TRACE_RESULT_PART4; }
                 else if (debugTimeoutTraceTriggerCounter === 2) { json = MOCK.JSON_TRACE_RESULT_PART4_ERROR; }
                 else if (debugTimeoutTraceTriggerCounter === 3) { json = MOCK.JSON_TRACE_RESULT_PART4_LOOP; }
                 else {
                    json = MOCK.JSON_TRACE_RESULT_PART4;
                    debugTimeoutTraceTriggerCounter = 0;
                 }
            } else if (debugTraceTriggerCounter === 5) {
                debugTraceTriggerCounter = 1;
                json = MOCK.JSON_TRACE_RESULT_PART1;
            } else if (debugTraceTriggerCounter > 5) {
                json = MOCK.JSON_TRACE_RESULT_INTERDOMAIN;
                debugTraceTriggerCounter = 0;
            }

            var jsonobj = $.parseJSON(json);
            ajaxDone(jsonobj);

        } else {
            $.ajax({
                url:"/sdntrace/trace/" + traceId.request_id + "?q=" + Math.random(),
                type: 'GET',
                dataType: 'json',
                crossdomain:true
            })
            .done(function(json) {
                ajaxDone(json);
                console.log('call_trace_listener  ajax done');
            })
            .fail(function() {
                console.warn("call_trace_listener ajax error" );
                // Stop trace
                _self.traceStop();
            })
            .always(function() {
                console.log( "call_trace_listener ajax complete" );
            });
        }

        if (_flagCallTraceListenerAgain) {
            _threadTraceListener = setTimeout(_self.callTraceListener, _traceTimerTriggerCall, traceId);
        }
    };
 }; // SDNTrace


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
        var jsonStr = sdntrace.buildTraceLayer2JSON();
        sdntrace.callTraceRequestId(jsonStr);
    });
    $('#layer3_btn').click(function() {
        var jsonStr = sdntrace._build_trace_layer3_json();
        sdntrace.callTraceRequestId(jsonStr);
    });
    $('#layerfull_btn').click(function() {
        var jsonStr = sdntrace._build_trace_layerfull_json();
        sdntrace.callTraceRequestId(jsonStr);
    });
});
