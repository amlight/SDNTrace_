# SDNTrace
Install Ryu [https://osrg.github.io/ryu/]

    pip install ryu


Edit the Ryu config file:

    sudo vim /usr/local/etc/ryu/ryu.conf

with the parameters

    wsapi_port=8182
    ofp_tcp_listen_port=9933

Add a log method to SDNTrace class


# Mininet
Install mininet to make tests in development environment.
    apt-get install mininet

Mininet example:
    sudo mn --topo linear,4 --mac --controller=remote,ip=127.0.0.1:9933


# Testing the SDN trace
You can use a Firefox Rest plugin to test the trace response.
Send a PUT request to:

    http://127.0.0.1:8182/sdntrace/trace

Send a json mime type data:
    {"trace":{"switch":{"dpid":"0000000000000001","in_port":1},"eth":{"dl_vlan":100}}}
