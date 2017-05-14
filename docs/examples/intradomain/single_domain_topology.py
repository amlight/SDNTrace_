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


ip = '192.168.56.1'


def single_domain():

    """Create a network from semi-scratch with multiple controllers."""
    net = Mininet(topo=None, build=False)

    # Add switches
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')
    s4 = net.addSwitch('s4')
    s5 = net.addSwitch('s5')

    # Add links
    net.addLink(s2, s3)
    net.addLink(s2, s1)
    net.addLink(s3, s1)
    net.addLink(s3, s5)
    net.addLink(s5, s4)
    net.addLink(s4, s1)

    # Add hosts
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')

    # Add links to switches
    net.addLink(s2, h3)
    net.addLink(s4, h2)
    net.addLink(s1, h1)

    ctrl = net.addController('ctrl', controller=RemoteController, ip=ip, port=6633)

    net.build()
    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')  # for CLI output
    Cleanup.cleanup()
    single_domain()
