#!/usr/bin/python

"""
This example creates a multi-controller network from semi-scratch by
using the net.add*() API and manually starting the switches and controllers.
"""

from mininet.clean import Cleanup
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel


ip_sdntrace = '190.103.187.55'


def int2dpid( dpid ):
   try:
      dpid = hex( dpid )[ 2: ]
      dpid = '0' * ( 16 - len( dpid ) ) + dpid
      return dpid
   except IndexError:
      raise Exception( 'Unable to derive default datapath ID - '
                       'please either specify a dpid or use a '
		               'canonical switch name such as s23.' )


def multiControllerNet():

    "Create a network from semi-scratch with multiple controllers."
    net = Mininet(topo=None, build=False)

    # Domain1 controller, hosts and switches
    Domain1ctrl = net.addController('domain1ctlr', controller=RemoteController, ip=ip_sdntrace, port=16601)
    Domain1host01 = net.addHost('h1', mac='dd:00:00:00:00:01')
    Domain1host03 = net.addHost('h3', mac='dd:00:00:00:00:03')
    Domain1switch01 = net.addSwitch('s1', listenPort=6601, dpid=int2dpid(1))
    Domain1switch02 = net.addSwitch('s2', listenPort=6602, dpid=int2dpid(2))
    Domain1switch03 = net.addSwitch('s3', listenPort=6603, dpid=int2dpid(3))
    Domain1switch04 = net.addSwitch('s4', listenPort=6604, dpid=int2dpid(4))
    Domain1switch05 = net.addSwitch('s5', listenPort=6605, dpid=int2dpid(5))

    # Domain1 local links
    net.addLink(Domain1host01, Domain1switch01, port1=1, port2=1)
    net.addLink(Domain1host03, Domain1switch04, port1=1, port2=1)
    net.addLink(Domain1switch01, Domain1switch02, port1=2, port2=1)
    net.addLink(Domain1switch01, Domain1switch03, port1=3, port2=1)
    net.addLink(Domain1switch02, Domain1switch04, port1=3, port2=4)
    net.addLink(Domain1switch02, Domain1switch05, port1=2, port2=2)
    net.addLink(Domain1switch03, Domain1switch05, port1=2, port2=1)
    net.addLink(Domain1switch04, Domain1switch05, port1=2, port2=3)

    # Domain3 controller, hosts and switches
    Domain3ctrl = net.addController('domain3ctlr', controller=RemoteController, ip=ip_sdntrace, port=16609)
    Domain3host02 = net.addHost('h2', mac='dd:00:00:00:00:02')
    Domain3switch09 = net.addSwitch('s9', listenPort=6609, dpid=int2dpid(9))
    Domain3switch10 = net.addSwitch('s10', listenPort=6610, dpid=int2dpid(10))

    # Domain3 local links
    net.addLink(Domain3host02, Domain3switch09, port1=1, port2=1)
    net.addLink(Domain3switch09, Domain3switch10, port1=2, port2=1)

    # Domain4 controller, hosts and switches
    Domain4ctrl = net.addController('domain4ctlr', controller=RemoteController, ip=ip_sdntrace, port=16611)
    Domain4switch11 = net.addSwitch('s11', listenPort=6611, dpid=int2dpid(11))
    Domain4switch12 = net.addSwitch('s12', listenPort=6612, dpid=int2dpid(12))
    Domain4switch13 = net.addSwitch('s13', listenPort=6613, dpid=int2dpid(13))
    Domain4switch14 = net.addSwitch('s14', listenPort=6614, dpid=int2dpid(14))
    Domain4switch15 = net.addSwitch('s15', listenPort=6615, dpid=int2dpid(15))
    Domain4host04 = net.addHost('h4', mac='dd:00:00:00:00:04')
 
    # Domain4 local links
    net.addLink(Domain4switch11, Domain4switch12, port1=2, port2=1)
    net.addLink(Domain4switch11, Domain4switch14, port1=3, port2=2)
    net.addLink(Domain4switch12, Domain4switch13, port1=3, port2=1)
    net.addLink(Domain4switch12, Domain4switch14, port1=2, port2=4)
    net.addLink(Domain4switch13, Domain4switch15, port1=2, port2=4)
    net.addLink(Domain4switch14, Domain4switch15, port1=3, port2=1)
    net.addLink(Domain4host04, Domain4switch15, port1=1, port2=2)

    # Domain2 hosts and switches
    Domain2ctrl = net.addController('domain2ctlr', controller=RemoteController, ip=ip_sdntrace, port=16606)
    Domain2switch06 = net.addSwitch('s6', listenPort=6606, dpid=int2dpid(6))
    Domain2switch07 = net.addSwitch('s7', listenPort=6607, dpid=int2dpid(7))
    Domain2switch08 = net.addSwitch('s8', listenPort=6608, dpid=int2dpid(8))
    Domain2host05 = net.addHost('h5', mac='dd:00:00:00:00:05')

    # Domain2 local links
    net.addLink(Domain2switch06, Domain2switch07, port1=2, port2=1)
    net.addLink(Domain2switch07, Domain2switch08, port1=2, port2=2)
    net.addLink(Domain2host05, Domain2switch08, port1=1, port2=1)

    # Domain6 controller, hosts and switches
    Domain6ctrl = net.addController('domain6ctlr', controller=RemoteController, ip=ip_sdntrace, port=16616)
    Domain6switch16 = net.addSwitch('s16', listenPort=6616, dpid=int2dpid(16))
    Domain6switch17 = net.addSwitch('s17', listenPort=6617, dpid=int2dpid(17))
    Domain6switch18 = net.addSwitch('s18', listenPort=6618, dpid=int2dpid(18))
    Domain6host06 = net.addHost('h6', mac='dd:00:00:00:00:06')

    # Domain6 local links
    net.addLink(Domain6switch16, Domain6switch17, port1=1, port2=1)
    net.addLink(Domain6switch16, Domain6switch18, port1=2, port2=3)
    net.addLink(Domain6switch17, Domain6switch18, port1=2, port2=2)
    net.addLink(Domain6host06, Domain6switch18, port1=1, port2=1)

    # Domain5 controller, hosts and switches
    Domain5ctrl = net.addController('domain5ctrl', controller=RemoteController, ip=ip_sdntrace, port=16619)
    Domain5switch19 = net.addSwitch('s19', listenPort=6619, dpid=int2dpid(19))
    Domain5switch20 = net.addSwitch('s20', listenPort=6620, dpid=int2dpid(20))
    Domain5host07 = net.addHost('h7', mac='dd:00:00:00:00:07')

    # Domain5 local links
    net.addLink(Domain5host07, Domain5switch20, port1=1, port2=1)
    net.addLink(Domain5switch19, Domain5switch20, port1=1, port2=2)

    # Inter-domain
    # Domain1 - Domain2
    net.addLink(Domain1switch04, Domain2switch06, port1=3, port2=1)

    # Domain1 - Domain4
    net.addLink(Domain1switch05, Domain4switch11, port1=4, port2=1)

    # Domain3 - Domain4
    net.addLink(Domain3switch10, Domain4switch14, port1=2, port2=1)

    # Domain2 - Domain6
    net.addLink(Domain2switch08, Domain6switch17, port1=3, port2=3)

    # Domain2 - Domain4
    net.addLink(Domain2switch07, Domain4switch13, port1=3, port2=3)

    # Domain4 - Domain6
    net.addLink(Domain4switch15, Domain6switch16, port1=3, port2=3)

    # Domain6 - Domain5
    net.addLink(Domain6switch17, Domain5switch19, port1=4, port2=2)

    net.build()

    # Start switches
    Domain1switch01.start([Domain1ctrl])
    Domain1switch02.start([Domain1ctrl])
    Domain1switch03.start([Domain1ctrl])
    Domain1switch04.start([Domain1ctrl])
    Domain1switch05.start([Domain1ctrl])
    Domain2switch06.start([Domain2ctrl])
    Domain2switch07.start([Domain2ctrl])
    Domain2switch08.start([Domain2ctrl])
    Domain3switch09.start([Domain3ctrl])
    Domain3switch10.start([Domain3ctrl])
    Domain4switch11.start([Domain4ctrl])
    Domain4switch12.start([Domain4ctrl])
    Domain4switch13.start([Domain4ctrl])
    Domain4switch14.start([Domain4ctrl])
    Domain4switch15.start([Domain4ctrl])
    Domain6switch16.start([Domain6ctrl])
    Domain6switch17.start([Domain6ctrl])
    Domain6switch18.start([Domain6ctrl])
    Domain5switch19.start([Domain5ctrl])
    Domain5switch20.start([Domain5ctrl])

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )  # for CLI output
    Cleanup.cleanup()
    multiControllerNet()
