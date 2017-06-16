#!/bin/bash

SDNTRACE_IP=$1

SWITCHES="s1 s2 s3 s4 s5"

if [ ! -z $1  ]; then
    PROTO="OpenFlow13"
else
    PROTO="OpenFlow10"
fi

for sw in $SWITCHES; do
    ovs-vsctl set Bridge $sw protocols=$PROTO
    ovs-ofctl del-flows $sw -O $PROTO
    ovs-vsctl set Bridge $sw other-config:dp-desc=$sw
done