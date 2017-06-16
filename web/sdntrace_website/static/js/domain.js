
/* global SDNLG_CONF, sdncolor */

/**
 * Represents link between two nodes.
 * @returns {Link}
 */
var Link = function() {
    // Switch objects
    this.node1 = null;
    this.node2 = null;

    // Label name String
    this.label1 = null;
    this.label2 = null;

    // Label number String
    this.label_num1 = null;
    this.label_num2 = null;

    // number. Bits per second.
    this.speed = null;
};

/**
 * Switch representation.
 * @param {type} switch_id Switch DPID (datapath id)
 * @returns {Switch}
 */
var Switch = function(switch_id) {
    this.id = switch_id;
    this.dpid = switch_id; // datapath_id

    this.name;
    this.switch_color;
    this.tcp_port;
    this.openflow_version;
    this.switch_vendor;
    this.ip_address;
    this.number_flows;

    // number of ports
    this.n_ports;
    this.n_tables;

    // switch ports
    this.ports = [];

    // switch flows statistics
    this.flow_stat = null;

    this.domain; // if the switch belongs to an interdomain

    /**
     * Get switch fantasy name from configuration data.
     * @returns {String}
     */
    this.getName = function() {
        if (this.name) {
            return this.name;
        }
        if (typeof SDNLG_CONF !== 'undefined') {
            var name = SDNLG_CONF.dict[this.id];
            if (name !== undefined) {
                return name;
            }
        }
        return "";
    };

    /**
     * Get switch fantasy name from configuration data.
     * If there is no name return the switch ID.
     */
    this.getNameOrId = function() {
        if (this.name) {
            return this.name;
        }
        if (typeof SDNLG_CONF !== 'undefined') {
            var name = SDNLG_CONF.dict[this.id];
            if (name !== undefined) {
                return name;
            }
        }
        return this.id;
    };

    /**
     * Get switch fantasy name from configuration data.
     * Return verbose name as: <ID> - <NAME>
     */
    this.getVerboseName = function() {
        if (this.name) {
            return this.id + ' - ' + this.name;
        }
        if (typeof SDNLG_CONF !== 'undefined') {
            var name = SDNLG_CONF.dict[this.id];
            if (name !== undefined) {
                return this.id + ' - ' + name;
            }
        }
        return this.id;
    };

    /**
     * Get switch fantasy name from configuration data.
     * Return verbose name to be used on vis.js: <ID>\n<NAME>
     */
    this.getNodeName = function() {
        if (this.name) {
            return this.name;
        }

        if (typeof SDNLG_CONF !== 'undefined') {
            var name = SDNLG_CONF.dict[this.id];
            if (name !== undefined) {
                return name;
            }
        }
        return this.id;
    };

    this.get_port_by_id = function(node_id, p_id) {
        var port_id = node_id +"_"+ p_id;

        for (var x in this.ports){
            if(this.ports[x].id === port_id) {
                return this.ports[x];
            }
        }
        return null;
    };

    this.getD3jsData = function() {
        var nodeObj = {
            id: this.id,
            dpid: this.id,
            name: this.id,
            data: this,
            label: this.getNodeName(),
            physics: true,
            stroke_width: 1,
            x: 300, // OBS: need to position otherwise will be at x = 0
            y: 300, // OBS: need to position otherwise will be at y = 0
            type: Switch.TYPE
        };
        // Trace coloring
        if (typeof(nodeObj.color) === 'undefined') {
            nodeObj.background_color = sdncolor.NODE_COLOR[nodeObj.type];
        }
        return nodeObj;
    };
};

// Return switch id if the class is used with strings
Switch.prototype.toString = function(){ return this.id; };
Switch.clone_obj = function(p_sw) {
    var return_switch = new Switch(p_sw.id);

    return_switch.id = p_sw.id;
    return_switch.dpid = p_sw.dpid;
    return_switch.name = p_sw.name;
    return_switch.switch_color = p_sw.switch_color;
    return_switch.tcp_port = p_sw.tcp_port;
    return_switch.openflow_version = p_sw.openflow_version;
    return_switch.switch_vendor = p_sw.switch_vendor;
    return_switch.ip_address = p_sw.ip_address;
    return_switch.number_flows = p_sw.number_flows;
    return_switch.n_ports = p_sw.n_ports;
    return_switch.n_tables = p_sw.n_tables;
    return_switch.ports = p_sw.ports;
    return_switch.domain = p_sw.domain;

    return return_switch;
};

/**
 * Switch static TYPE property;
 * @type String
 */
Switch.TYPE = "switch";

/**
 * Node port representation.
 * Node can be a Switch or Host.
 * 
 * @param {type} node_id Switch or Host id.
 * @param {type} port_id Port id
 * @param {type} number Port number
 * @param {type} label Port label
 * @returns {Port}
 */
var Port = function(node_id, port_id, number, label) {
    this.id = node_id + "_" + port_id;
    this.number = number;
    this.label = label;
    this.speed = '';
    this.uptime = '';
    this.status = '';

    this.getD3jsData = function() {
        var nodeObj = {
            id: this.id,
            name: null,
            data: this,
            label: this.label,
            physics: true,
            from_sw: '',
            to_sw: '',
            stroke_width: 1,
            type: Port.TYPE
        };
        nodeObj.background_color = sdncolor.NODE_COLOR[nodeObj.type];

        return nodeObj;
    };
};

// Return switch port id if the class is used with strings
Port.prototype.toString = function(){ return this.id; };

/**
 * Port static TYPE property;
 * @type String
 */
Port.TYPE = "port";


/**
 * Domain representation.
 * @param {type} domain_id
 * @param {type} label
 * @returns {Domain}
 */
var Domain = function(domain_id, label) {
    this.id = domain_id;
    this.label = label;

    this.getD3jsData = function() {
        var nodeObj = {
            id: this.id,
            name: null,
            data: this,
            label: this.label,
            physics: true,
            stroke_width: 1,
            type: Domain.TYPE
        };
        nodeObj.background_color = sdncolor.NODE_COLOR[nodeObj.type];

        return nodeObj;
    };

    this.getName = function() {
        return this.label;
    };
};

/**
 * Domain static TYPE property;
 * @type String
 */
Domain.TYPE = "domain";

/**
 * Domain static function to generate an ID based on the domain_name. 
 * @param {type} p_domainName
 * @returns {String}
 */
Domain.createId = function(p_domainName) {
    if (p_domainName === null || p_domainName === "") {
        console.log("[ERROR] Domain.createId p_domain_name is empty.");
        throw "[ERROR] Domain.createId p_domain_name is empty.";
    }

    var domain_id = p_domainName.replace(" ", "_");

    return "domain_" + domain_id;
};

/**
 * Host representation.
 * Hosts must be linked to a Node.
 * 
 * @param {type} host_id Host id. Use can use the createId() to generate an ID.
 * @param {type} label Host label
 * @returns {Host}
 */
var Host = function(host_id, label) {
    this.id = host_id;
    this.label = label;

    this.getD3jsData = function() {
        var nodeObj = {
            id: this.id,
            name: null,
            data: this,
            label: this.label,
            physics: true,
            stroke_width: 1,
            type: Host.TYPE
        };
        nodeObj.background_color = sdncolor.NODE_COLOR[nodeObj.type];

        return nodeObj;
    };

    this.getName = function() {
        return this.label;
    };
};

/**
 * Host static TYPE property;
 * @type String
 */
Host.TYPE = "host";

/**
 * Host static function to generate a Host ID with the parameters.
 * @param {type} node_id
 * @param {type} port_id
 * @returns {String}
 */
Host.createId = function(node_id, port_id) {
    if (node_id === null || node_id === "") {
        console.log("[ERROR] Host.createId node_id empty.");
        throw "[ERROR] Host.createId node_id empty.";
    }
    if (port_id === null || port_id === "") {
        console.log("[ERROR] Host.createId port_id empty.");
        throw "[ERROR] Host.createId port_id empty.";
    }

    return "host_" + node_id + "_" + port_id;
};
