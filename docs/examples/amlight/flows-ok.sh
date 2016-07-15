
# AmLight Topology with working flows
# It is possible to ping from clH2 to miH3
# clH2 ping miH3

#DPID Name Port
#01 mia1 6636
#02 mia2 6637
#05 ch5 6635
#03 sol3 6638
#04 ch4 6634


# IP,TCP,port=80
# ICMP
# ARP
# circuit from miH3 -> clH2
# mia1
ovs-ofctl add-flow tcp:192.168.56.103:6636 "in_port=3,ip,tcp,tp_dst=80 action=mod_vlan_vid=101,output:1"
ovs-ofctl add-flow tcp:192.168.56.103:6636 "in_port=3,icmp action=mod_vlan_vid=101,output:1"
ovs-ofctl add-flow tcp:192.168.56.103:6636 "in_port=3,arp action=mod_vlan_vid=101,output:1"
# mia2
ovs-ofctl add-flow tcp:192.168.56.103:6637 "in_port=1,dl_vlan=101 action=mod_vlan_vid=102,output:3"
# ch5
ovs-ofctl add-flow tcp:192.168.56.103:6635 "in_port=1,dl_vlan=102 action=mod_vlan_vid=105,output:2"
# ch4
ovs-ofctl add-flow tcp:192.168.56.103:6634 "in_port=1,dl_vlan=105 action=strip_vlan,output:3"

# circuit from clH2 -> miH3
# ch4
ovs-ofctl add-flow tcp:192.168.56.103:6634 "in_port=3,ip,tcp,tp_dst=80 action=mod_vlan_vid=104,output:1"
ovs-ofctl add-flow tcp:192.168.56.103:6634 "in_port=3,icmp action=mod_vlan_vid=104,output:1"
ovs-ofctl add-flow tcp:192.168.56.103:6634 "in_port=3,arp action=mod_vlan_vid=104,output:1"
# ch5
ovs-ofctl add-flow tcp:192.168.56.103:6635 "in_port=2,dl_vlan=104 action=mod_vlan_vid=105,output:1"
# mia2
ovs-ofctl add-flow tcp:192.168.56.103:6637 "in_port=3,dl_vlan=105 action=mod_vlan_vid=102,output:1"
# mia1
ovs-ofctl add-flow tcp:192.168.56.103:6636 "in_port=1,dl_vlan=102 action=strip_vlan,output:3"


# IP,TCP,port=25
# circuit from miH3 -> clH2
# mia1
ovs-ofctl add-flow tcp:192.168.56.103:6636 "in_port=3,ip,tcp,tp_dst=25 action=mod_vlan_vid=101,output:2"
# sol
ovs-ofctl add-flow tcp:192.168.56.103:6638 "in_port=1,dl_vlan=101 action=mod_vlan_vid=103,output:3"
# ch4
ovs-ofctl add-flow tcp:192.168.56.103:6634 "in_port=2,dl_vlan=103 action=strip_vlan,output:3"

# circuit from clH2 -> miH3
# ch4
ovs-ofctl add-flow tcp:192.168.56.103:6634 "in_port=3,ip,tcp,tp_dst=25 action=mod_vlan_vid=104,output:2"
# sol
ovs-ofctl add-flow tcp:192.168.56.103:6638 "in_port=3,dl_vlan=104 action=mod_vlan_vid=103,output:1"
# mia1
ovs-ofctl add-flow tcp:192.168.56.103:6636 "in_port=2,dl_vlan=103 action=strip_vlan,output:3"