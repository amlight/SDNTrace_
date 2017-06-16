#!/usr/bin/env bash

PROTO='-O OpenFlow10'

if [ ! -z $1  ]; then
    PROTO='-O OpenFlow13'
fi

# From h2 to h7 - ok
ovs-ofctl add-flow s5  "in_port=4,dl_vlan=200 actions=output:2" $PROTO
ovs-ofctl add-flow s2  "in_port=2,dl_vlan=200 actions=output:3" $PROTO
ovs-ofctl add-flow s4 "in_port=4,dl_vlan=200 actions=output:3" $PROTO

ovs-ofctl add-flow s20 "in_port=2,dl_vlan=200 actions=strip_vlan,output:1" $PROTO

#From h7 to h2 - ok
ovs-ofctl add-flow s20 "in_port=1 actions=mod_vlan_vid:200,output:2" $PROTO
ovs-ofctl add-flow s19 "in_port=1,dl_vlan=200 actions=output:2" $PROTO
ovs-ofctl add-flow s17 "in_port=4,dl_vlan=200 actions=output:3" $PROTO
ovs-ofctl add-flow s8  "in_port=3,dl_vlan=200 actions=output:2" $PROTO
ovs-ofctl add-flow s7  "in_port=2,dl_vlan=200 actions=output:1" $PROTO

# From h3 to s7 - loop
ovs-ofctl add-flow s4 "in_port=1 actions=mod_vlan_vid:300,output:3" $PROTO
ovs-ofctl add-flow s6 "in_port=1,dl_vlan=300 actions=output:2" $PROTO
ovs-ofctl add-flow s7 "in_port=1,dl_vlan=300 actions=output:2" $PROTO
ovs-ofctl add-flow s8 "in_port=2,dl_vlan=300 actions=output:2" $PROTO
ovs-ofctl add-flow s7 "in_port=2,dl_vlan=300 actions=output:2" $PROTO
