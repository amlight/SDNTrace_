from libs.coloring import coloring


def define_color(switches):
    """
        Get colors from coloring class
        Args:
            switches: dict of switches from SDNTrace class
            links: SDNTrace.links
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
    for _, switch in switches.items():
        switch.old_color = switch.color


def simplify_list_links(links):
    """
        Removes duplicated link entries in links
        Args:
            links = list of known links
        Returns:
            links updated
    """
    # 1 - Sort links
    for link in links:
        idx = links.index(link)
        links[idx] = tuple(sorted(link))
    links = sorted(links)
    # 2 - Remove duplicated
    links = list(set(links))
    return links
