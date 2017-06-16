var DEBUG = false;

/**
 * MOCK object to store all the mock data.
 */
var MOCK = {};

// Mock json switch list structures. Used for testing purposes.
/** @constant */
MOCK.JSON_SWITCHES = '[' +
    '{"capabilities": "", "dpid": "0000000000000001", "n_ports": 8, "n_tables": 5},' +
    '{"capabilities": "", "dpid": "0000000000000002", "n_ports": 16, "n_tables": 5},' +
    '{"capabilities": "", "dpid": "0000000000000003", "n_ports": 23, "n_tables": 5},' +
    '{"capabilities": "", "dpid": "0000000000000004", "n_ports": 8, "n_tables": 5},' +
    '{"capabilities": "", "dpid": "0000000000000005", "n_ports": 8, "n_tables": 5},' +
    '{"capabilities": "", "dpid": "0000000000000006", "n_ports": 16, "n_tables": 5},' +
    '{"capabilities": "", "dpid": "0000000000000007", "n_ports": 8, "n_tables": 5}' +
    ']';

/** @constant */
MOCK.JSON_SDNTRACE_SWITCHES = '[' +
    '"0000000000000001", "0000000000000002", "0000000000000003", "0000000000000004", "0000000000000005", "0000000000000006"' +
    ']';

/** @constant */
MOCK.JSON_SDNTRACE_SWITCH_INFO =
    '{"switch_color": "1", "datapath_id": "0000000000000001", "openflow_version": "1.0", "number_flows": 0, "switch_vendor": "Nicira, Inc.", "tcp_port": 52320, "ip_address": "190.103.187.56", "switch_name": "s1"}';

// Mock json topology structure. Used for testing purposes.
/** @constant */
MOCK.JSON_TOPOLOGY = '[' +
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

/** @constant */
MOCK.JSON_TOPOLOGY_TRACE = '{' +
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
/** @constant */
MOCK.JSON_SWITCH_PORTS = '[' +
    '{ "name": "10Gigabit1", "port_no": 1, "speed": 10000000000, "uptime": 726558 },' +
    '{ "name": "10Gigabit2", "port_no": 2, "speed": 10000000000, "uptime": 614493 },' +
    '{ "name": "10Gigabit3", "port_no": 3, "speed": 10000000000, "uptime": 464014 },' +
    '{ "name": "10Gigabit4", "port_no": 4, "speed": 10000000000, "uptime": 997827 },' +
    '{ "name": "10Gigabit5", "port_no": 5, "speed": 10000000000, "uptime": 632296 },' +
    '{ "name": "10Gigabit6", "port_no": 6, "speed": 10000000000, "uptime": 482803 },' +
    '{ "name": "10Gigabit7", "port_no": 7, "speed": 10000000000, "uptime": 1007698},' +
    '{ "name": "10Gigabit8", "port_no": 8, "speed": 10000000000, "uptime": 418707 }' +
    ']';

/** @constant */
MOCK.JSON_SDNTRACE_SWITCH_PORTS = '{' +
    '"1": {"speed": "10GB_FD", "name": "s1-eth1", "port_no": 1, "status": "up" },' +
    '"2": {"speed": "10GB_FD", "name": "s1-eth2", "port_no": 2, "status": "up" },' +
    '"3": {"speed": "10GB_FD", "name": "s1-eth3", "port_no": 3, "status": "up"},' +
    '"4": {"speed": "10GB_FD", "name": "s1-eth4", "port_no": 4, "status": "up"}' +
    '}';

/** @constant */
MOCK.JSON_FLOWS = '{"number_flows": 4, "flows": [{"actions": [{"max_len": 65509, "type": "OFPActionOutput(0)", "port": 65533}], "idle_timeout": 0, "cookie": 2000002, "priority": 50000, "hard_timeout": 0, "byte_count": 0, "duration_nsec": 6000000, "packet_count": 0, "duration_sec": 100, "table_id": 0, "match": {"wildcards": 3678459, "dl_src": "ee:ee:ee:ee:ee:02"}}, {"actions": [{"type": "OFPActionStripVlan(3)"}, {"max_len": 0, "type": "OFPActionOutput(0)", "port": 1}], "idle_timeout": 0, "cookie": 0, "priority": 32768, "hard_timeout": 0, "byte_count": 0, "duration_nsec": 906000000, "packet_count": 0, "duration_sec": 142, "table_id": 0, "match": {"wildcards": 3678460, "dl_vlan": 200, "in_port": 2}}, {"actions": [{"type": "OFPActionVlanVid(1)", "vlan_vid": 200}, {"max_len": 0, "type": "OFPActionOutput(0)", "port": 2}], "idle_timeout": 0, "cookie": 0, "priority": 32768, "hard_timeout": 0, "byte_count": 0, "duration_nsec": 933000000, "packet_count": 0, "duration_sec": 142, "table_id": 0, "match": {"wildcards": 3678462, "in_port": 1}}, {"actions": [{"max_len": 65509, "type": "OFPActionOutput(0)", "port": 65533}], "idle_timeout": 0, "cookie": 0, "priority": 1, "hard_timeout": 0, "byte_count": 2760, "duration_nsec": 492000000, "packet_count": 46, "duration_sec": 112, "table_id": 0, "match": {"wildcards": 3678437, "dl_type": 35020, "dl_dst": "01:80:c2:00:00:0e", "dl_vlan": 100}}], "dpid": "0000000000000001"}';

// Mock json trace
/** @constant */
MOCK.JSON_TRACE = '80001';
/** @constant */
MOCK.JSON_TRACE_RESULT = '{"total_time": "0:00:03.520170","start_time": "2017-03-21 13:30:42.024902",'+
    '"result": ['+
    '{"time": "2017-03-21 13:30:42.024902","type": "starting","port": "s1-eth1","dpid": "0000000000000001"},'+
    '{"time": "0:00:00.510086","type": "trace","port": "s2-eth2","dpid": "0000000000000002"},'+
    '{"time": "0:00:01.012277","type": "trace","port": "s3-eth2","dpid": "0000000000000003"},'+
    '{"time": "0:00:01.514501","type": "trace","port": "s4-eth2","dpid": "0000000000000004"},'+
    '{"msg": null,"reason": "done","type": "last","time": "0:00:03.519943"}],'+
    '"request_id": 80001}';

/** @constant */
MOCK.JSON_TRACE_RESULT = '{"total_time": "0:00:03.520170","start_time": "2017-03-21 13:30:42.024902",'+
    '"result": ['+
    '{"time": "2017-03-21 13:30:42.024902","type": "starting","port": "s1-eth1","dpid": "0000000000000001"},'+
    '{"time": "0:00:00.510086","type": "trace","port": "s2-eth2","dpid": "0000000000000002"},'+
    '{"time": "0:00:01.012277","type": "trace","port": "s3-eth2","dpid": "0000000000000003"},'+
    '{"time": "0:00:01.514501","type": "trace","port": "s4-eth2","dpid": "0000000000000004"},'+
    '{"msg": null,"reason": "done","type": "last","time": "0:00:03.519943"}],'+
    '"request_id": 80001}';

/** @constant */
MOCK.JSON_TRACE_RESULT_INTERDOMAIN = '{"total_time": "0:00:05.019943","start_time": "2017-03-21 13:30:42.024902",'+
    '"result": ['+
    '{"time": "2017-03-21 13:30:42.024902","type": "starting","port": "s1-eth1","dpid": "0000000000000001"},'+
    '{"time": "0:00:00.510086","type": "trace","port": "s2-eth2","dpid": "0000000000000002"},'+
    '{"time": "0:00:01.012277","type": "trace","port": "s3-eth2","dpid": "0000000000000003"},'+
    '{"time": "0:00:02.514501","type": "intertrace", "domain":"Domain B"},'+
    '{"time": "0:00:04.014501","type": "intertrace", "domain":"Domain C"},'+
    '{"time": "0:00:04.514501","type": "trace","port": "s8-eth1","dpid": "0000000000000101"},'+
    '{"msg": null,"reason": "done","type": "last","time": "0:00:05.019943"}],'+
    '"request_id": 80001}';

/** @constant */
MOCK.JSON_TRACE_RESULT_PART1 = '{"total_time": "0:00:00","start_time": "2017-03-21 13:30:42.024902",'+
    '"result": ['+
    '{"time": "2017-03-21 13:30:42.024902","type": "starting","port": "s1-eth1","dpid": "0000000000000001"}],'+
    '"request_id": 80001}';

/** @constant */
MOCK.JSON_TRACE_RESULT_PART2 = '{"total_time": "0:00.510086","start_time": "2017-03-21 13:30:42.024902",'+
    '"result": ['+
    '{"time": "2017-03-21 13:30:42.024902","type": "starting","port": "s1-eth1","dpid": "0000000000000001"},'+
    '{"time": "0:00:00.510086","type": "trace","port": "s2-eth2","dpid": "0000000000000002"}],'+
    '"request_id": 80001}';

/** @constant */
MOCK.JSON_TRACE_RESULT_PART3 = '{"total_time": "0:00:01.514501","start_time": "2017-03-21 13:30:42.024902",'+
    '"result": ['+
    '{"time": "2017-03-21 13:30:42.024902","type": "starting","port": "s1-eth1","dpid": "0000000000000001"},'+
    '{"time": "0:00:00.510086","type": "trace","port": "s2-eth2","dpid": "0000000000000002"},'+
    '{"time": "0:00:01.012277","type": "trace","port": "s3-eth2","dpid": "0000000000000003"},'+
    '{"time": "0:00:01.514501","type": "trace","port": "s4-eth2","dpid": "0000000000000004"}],'+
    '"request_id": 80001}';

/** @constant */
MOCK.JSON_TRACE_RESULT_PART4 = '{"total_time": "0:00:03.520170","start_time": "2017-03-21 13:30:42.024902",'+
    '"result": ['+
    '{"time": "2017-03-21 13:30:42.024902","type": "starting","port": "s1-eth1","dpid": "0000000000000001"},'+
    '{"time": "0:00:00.510086","type": "trace","port": "s2-eth2","dpid": "0000000000000002"},'+
    '{"time": "0:00:01.012277","type": "trace","port": "s3-eth2","dpid": "0000000000000003"},'+
    '{"time": "0:00:01.514501","type": "trace","port": "s4-eth2","dpid": "0000000000000004"},'+
    '{"msg": null,"reason": "done","type": "last","time": "0:00:03.519943"}],'+
    '"request_id": 80001}';
    
/** @constant */
MOCK.JSON_TRACE_RESULT_PART4_ERROR = '{"total_time": "0:00:03.520170","start_time": "2017-03-21 13:30:42.024902",'+
    '"result": ['+
    '{"time": "2017-03-21 13:30:42.024902","type": "starting","port": "s1-eth1","dpid": "0000000000000001"},'+
    '{"time": "0:00:00.510086","type": "trace","port": "s2-eth2","dpid": "0000000000000002"},'+
    '{"time": "0:00:01.012277","type": "trace","port": "s3-eth2","dpid": "0000000000000003"},'+
    '{"time": "0:00:01.514501","type": "trace","port": "s4-eth2","dpid": "0000000000000004"},'+
    '{"msg": "Unknown error","reason": "error","type": "last","time": "0:00:03.519943"}],'+
    '"request_id": 80001}';
    
/** @constant */
MOCK.JSON_TRACE_RESULT_PART4_LOOP = '{"total_time": "0:00:03.520170","start_time": "2017-03-21 13:30:42.024902",'+
    '"result": ['+
    '{"time": "2017-03-21 13:30:42.024902","type": "starting","port": "s1-eth1","dpid": "0000000000000001"},'+
    '{"time": "0:00:00.510086","type": "trace","port": "s2-eth2","dpid": "0000000000000002"},'+
    '{"time": "0:00:01.012277","type": "trace","port": "s3-eth2","dpid": "0000000000000003"},'+
    '{"time": "0:00:01.514501","type": "trace","port": "s4-eth2","dpid": "0000000000000004"},'+
    '{"msg": null,"reason": "loop","type": "last","time": "0:00:03.519943"}],'+
    '"request_id": 80001}';
