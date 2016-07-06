# AmLight Topology with loop
# It is not possible to ping from clH2 to miH3
# clH2 ping miH3

#DPID Name Port
#01 mia1 6636
#02 mia2 6637
#03 sol3 6638
#04 ch4 6634
#05 ch5 6635

#ch4-eth3<->sol3-eth4 (OK OK)
#ch5-eth2<->ch4-eth2 (OK OK)

#mia1-eth2<->mia2-eth1 (OK OK)
#mia1-eth3<->sol3-eth2 (OK OK)
#mia2-eth3<->ch5-eth1 (OK OK)
#mia2-eth2<->sol3-eth3 (OK OK)

#ch4-eth1<->clH2-eth0 (OK OK)
#mia1-eth1<->miH3-eth0 (OK OK)
#sol3-eth1<->spH1-eth0 (OK OK)


# circuit from miH3 -> clH2 --> LOOPED!
# mia1
ovs-ofctl add-flow tcp:192.168.56.103:6636 "in_port=1 action=mod_vlan_vid=101,output:2"

# mia2
ovs-ofctl add-flow tcp:192.168.56.103:6637 "in_port=1,dl_vlan=101 action=mod_vlan_vid=102,output:2"

# sol3
ovs-ofctl add-flow tcp:192.168.56.103:6638 "in_port=3,dl_vlan=102 action=mod_vlan_vid=103,output:2"

# mia1
ovs-ofctl add-flow tcp:192.168.56.103:6636 "in_port=3,dl_vlan=103 action=mod_vlan_vid=101,output:2"


# circuit from clH2 -> miH3 --> OK!
# ch4
ovs-ofctl add-flow tcp:192.168.56.103:6634 "in_port=1 action=mod_vlan_vid=104,output:3"

# sol3
ovs-ofctl add-flow tcp:192.168.56.103:6638 "in_port=4,dl_vlan=104 action=mod_vlan_vid=103,output:3"

# mia2
ovs-ofctl add-flow tcp:192.168.56.103:6637 "in_port=2,dl_vlan=103 action=mod_vlan_vid=102,output:1"

# mia1
ovs-ofctl add-flow tcp:192.168.56.103:6636 "in_port=2,dl_vlan=102 action=strip_vlan,output:1"
