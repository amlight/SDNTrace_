"""
    AmLight topology
    5 switches and 3 hosts
"""

from mininet.topo import Topo

class MyTopo( Topo ):

    def __init__( self ):
        # Initialize topology
        Topo.__init__( self )

        # Add switches
        spSwitch = self.addSwitch( 'sol3' )
        mia1Switch = self.addSwitch( 'mia1' )
        mia2Switch = self.addSwitch( 'mia2' )
        ch1Switch = self.addSwitch( 'ch4' )
        ch2Switch = self.addSwitch( 'ch5' )

        # Add links
        self.addLink( mia1Switch, mia2Switch )
        self.addLink( mia1Switch, spSwitch )
        self.addLink( mia2Switch, spSwitch )
        self.addLink( mia2Switch, ch2Switch )
        self.addLink( ch2Switch, ch1Switch )
        self.addLink( ch1Switch, spSwitch )

        # Add hosts
        spHost = self.addHost( 'spH1' )
        clHost = self.addHost( 'clH2' )
        miHost = self.addHost( 'miH3' )

        # Add links to switches
        self.addLink( mia1Switch, miHost )
        self.addLink( ch1Switch, clHost )
        self.addLink( spSwitch, spHost )

topos = { 'mytopo': ( lambda: MyTopo() ) }