
var SdnFlowTable = function() {
    // Flow table dialog
    this.dialog = '';

    var _init = function(self) {
        _init_tabulator(self);
        _init_dialog(self);
    }

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
                        {id: 14, title:"dl_type", field:"match__dl_type", align:"center", width:"90", headerFilter:"input"},

                    ],
                },
                {//create column Actions group
                    id: 20,
                    title:"Action",
                    columns:[
                        {id: 21, title:"type", field:"action__type", align:"center", width:"100", headerFilter:"input"},
                        {id: 22, title:"max_len", field:"action__max_len", align:"center", width:"90", headerFilter:"input"},
                        {id: 23, title:"port", field:"action__port", align:"center", width:"90", headerFilter:"input"},
                        {id: 24, title:"vlan", field:"action__vlan_vid", align:"center", width:"90", headerFilter:"input"},
                    ],
                },
                {//create column Counters group
                    id: 30,
                    title:"Counters",
                    columns:[
                        {id: 31, title:"bytes", field:"byte_count", align:"center", width:"100", headerFilter:"input"},
                        {id: 32, title:"packets", field:"packet_count", align:"center", width:"100", headerFilter:"input"},
                    ],
                },
                {//create column group
                    id: 40,
                    title:"Other fields -",
                    columns:[
                        {id: 41, title:"", field:"empty", width:"120", headerSort:false},
                        {id: 42, title:"hard timeout", field:"hard_timeout", width:"120", headerFilter:"input"},
                        {id: 43, title:"idle timeout", field:"idle_timeout", width:"120", headerFilter:"input"},
//                        {id: 44, title:"duration nsec", field:"duration_nsec", align:"center", width:"120", headerFilter:"input"},
                        {id: 45, title:"duration sec", field:"duration_sec", align:"center", width:"120", headerFilter:"input"},
                        {id: 46, title:"table id", field:"table_id", align:"center", width:"100", headerFilter:"input"},
                    ],
                    headerDblClick :function(e, columnDef){
                        var header_title = $(columnDef.getElement()).children('.tabulator-col-content').children('.tabulator-col-title');
                        if (header_title.text() == 'Other fields +') {
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
            {field:"match__in_port", type:"=", value:''},
        ]);
    }

    var _init_dialog = function(self) {
        // Trace form modal
        self.dialog = $("#flow_stats_table_dialog").dialog({
          autoOpen: false,
          height: 750,
          width: 1700,
          modal: true,
          buttons: {
            Cancel: function() {
              sdnflowtable.dialogClose();
            }
          },
          close: function() {
              sdnflowtable.dialogClose();
          }
        });

        $("#flow_stats_table_dialog").on("dialogopen", function( event, ui ) {
            $("#flow_stats_table").tabulator("clearFilter", true);
            $("#flow_stats_table").tabulator("setSort", "priority", "desc"); //sort by PRIORITY groups
            $("#flow_stats_table").tabulator("setSort", "match__in_port", "asc"); //sort by PRIORITY groups

        });
    }

    this.setData = function(dpid, json) {
        // console panel title
        $("#ui-id-1").html(dpid);
        // fill tabulator table data
        $("#flow_stats_table").tabulator("setData", json);
    }
    this.dialogOpen = function() {
        sdnflowtable.dialog.dialog('open');
    }
    this.dialogClose = function() {
        sdnflowtable.dialog.dialog('close');
    }

    // Initialize sdnflowtable Object.
    _init(this);
}
