"""
    Inter-domain demo topology
"""

from mininet.net import Mininet
from mininet.node import RemoteController, Host
from mininet.cli import CLI


def InterDomain():
    """

    """
    net = Mininet(topo=None, build=False)

    # RNP
    s1 = net.addSwitch('s1', listenPort=6601, mac='01:00:00:00:00:01')
    s2 = net.addSwitch('s2', listenPort=6602, mac='01:00:00:00:00:02')
    s3 = net.addSwitch('s3', listenPort=6603, mac='01:00:00:00:00:03')
    s4 = net.addSwitch('s4', listenPort=6604, mac='01:00:00:00:00:04')
    s5 = net.addSwitch('s5', listenPort=6605, mac='01:00:00:00:00:05')
    h1 = net.addHost('h1', mac='dd:00:00:00:00:11')
    h3 = net.addHost('h3', mac='dd:00:00:00:00:13')

    net.addLink(s1, s2, port1=2, port2=1)
    net.addLink(s1, s3, port1=3, port2=1)
    net.addLink(s2, s4, port1=3, port2=4)
    net.addLink(s2, s5, port1=2, port2=2)
    net.addLink(s4, s5, port1=2, port2=3)
    net.addLink(s3, s5, port1=2, port2=1)
    net.addLink(h1, s1, port1=1, port2=1)
    net.addLink(h3, s4, port1=1, port2=1)

    rnpctl = net.addController('rnptrace', controller=RemoteController,
                                ip='190.103.187.55', port=9901)

    # RedClara
    s6 = net.addSwitch('s6', listenPort=6606, mac='02:00:00:00:00:01')
    s7 = net.addSwitch('s7', listenPort=6607, mac='02:00:00:00:00:02')
    s8 = net.addSwitch('s8', listenPort=6608, mac='02:00:00:00:00:03')

    h5 = net.addHost('h5', mac='dd:00:00:00:00:15')

    net.addLink(s6, s7, port1=2, port2=1)
    net.addLink(s7, s8, port1=2, port2=2)
    net.addLink(h5, s8, port1=1, port2=1)

    claractl = net.addController('claratrace', controller=RemoteController,
                                 ip='190.103.187.55', port=9902)

    # Inter-domain
    net.addLink(s4, s6, port1=3, port2=1)

    net.build()
    print "net.build"

    s1.start([rnpctl])
    s2.start([rnpctl])
    s3.start([rnpctl])
    s4.start([rnpctl])
    s5.start([rnpctl])
    s6.start([claractl])
    s7.start([claractl])
    s8.start([claractl])

    net.start()
    print "net.start"
    CLI(net)
    print "CLI(net)"
    net.stop()
    print "net.stop"

if __name__ == '__main__':
    InterDomain()