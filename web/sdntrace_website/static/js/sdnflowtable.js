
/**
 * Class to manage the flow stat visualization.
 * It is responsible to configure and render the flow stat table,
 * and the lateral panel data.
 */
var SdnFlowTable = function() {
    // Flow table dialog
    this.dialog = '';

    /**
     * Initial Tabulator columns and filters configuration.
     * @param {type} self Self object, because it is a private method
     */
    var _init_tabulator = function(self) {
//        $("#flow_stats_table").css('height', '700px');
        $("#flow_stats_table").tabulator({
//            height:"600px",
            groupBy:"match__in_port",
            headerFilterPlaceholder:"Filter...",
            columns:[
                {id: 1, title:"in_port", field:"match__in_port", sorter:"string", width:"85", headerFilter:"number"},
                {id: 2, title:"cookie", field:"cookie", width:"85", headerFilter:"input"},
                {id: 3, title:"priority", field:"priority", width:"85", sorter:"number", headerFilter:"input"},
                {//create column Match group
                    id: 10,
                    title:"Match",
                    columns:[
                        {id: 11, title:"vlan", field:"match__dl_vlan", align:"center", width:"70", headerFilter:"input"},
                        {id: 12, title:"dl_src", field:"match__dl_src", align:"center", width:"135", headerFilter:"input"},
                        {id: 13, title:"dl_dst", field:"match__dl_dst", align:"center", width:"135", headerFilter:"input"},
                        {id: 14, title:"dl_type", field:"match__dl_type", align:"center", width:"90", headerFilter:"input"}
                    ]
                },
                {//create column Actions group
                    id: 20,
                    title:"Action",
                    columns:[
                        {id: 21, title:"type", field:"action__type", align:"center", width:"100", headerFilter:"input"},
                        {id: 22, title:"max_len", field:"action__max_len", align:"center", width:"90", headerFilter:"input"},
                        {id: 23, title:"port", field:"action__port", align:"center", width:"90", headerFilter:"input"},
                        {id: 24, title:"vlan", field:"action__vlan_vid", align:"center", width:"90", headerFilter:"input"}
                    ]
                },
                {//create column Counters group
                    id: 30,
                    title:"Counters",
                    columns:[
                        {id: 31, title:"bytes", field:"byte_count", align:"center", width:"100", headerFilter:"input"},
                        {id: 32, title:"packets", field:"packet_count", align:"center", width:"100", headerFilter:"input"}
                    ]
                },
                {//create column Other fields group
                    id: 40,
                    title:"Other fields -",
                    columns:[
                        {id: 41, title:"", field:"empty", width:"120", headerSort:false},
                        {id: 42, title:"hard timeout", field:"hard_timeout", width:"120", headerFilter:"input"},
                        {id: 43, title:"idle timeout", field:"idle_timeout", width:"120", headerFilter:"input"},
//                        {id: 44, title:"duration nsec", field:"duration_nsec", align:"center", width:"120", headerFilter:"input"},
                        {id: 45, title:"duration sec", field:"duration_sec", align:"center", width:"120", headerFilter:"input"},
                        {id: 46, title:"table id", field:"table_id", align:"center", width:"100", headerFilter:"input"}
                    ],
                    /**
                     * Other fields double click to toggle the columns visualization.
                     * @param {type} e Event obj
                     * @param {type} columnDef Column obj
                     */
                    headerDblClick :function(e, columnDef){
                        var header_title = $(columnDef.getElement()).children('.tabulator-col-content').children('.tabulator-col-title');
                        if (header_title.text() === 'Other fields +') {
                           header_title.text('Other fields -');
                        } else {
                           header_title.text('Other fields +');
                        }

                        $("#flow_stats_table").tabulator("toggleColumn","empty");
                        $("#flow_stats_table").tabulator("toggleColumn","hard_timeout");
                        $("#flow_stats_table").tabulator("toggleColumn","idle_timeout");
//                        $("#flow_stats_table").tabulator("toggleColumn","duration_nsec");
                        $("#flow_stats_table").tabulator("toggleColumn","duration_sec");
                        $("#flow_stats_table").tabulator("toggleColumn","table_id");
                    }
                }
            ]
        });

        $("#flow_stats_table").tabulator("toggleColumn","empty");

        $("#flow_stats_table").tabulator("setFilter", [
            {field:"match__in_port", type:"=", value:''}
        ]);
    };

    /**
     * Inital dialog configuration.
     * The Tabulator content is rendered inside a dialog widget.
     * @param {type} self
     * @returns {undefined}
     */
    var _init_dialog = function(self) {
        // Trace form modal
        self.dialog = $("#flow_stats_table_dialog").dialog({
          autoOpen: false,
          height: 750,
          width: 1700,
          modal: true,
          buttons: {
            Cancel: function() {
              self.dialogClose();
            }
          },
          close: function() {
              self.dialogClose();
          }
        });

        $("#flow_stats_table_dialog").on("dialogopen", function( event, ui ) {
            $("#flow_stats_table").tabulator("clearFilter", true);
            $("#flow_stats_table").tabulator("setSort", "priority", "desc"); //sort by PRIORITY groups
            $("#flow_stats_table").tabulator("setSort", "match__in_port", "asc"); //sort by PRIORITY groups

        });
    };

    var SdnFlowTable = function(self) {
        _init_tabulator(self);
        _init_dialog(self);
    }(this);


    /**
     * Set tabulator data.
     * @param {type} dpid Switch DPID
     * @param {type} json Tabulated data.
     */
    this.setData = function(dpid, json) {
        // console panel title
        $("#ui-id-1").html(dpid);
        // fill tabulator table data
        $("#flow_stats_table").tabulator("setData", json);
    };
    
    /**
     * Open the dialog with the Tabulator data.
     */
    this.dialogOpen = function() {
        this.dialog.dialog('open');
    };
    /**
     * Close the dialog with the Tabulator data.
     */
    this.dialogClose = function() {
        this.dialog.dialog('close');
    };

    /**
     * Use with set_switch_focus to set the lateral panel data
     * @param {type} p_dpid Switch DPID
     * @param {type} p_flowStat Switch flow data object
     */
    this.setSwitchFlowPanelData = function(p_dpid, p_flowStat) {
        /**
         * Helper function to create <li> tags to display flow attributes
         * @param {type} htmlUL HTML UL DOM
         * @param {type} label LI label value
         * @param {type} value LI type value
         */
        var _createLi = function(htmlUL ,label, value) {
            var htmlLI=  $('<li></li>');
            htmlUL.append(htmlLI);
            htmlLI.append($('<span>' + label + ': </span>'));
            htmlLI.append($('<span>' + value + '</span>'));
        };

        // display panel
        $('#switch_flows_panel').show();
        // animation to open panel
        $('#switch_flows_panel_collapse').collapse("show");
        // fill html content
        $('#switch_flows_panel_dpid_value').html(p_dpid);

        var _flowStatObj = p_flowStat;

        // Clear panel
        $('#switch_flows_panel_collapse > .panel-body').empty();
        // Prepare to create panel content
        var _html = $('<div></div>');
        $('#switch_flows_panel_collapse > .panel-body').append(_html);

        for(var x in _flowStatObj.flows) {
            var flowObj = _flowStatObj.flows[x];

            // Flow actions
            var actionStr = '<table class="table-bordered table-condensed"><thead><tr><th>Type</th><th>Max Len.</th><th>Port</th><th>VLAN</th></tr></thead><tbody>';
            for(var y in flowObj.actions) {
                var actionObj = flowObj.actions[y];
                actionStr += '<tr><td>' + actionObj.type + '</td><td>' + (actionObj.max_len || '--') + '</td><td>' + (actionObj.port || '--') + '</td><td>' + (actionObj.vlan_vid || '--') + '</td></tr>';
            }
            actionStr += '</tbody></table><br>';
            _html.append($(actionStr));

            // Flow attributes
            var htmlUL = $('<ul></ul>');
            _html.append(htmlUL);

            _createLi(htmlUL, 'Idle timeout', flowObj.idle_timeout);
            _createLi(htmlUL, 'Cookie', flowObj.cookie);
            _createLi(htmlUL, 'Priority', flowObj.priority);
            _createLi(htmlUL, 'Hard timeout', flowObj.hard_timeout);
            _createLi(htmlUL, 'Byte count', flowObj.byte_count);
            _createLi(htmlUL, 'Duration (ns)', flowObj.duration_nsec);
            _createLi(htmlUL, 'Packet count', flowObj.packet_count);
            _createLi(htmlUL, 'Duration (s)', flowObj.duration_sec);
            _createLi(htmlUL, 'Table ID', flowObj.table_id);

            htmlUL = $('<ul></ul>');
            _html.append(htmlUL);

            // Flow matches
            _createLi(htmlUL, '<u>Match</u>', '');
            if(flowObj.match.wildcards) { _createLi(htmlUL, 'wildcards', flowObj.match.wildcards || ''); }
            if(flowObj.match.in_port) { _createLi(htmlUL, 'in_port', flowObj.match.in_port || ''); }
            if(flowObj.match.dl_vlan) { _createLi(htmlUL, 'dl_vlan', flowObj.match.dl_vlan || ''); }
            if(flowObj.match.dl_type) { _createLi(htmlUL, 'dl_type', flowObj.match.dl_type || ''); }
            if(flowObj.match.dl_src) { _createLi(htmlUL, 'dl_src', flowObj.match.dl_src || ''); }
            if(flowObj.match.dl_dst) { _createLi(htmlUL, 'dl_dst', flowObj.match.dl_dst || ''); }

            _html.append($("<hr>"));
        }
    };
};
