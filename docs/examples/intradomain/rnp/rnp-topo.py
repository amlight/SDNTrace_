""" RNP topology
    Data source: https://rnp.br/servicos/conectividade/trafego
"""
from mininet.topo import Topo

class MyTopo( Topo ):

    def __init__( self ):
        # Initialize topology
        Topo.__init__( self )

        # Add switches
        acSw = self.addSwitch('sw1')
        alSw = self.addSwitch('sw2')
        apSw = self.addSwitch('sw3')
        amSw = self.addSwitch('sw4')
        baSw = self.addSwitch('sw5')
        ceSw = self.addSwitch('sw6')
        dfSw = self.addSwitch('sw7')
        esSw = self.addSwitch('sw8')
        goSw = self.addSwitch('sw9')
        maSw = self.addSwitch('sw10')
        mtSw = self.addSwitch('sw11')
        msSw = self.addSwitch('sw12')
        mgSw = self.addSwitch('sw13')
        paSw = self.addSwitch('sw14')
        pbjSw = self.addSwitch('sw15')
        prSw = self.addSwitch('sw16')
        peSw = self.addSwitch('sw17')
        piSw = self.addSwitch('sw18')
        rjSw = self.addSwitch('sw19')
        rnSw = self.addSwitch('sw20')
        rsSw = self.addSwitch('sw21')
        roSw = self.addSwitch('sw22')
        rrSw = self.addSwitch('sw23')
        scSw = self.addSwitch('sw24')
        spSw = self.addSwitch('sw25')
        seSw = self.addSwitch('sw26')
        toSw = self.addSwitch('sw27')
        pbcSw = self.addSwitch('sw28')
        miaSw = self.addSwitch('sw29')

        # Add links
        self.addLink(acSw, roSw)
        self.addLink(roSw, mtSw)
        self.addLink(mtSw, msSw)
        self.addLink(mtSw, goSw)
        self.addLink(msSw, prSw)
        self.addLink(prSw, rsSw)
        self.addLink(prSw, spSw)
        self.addLink(prSw, scSw)
        self.addLink(scSw, spSw)
        self.addLink(spSw, rjSw)
        self.addLink(rjSw, esSw)
        self.addLink(rjSw, dfSw)
        self.addLink(goSw, toSw)
        self.addLink(goSw, dfSw)
        self.addLink(toSw, paSw)
        self.addLink(dfSw, amSw)
        self.addLink(dfSw, mgSw)
        self.addLink(esSw, baSw)
        self.addLink(baSw, peSw)
        self.addLink(baSw, seSw)
        self.addLink(baSw, mgSw)
        self.addLink(mgSw, ceSw)
        self.addLink(seSw, alSw)
        self.addLink(alSw, peSw)
        self.addLink(amSw, paSw)
        self.addLink(amSw, rrSw)
        self.addLink(rrSw, ceSw)
        self.addLink(spSw, mgSw)
        self.addLink(spSw, ceSw)
        self.addLink(ceSw, maSw)
        self.addLink(ceSw, rnSw)
        self.addLink(ceSw, peSw)
        self.addLink(maSw, paSw)
        self.addLink(paSw, apSw)
        self.addLink(paSw, piSw)
        self.addLink(piSw, peSw)
        self.addLink(rnSw, pbjSw)
        self.addLink(pbjSw, pbcSw)
        self.addLink(pbcSw, peSw)
        self.addLink(spSw, miaSw)
        self.addLink(ceSw, miaSw)
        self.addLink(rsSw, scSw)

        # Add hosts
        rsHost = self.addHost('h1')
        miaHost = self.addHost('h2')
        baHost = self.addHost('h3')
        acHost = self.addHost('h4')

        # Add links to hosts
        self.addLink(rsHost, rsSw)
        self.addLink(miaHost, miaSw)
        self.addLink(baHost, baSw)

topos = {'mytopo': (lambda: MyTopo())}