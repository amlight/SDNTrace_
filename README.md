# SDNTrace

Coming soon

Configure
sudo vim /usr/local/etc/ryu/ryu.conf

with

wsapi_port=8182
ofp_tcp_listen_port=9933

create my own config file, including

PACKET_OUT_INTERVAL = 5
PUSH_COLORS_INTERVAL = 10
COLLECT_INTERVAL = 30
HAS_OFPP_TABLE_SUPPORT = True

Add a log method to SDNTrace class

clear old coloring flows left in case of controller restart
