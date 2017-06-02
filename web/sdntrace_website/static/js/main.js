
/**
 * Helper function to remove duplicates from an array.
 * @param {type} p_array
 * @returns {Array}
 */
var arrayRemoveDuplicates = function(p_array) {
    var seen = {};
    var out = [];
    var len = p_array.length;
    var j = 0;
    for(var i = 0; i < len; i++) {
        var item = p_array[i];
        if(seen[item] !== 1) {
            seen[item] = 1;
            out[j++] = item;
        }
    }
    return out;
};

/*
 * Helper function to remove attributes with empty values from a json object.
 */
var removeEmptyJsonValues = function(obj) {
    for (var i in obj) {
        for (var j in obj[i]) {
            for (var w in obj[i][j]) {
                if (obj[i][j][w] === null || obj[i][j][w] === '') {
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
};


var forcegraph = '';
var sdntopology = '';
var sdncolor = '';
var sdnflowtable = '';

/* Initial data load */
/* Call ajax to load switches and topology */
var _initialDataLoad = function() {
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
    var getSwitchesCallback = sdntopology.callSdntraceGetTopology;

    // load switches data
    // Pass load topology function as a callback
    sdntopology.callSdntraceGetSwitches(getSwitchesCallback);
};


/* Initial configuration */
var _initial_configuration = function() {
    if (typeof SDNLG_CONF != 'undefined') {
        // header logo img src
        $('#header__logo img').attr("src", SDNLG_CONF.header_logo_img_src);
        // header name
        // $('#header__name').text(SDNLG_CONF.header_name);
        // SDN LG version
        $('#about__version').text(SDNLG_CONF.version);
        $('#about__roadmap').html(SDNLG_CONF.about_roadmap);
    }
}

var _initial_event_handlers = function() {
    
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
        sdntrace.clearTraceInterface();

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
}


/* Initial load */
$(function() {
    // Load js configuration data
    _initial_configuration();
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
    
    _initial_event_handlers()

    forcegraph = new ForceGraph(selector,data);

    sdnflowtable = new SdnFlowTable();

    // initial data load (switch list, topology, colors)
    _initialDataLoad();
});




