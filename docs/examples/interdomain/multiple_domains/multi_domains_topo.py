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

    # RNP controller, hosts and switches
    RNPctrl = net.addController('rnp', controller=RemoteController, ip=ip_sdntrace, port=16601)
    RNPhost01 = net.addHost('h1', mac='dd:00:00:00:00:01')
    RNPhost03 = net.addHost('h3', mac='dd:00:00:00:00:03')
    RNPswitch01 = net.addSwitch('s1', listenPort=6601, dpid=int2dpid(1))
    RNPswitch02 = net.addSwitch('s2', listenPort=6602, dpid=int2dpid(2))
    RNPswitch03 = net.addSwitch('s3', listenPort=6603, dpid=int2dpid(3))
    RNPswitch04 = net.addSwitch('s4', listenPort=6604, dpid=int2dpid(4))
    RNPswitch05 = net.addSwitch('s5', listenPort=6605, dpid=int2dpid(5))

    # RNP local links
    net.addLink(RNPhost01, RNPswitch01, port1=1, port2=1)
    net.addLink(RNPhost03, RNPswitch04, port1=1, port2=1)
    net.addLink(RNPswitch01, RNPswitch02, port1=2, port2=1)
    net.addLink(RNPswitch01, RNPswitch03, port1=3, port2=1)
    net.addLink(RNPswitch02, RNPswitch04, port1=3, port2=4)
    net.addLink(RNPswitch02, RNPswitch05, port1=2, port2=2)
    net.addLink(RNPswitch03, RNPswitch05, port1=2, port2=1)
    net.addLink(RNPswitch04, RNPswitch05, port1=2, port2=3)

    # ANSP controller, hosts and switches
    ANSPctrl = net.addController('ansp', controller=RemoteController, ip=ip_sdntrace, port=16609)
    ANSPhost02 = net.addHost('h2', mac='dd:00:00:00:00:02')
    ANSPswitch09 = net.addSwitch('s9', listenPort=6609, dpid=int2dpid(9))
    ANSPswitch10 = net.addSwitch('s10', listenPort=6610, dpid=int2dpid(10))

    # ANSP local links
    net.addLink(ANSPhost02, ANSPswitch09, port1=1, port2=1)
    net.addLink(ANSPswitch09, ANSPswitch10, port1=2, port2=1)

    # SouthernLight controller, hosts and switches
    SLIGHTctrl = net.addController('slight', controller=RemoteController, ip=ip_sdntrace, port=16611)
    SLIGHTswitch11 = net.addSwitch('s11', listenPort=6611, dpid=int2dpid(11))
    SLIGHTswitch12 = net.addSwitch('s12', listenPort=6612, dpid=int2dpid(12))
    SLIGHTswitch13 = net.addSwitch('s13', listenPort=6613, dpid=int2dpid(13))
    SLIGHTswitch14 = net.addSwitch('s14', listenPort=6614, dpid=int2dpid(14))
    SLIGHTswitch15 = net.addSwitch('s15', listenPort=6615, dpid=int2dpid(15))
    SLIGHThost04 = net.addHost('h4', mac='dd:00:00:00:00:04')
 
    # SouthernLight local links
    net.addLink(SLIGHTswitch11, SLIGHTswitch12, port1=2, port2=1)
    net.addLink(SLIGHTswitch11, SLIGHTswitch14, port1=3, port2=2)
    net.addLink(SLIGHTswitch12, SLIGHTswitch13, port1=3, port2=1)
    net.addLink(SLIGHTswitch12, SLIGHTswitch14, port1=2, port2=4)
    net.addLink(SLIGHTswitch13, SLIGHTswitch15, port1=2, port2=4)
    net.addLink(SLIGHTswitch14, SLIGHTswitch15, port1=3, port2=1)
    net.addLink(SLIGHThost04, SLIGHTswitch15, port1=1, port2=2)

    # CLARA hosts and switches
    CLARActrl = net.addController('clara', controller=RemoteController, ip=ip_sdntrace, port=16606)
    CLARAswitch06 = net.addSwitch('s6', listenPort=6606, dpid=int2dpid(6))
    CLARAswitch07 = net.addSwitch('s7', listenPort=6607, dpid=int2dpid(7))
    CLARAswitch08 = net.addSwitch('s8', listenPort=6608, dpid=int2dpid(8))
    CLARAhost05 = net.addHost('h5', mac='dd:00:00:00:00:05')

    # CLARA local links
    net.addLink(CLARAswitch06, CLARAswitch07, port1=2, port2=1)
    net.addLink(CLARAswitch07, CLARAswitch08, port1=2, port2=2)
    net.addLink(CLARAhost05, CLARAswitch08, port1=1, port2=1)

    # AmLight controller, hosts and switches
    AMLIGHTctrl = net.addController('amlight', controller=RemoteController, ip=ip_sdntrace, port=16616)
    AMLIGHTswitch16 = net.addSwitch('s16', listenPort=6616, dpid=int2dpid(16))
    AMLIGHTswitch17 = net.addSwitch('s17', listenPort=6617, dpid=int2dpid(17))
    AMLIGHTswitch18 = net.addSwitch('s18', listenPort=6618, dpid=int2dpid(18))
    AMLIGHThost06 = net.addHost('h6', mac='dd:00:00:00:00:06')

    # AmLight local links
    net.addLink(AMLIGHTswitch16, AMLIGHTswitch17, port1=1, port2=1)
    net.addLink(AMLIGHTswitch16, AMLIGHTswitch18, port1=2, port2=3)
    net.addLink(AMLIGHTswitch17, AMLIGHTswitch18, port1=2, port2=2)
    net.addLink(AMLIGHThost06, AMLIGHTswitch18, port1=1, port2=1)

    # Internet2 controller, hosts and switches
    I2ctrl = net.addController('i2', controller=RemoteController, ip=ip_sdntrace, port=16619)
    I2switch19 = net.addSwitch('s19', listenPort=6619, dpid=int2dpid(19))
    I2host07 = net.addHost('h7', mac='dd:00:00:00:00:07')

    # Internet2 local links
    net.addLink(I2host07, I2switch19, port1=1, port2=1)

    # Inter-domain
    # RNP - CLARA
    net.addLink(RNPswitch04, CLARAswitch06, port1=3, port2=1)

    # RNP - SouthernLight
    net.addLink(RNPswitch05, SLIGHTswitch11, port1=4, port2=1)

    # ANSP - SouthernLight
    net.addLink(ANSPswitch10, SLIGHTswitch14, port1=2, port2=1)

    # CLARA - AmLight
    net.addLink(CLARAswitch08, AMLIGHTswitch17, port1=3, port2=3)

    # CLARA - SouthernLight
    net.addLink(CLARAswitch07, SLIGHTswitch13, port1=3, port2=3)

    # SouthernLight - AmLight
    net.addLink(SLIGHTswitch15, AMLIGHTswitch16, port1=3, port2=3)

    # AmLight - Internet2
    net.addLink(AMLIGHTswitch17, I2switch19, port1=4, port2=2)

    net.build()

    # Start switches
    RNPswitch01.start([RNPctrl])
    RNPswitch02.start([RNPctrl])
    RNPswitch03.start([RNPctrl])
    RNPswitch04.start([RNPctrl])
    RNPswitch05.start([RNPctrl])
    CLARAswitch06.start([CLARActrl])
    CLARAswitch07.start([CLARActrl])
    CLARAswitch08.start([CLARActrl])
    ANSPswitch09.start([ANSPctrl])
    ANSPswitch10.start([ANSPctrl])
    SLIGHTswitch11.start([SLIGHTctrl])
    SLIGHTswitch12.start([SLIGHTctrl])
    SLIGHTswitch13.start([SLIGHTctrl])
    SLIGHTswitch14.start([SLIGHTctrl])
    SLIGHTswitch15.start([SLIGHTctrl])
    AMLIGHTswitch16.start([AMLIGHTctrl])
    AMLIGHTswitch17.start([AMLIGHTctrl])
    AMLIGHTswitch18.start([AMLIGHTctrl])
    I2switch19.start([I2ctrl]) 

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )  # for CLI output
    Cleanup.cleanup()
    multiControllerNet()
