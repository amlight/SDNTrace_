from ryu.lib import hub
from libs.core.singleton import Singleton
from libs.core.config_reader import ConfigReader
from libs.topology.switches import Switches
from libs.topology.links import Links
from apps.graph_coloring.coloring import Coloring


class GraphColoring(object):

    __metaclass__ = Singleton

    def __init__(self):
        self.switches = Switches()
        self.links = Links()
        self.config = ConfigReader()
        self.colors = []        # List of current colors in use
        self.old_colors = []    # List of old colors used
        # Threads
        self._refresh_colors = hub.spawn(self._push_colors)
        print('Graph Coloring App activated')

    def _push_colors(self):
        """
            This routine will run every PUSH_COLORS_INTERVAL interval
            and process the self.links to associate colors to OFSwitches.
            Flows will be pushed to switches with the dl_src field set
            to the defined color outputting to controller
            Args:
                self
        """
        while True:
            if len(self.switches) > 1:
                if len(self.links) is not 0:
                    self.install_colored_flows()
            hub.sleep(self.config.trace.push_color_interval)

    def install_colored_flows(self):
        """
            First define colors for each node
            Delete old flows
            Then push new flows
        """
        colors = self.define_colors(self.switches.get_switches())
        # Compare received colors with self.old_colors
        # If the same, ignore
        if colors is not None:
            self.colors = colors
            if len(self.old_colors) is 0:
                self.old_colors = self.colors
            else:
                if self.colors == self.old_colors:
                    return

        # Check all colors in use
        # For each switch:
        # 1 - Delete colored flows
        # 2 - For each switch, check colors of neighbors
        # 3 - Install all neighbors' colors
        for switch in self.switches.get_switches():
            # 1 - Delete old colored flows
            switch.delete_colored_flows()
            # 2 - Check colors of all other switches
            neighbor_colors = []
            for color in self.colors:
                # Get Dict Key. Just one Key
                for key in color:
                    if key != switch.name:
                        neighbor = self.switches.get_switch(key, by_name=True)
                        if neighbor in switch.adjacencies_list:
                            neighbor_colors.append(color[key])
            # 3 - Install all colors from other switches
            # in some cases, if two neighbors have the same color, the same flow
            # will be installed twice. It is not an issue.
            for color in neighbor_colors:
                switch.install_color(color)
            del neighbor_colors
            switch.old_color = switch.color
        self.old_colors = self.colors

    def define_colors(self, switches):
        """
            Get colors from coloring class
            Args:
                switches: dict of switches from SDNTrace class
            Returns:
                list of colors and hosts to be used
        """
        self.save_current_colors()
        colors = Coloring(switches)
        colors.define_colors()
        ret_colors = colors.return_colors()
        del colors
        return ret_colors

    def save_current_colors(self):
        """
            Save all current colors
            If the coloring flow needs to be replaced, it is
                important to know the last color to use as a
                match for deleting old flows
                Just copy current color for old_color variable
            Args:
                switches: SDNTrace class' dict of switches
        """
        for switch in self.switches.get_switches():
            switch.old_color = switch.color
