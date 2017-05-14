from apps.coloring import coloring


def define_colors(switches):
    """
        Get colors from coloring class
        Args:
            switches: dict of switches from SDNTrace class
        Returns:
            list of colors and hosts to be used
    """
    save_current_colors(switches)
    colors = coloring.Coloring(switches)
    colors.define_colors()
    ret_colors = colors.return_colors()
    del colors
    return ret_colors


def save_current_colors(switches):
    """
        Save all current colors
        If the coloring flow needs to be replaced, it is
            important to know the last color to use as a
            match for deleting old flows
            Just copy current color for old_color variable
        Args:
            switches: SDNTrace class' dict of switches
    """
    for switch in switches:
        switch.old_color = switch.color
