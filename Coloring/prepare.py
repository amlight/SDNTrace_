from coloring import Coloring


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


def save_current_colors(obj):
    """
        Save all current colors
        If the coloring flow needs to be replaced, it is
            important to know the last color to use as a
            match for deleting old flows
            Just copy current color for old_color variable
        Args:
            obj: SDNTrace class
    """
    for node in obj.node_list:
        node.old_color = node.color


def define_color(obj, links):
    """
        Get colors from Coloring class
        Args:
            obj: SDNTrace class
            links: SDNTrace.links
        Returns:
            list of colors and hosts to be used
    """
    prepare_adjencencies_list(obj, links)

    save_current_colors(obj)

    colors = Coloring(tuple(obj.node_list))
    colors.define_colors()
    ret_colors = colors.return_colors()
    # Debug
    # colors.print_colors()
    del colors

    return ret_colors


def create_adjecencies(pkt, node, neighbor):
    """
        Update adjencenciesList of each node.
        Args:
            pkt: SDNTrace object
            node: node to be searched
            neighbor: neighbor to be added to the adjencencyList
    """
    idx = get_node_from_name(pkt, node.name)
    neighbor_idx = get_node_from_name(pkt, neighbor)
    if pkt.node_list[neighbor_idx] not in pkt.node_list[idx].adjacencies_list:
        pkt.node_list[idx].adjacencies_list.append(pkt.node_list[neighbor_idx])


def get_node_from_name(pkt, name):
    """
        Return idx of a object on node_list
    """
    for node in pkt.node_list:
        if node.name == name:
            return pkt.node_list.index(node)


def prepare_adjencencies_list(pkt, links):
    """
        Prepare list of adjencencies
        This function iterates node_list and update the adjacency
            of each node based on links.
        Args:
            pkt: SDNTrace object
            links: list of links (SDNTrace.links)
    """
    for link in links:
        for node in pkt.node_list:
            if node.name == link[0]:
                create_adjecencies(pkt, node, link[1])
            elif node.name == link[1]:
                create_adjecencies(pkt, node, link[0])

    # print 'full print'
    # for node in pkt.node_list:
    #     print node.name, node.adjacencies_list
