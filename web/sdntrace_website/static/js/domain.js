
var Link = function() {
    // Switch obj
    this.node1 = null;
    this.node2 = null;

    // String
    this.label1 = null;
    this.label2 = null;

    // String
    this.label_num1 = null;
    this.label_num2 = null;

    // number. Bits per second.
    this.speed = null;
}

/**
 * Switch representation.
 */
var Switch = function(switch_id) {
    this.id = switch_id;
    this.dpid = switch_id; // datapath_id

    this.name;
    this.switch_color;
    this.tcp_port
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
     */
    this.get_name = function() {
        if (this.name) {
            return this.name;
        }
        if (typeof SDNLG_CONF != 'undefined') {
            var name = SDNLG_CONF.dict[this.id];
            if (name != undefined) {
                return name;
            }
        }
        return "";
    }

    /**
     * Get switch fantasy name from configuration data.
     * If there is no name return the switch ID.
     */
    this.get_name_or_id = function() {
        if (this.name) {
            return this.name;
        }
        if (typeof SDNLG_CONF != 'undefined') {
            var name = SDNLG_CONF.dict[this.id];
            if (name != undefined) {
                return name;
            }
        }
        return this.id;
    }

    /**
     * Get switch fantasy name from configuration data.
     * Return verbose name as: <ID> - <NAME>
     */
    this.get_verbose_name = function() {
        if (this.name) {
            return this.id + ' - ' + this.name;
        }
        if (typeof SDNLG_CONF != 'undefined') {
            var name = SDNLG_CONF.dict[this.id];
            if (name != undefined) {
                return this.id + ' - ' + name;
            }
        }
        return this.id;
    }

    /**
     * Get switch fantasy name from configuration data.
     * Return verbose name to be used on vis.js: <ID>\n<NAME>
     */
    this.get_node_name = function() {
        if (this.name) {
            return this.name;
        }

        if (typeof SDNLG_CONF != 'undefined') {
            var name = SDNLG_CONF.dict[this.id];
            if (name != undefined) {
                return name;
            }
        }
        return this.id;
    }

    this.get_port_by_id = function(node_id, p_id) {
        var p_id = node_id +"_"+ p_id;

        for (var x in this.ports){
            if(this.ports[x].id == p_id) {
                return this.ports[x];
            }
        }
        return null;
    }

    this.get_d3js_data = function() {
        node_id = this.id;
        node_obj = {id: node_id, dpid: node_id, name: node_id, data:this, label:this.get_node_name(), physics:true, mass:2, stroke_width:1, type:"switch", x:300, y:300};
        // Trace coloring
        if (typeof(node_obj.color)==='undefined') {
            node_obj.background_color = sdncolor.NODE_COLOR[node_obj.type];
        }
        return node_obj;
    }
}
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
 * Switch port representation.
 */
var Port = function(node_id, port_id, number, label, speed, uptime, status) {
    this.id = node_id + "_" + port_id;
    this.number = number;
    this.label = label;
    this.speed = speed;
    this.uptime = uptime;
    this.status = status;

    this.get_d3js_data = function() {
        node_id = this.id;
        node_obj = {id: node_id, name: null, data:this, label:this.label, physics:true, from_sw:'', to_sw:'', mass:2, stroke_width:1, type:"port"};
        node_obj.background_color = sdncolor.NODE_COLOR[node_obj.type];

        return node_obj;
    }

}
// Return switch port id if the class is used with strings
Port.prototype.toString = function(){ return this.id; };

/**
 * Domain representation.
 */
var Domain = function(domain_id, label) {
    this.id = domain_id;
    this.label = label;

    this.get_d3js_data = function() {
        node_obj = {id: this.id, name: null, data:this, label:this.label, physics:true, mass:2, stroke_width:1, type:"domain", x:300, y:300};
        node_obj.background_color = sdncolor.NODE_COLOR[node_obj.type];

        return node_obj;
    }

    this.get_name = function() {
        return this.label;
    }
}
Domain.create_id = function(p_domain_name) {
    /**
    * Create an Domain ID based on the domain_name.
    */
    if (p_domain_name == null || p_domain_name == "") {
        console.log("[ERROR] Domain.create_id p_domain_name is empty.");
        throw "[ERROR] Domain.create_id p_domain_name is empty.";
    }

    var domain_id = p_domain_name.replace(" ", "_");

    return "domain_" + domain_id;
}

/**
 * Host representation.
 */
var Host = function(node_id, port_id, label) {
    this.id = Host.create_id(node_id, port_id);
    this.label = label;

    this.get_d3js_data = function() {
        node_obj = {id: this.id, name: null, data:this, label:this.label, physics:true, mass:2, stroke_width:1, type:"host", x:300, y:300};
        node_obj.background_color = sdncolor.NODE_COLOR[node_obj.type];

        return node_obj;
    }

    this.get_name = function() {
        return this.label;
    }
}
Host.create_id = function(node_id, port_id) {
    if (node_id == null || node_id == "") {
        console.log("[ERROR] Host.create_id node_id empty.");
        throw "[ERROR] Host.create_id node_id empty.";
    }
    if (port_id == null || port_id == "") {
        console.log("[ERROR] Host.create_id port_id empty.");
        throw "[ERROR] Host.create_id port_id empty.";
    }

    return "host_" + node_id + "_" + port_id;
}

// Return switch port id if the class is used with strings
Port.prototype.toString = function(){ return this.id; };
