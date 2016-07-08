# AmLight Topology with loop
# It is not possible to ping from clH2 to miH3
# clH2 ping miH3

#DPID Name Port
#01 mia1 6636
#02 mia2 6637
#03 sol3 6638
#04 ch4 6634
#05 ch5 6635

# circuit from miH3 -> clH2 --> LOOPED!
# mia1
ovs-ofctl add-flow tcp:192.168.56.101:6636 "in_port=3 action=mod_vlan_vid=101,output:1"

# mia2
ovs-ofctl add-flow tcp:192.168.56.101:6637 "in_port=1,dl_vlan=101 action=mod_vlan_vid=102,output:2"

# sol3
ovs-ofctl add-flow tcp:192.168.56.101:6638 "in_port=2,dl_vlan=102 action=mod_vlan_vid=103,output:1"

# mia1
ovs-ofctl add-flow tcp:192.168.56.101:6636 "in_port=2,dl_vlan=103 action=mod_vlan_vid=101,output:1"


# circuit from clH2 -> miH3 --> OK!
# ch4
ovs-ofctl add-flow tcp:192.168.56.101:6634 "in_port=3 action=mod_vlan_vid=104,output:2"

# sol3
ovs-ofctl add-flow tcp:192.168.56.101:6638 "in_port=3,dl_vlan=104 action=mod_vlan_vid=103,output:2"

# mia2
ovs-ofctl add-flow tcp:192.168.56.101:6637 "in_port=2,dl_vlan=103 action=mod_vlan_vid=102,output:1"

# mia1
ovs-ofctl add-flow tcp:192.168.56.101:6636 "in_port=1,dl_vlan=102 action=strip_vlan,output:3"


