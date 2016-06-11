# S1
ovs-ofctl add-flow tcp:192.168.56.103:6634 "in_port=1 action=mod_vlan_vid=102,output:2"
ovs-ofctl add-flow tcp:192.168.56.103:6634 "in_port=2,dl_vlan=101 action=strip_vlan,output:1"

# S2
ovs-ofctl add-flow tcp:192.168.56.103:6635 "in_port=2,dl_vlan=102 action=mod_vlan_vid=103,output:3"
ovs-ofctl add-flow tcp:192.168.56.103:6635 "in_port=3,dl_vlan=102 action=mod_vlan_vid=101,output:2"

# S3
ovs-ofctl add-flow tcp:192.168.56.103:6636 "in_port=2,dl_vlan=103 action=mod_vlan_vid=104,output:3"
ovs-ofctl add-flow tcp:192.168.56.103:6636 "in_port=3,dl_vlan=103 action=mod_vlan_vid=102,output:2"

# S4
ovs-ofctl add-flow tcp:192.168.56.103:6637 "in_port=2,dl_vlan=104 action=strip_vlan,output:1"
ovs-ofctl add-flow tcp:192.168.56.103:6637 "in_port=1 action=mod_vlan_vid=103,output:2"