#!/bin/bash

PROTO=" -OOpenFlow10"

if [ ! -z $1  ]; then
    ovs-vsctl set Bridge s1 protocols=OpenFlow13
    ovs-vsctl set Bridge s2 protocols=OpenFlow13
    ovs-vsctl set Bridge s3 protocols=OpenFlow13
    ovs-vsctl set Bridge s4 protocols=OpenFlow13
    ovs-vsctl set Bridge s5 protocols=OpenFlow13
    ovs-vsctl set Bridge s6 protocols=OpenFlow13
    ovs-vsctl set Bridge s7 protocols=OpenFlow13
    ovs-vsctl set Bridge s8 protocols=OpenFlow13
    ovs-vsctl set Bridge s16 protocols=OpenFlow13
    ovs-vsctl set Bridge s17 protocols=OpenFlow13
    ovs-vsctl set Bridge s18 protocols=OpenFlow13
    PROTO=" -OOpenFlow13"
fi

ovs-vsctl set Bridge s1 other-config:dp-desc=s1
ovs-vsctl set Bridge s2 other-config:dp-desc=s2
ovs-vsctl set Bridge s3 other-config:dp-desc=s3
ovs-vsctl set Bridge s4 other-config:dp-desc=s4
ovs-vsctl set Bridge s5 other-config:dp-desc=s5
ovs-vsctl set Bridge s6 other-config:dp-desc=s6
ovs-vsctl set Bridge s7 other-config:dp-desc=s7
ovs-vsctl set Bridge s8 other-config:dp-desc=s8
ovs-vsctl set Bridge s16 other-config:dp-desc=s16
ovs-vsctl set Bridge s17 other-config:dp-desc=s17
ovs-vsctl set Bridge s18 other-config:dp-desc=s18

ovs-vsctl set-controller s1 tcp:190.103.187.55:9901
ovs-vsctl set-controller s2 tcp:190.103.187.55:9901
ovs-vsctl set-controller s3 tcp:190.103.187.55:9901
ovs-vsctl set-controller s4 tcp:190.103.187.55:9901
ovs-vsctl set-controller s5 tcp:190.103.187.55:9901
ovs-vsctl set-controller s6 tcp:190.103.187.55:9902
ovs-vsctl set-controller s7 tcp:190.103.187.55:9902
ovs-vsctl set-controller s8 tcp:190.103.187.55:9902
ovs-vsctl set-controller s16 tcp:190.103.187.55:9903
ovs-vsctl set-controller s17 tcp:190.103.187.55:9903
ovs-vsctl set-controller s18 tcp:190.103.187.55:9903

ovs-ofctl del-flows s1 $PROTO
ovs-ofctl del-flows s2 $PROTO
ovs-ofctl del-flows s3 $PROTO
ovs-ofctl del-flows s4 $PROTO
ovs-ofctl del-flows s5 $PROTO
ovs-ofctl del-flows s6 $PROTO
ovs-ofctl del-flows s7 $PROTO
ovs-ofctl del-flows s8 $PROTO
ovs-ofctl del-flows s16 $PROTO
ovs-ofctl del-flows s17 $PROTO
ovs-ofctl del-flows s18 $PROTO

# From h1 to h5 - ok
ovs-ofctl add-flow s1 "in_port=1 actions=mod_vlan_vid:200,output:2" $PROTO
ovs-ofctl add-flow s2 "in_port=1,dl_vlan=200 actions=output:3" $PROTO
ovs-ofctl add-flow s4 "in_port=4,dl_vlan=200 actions=output:3" $PROTO
ovs-ofctl add-flow s6 "in_port=1,dl_vlan=200 actions=output:2" $PROTO
ovs-ofctl add-flow s7 "in_port=1,dl_vlan=200 actions=output:2" $PROTO
ovs-ofctl add-flow s8 "in_port=2,dl_vlan=200 actions=output:3" $PROTO
ovs-ofctl add-flow s17 "in_port=3,dl_vlan=200 actions=output:2" $PROTO
ovs-ofctl add-flow s18 "in_port=2,dl_vlan=200 actions=strip_vlan,output:1" $PROTO

#From h5 to h1 - ok
ovs-ofctl add-flow s18 "in_port=1 actions=mod_vlan_vid:200,output:2" $PROTO
ovs-ofctl add-flow s17 "in_port=2,dl_vlan=200 actions=output:3" $PROTO
ovs-ofctl add-flow s8 "in_port=3,dl_vlan=200 actions=output:2" $PROTO
ovs-ofctl add-flow s7 "in_port=2,dl_vlan=200 actions=output:1" $PROTO
ovs-ofctl add-flow s6 "in_port=2,dl_vlan=200 actions=output:1" $PROTO
ovs-ofctl add-flow s4 "in_port=3,dl_vlan=200 actions=output:4" $PROTO
ovs-ofctl add-flow s2 "in_port=3,dl_vlan=200 actions=output:1" $PROTO
ovs-ofctl add-flow s1 "in_port=2,dl_vlan=200 actions=strip_vlan,output:1" $PROTO

# From h3 to s7 - loop
ovs-ofctl add-flow s4 "in_port=1 actions=mod_vlan_vid:300,output:3" $PROTO
ovs-ofctl add-flow s6 "in_port=1,dl_vlan=300 actions=output:2" $PROTO
ovs-ofctl add-flow s7 "in_port=1,dl_vlan=300 actions=output:2" $PROTO
ovs-ofctl add-flow s8 "in_port=2,dl_vlan=300 actions=output:2" $PROTO
ovs-ofctl add-flow s7 "in_port=2,dl_vlan=300 actions=output:2" $PROTO
