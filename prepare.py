from Coloring import Coloring


def simplify_list_links(links):
    # 1 - Sort links
    for link in links:
        idx = links.index(link)
        links[idx] = tuple(sorted(link))
    links = sorted(links)
    # 2 - Remove duplicated
    links = list(set(links))
    return links


def save_current_colors(obj):
    for node in obj.node_list:
        node.old_color = node.color


def define_color(obj):

    save_current_colors(obj)
    coloring = Coloring(tuple(obj.node_list))
    coloring.defineColors()
    colors = coloring.returnColors()
    del coloring

    return colors


def create_adjecencies(pkt, node, neighbor):
    idx = get_node_from_name(pkt, node.name)
    neighbor_idx = get_node_from_name(pkt, neighbor)
    if pkt.node_list[neighbor_idx] not in pkt.node_list[idx].adjenceciesList:
        pkt.node_list[idx].adjenceciesList.append(pkt.node_list[neighbor_idx])


def get_node_from_name(pkt, name):
    for node in pkt.node_list:
        if node.name == name:
            return pkt.node_list.index(node)


def prepare_adjencenciesList(pkt, links):
    for link in links:
        for node in pkt.node_list:
            if node.name == link[0]:
                create_adjecencies(pkt, node, link[1])
            elif node.name == link[1]:
                create_adjecencies(pkt, node, link[0])

    # print 'full print'
    # for node in pkt.node_list:
    #     print node.name, node.adjenceciesList
