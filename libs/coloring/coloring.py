

class Coloring(object):

    def __init__(self, switches_list):
        """
            Instantiate Cororing class
            Args:
                switches_list: list of OFSwitch classes (or node_list)
        """
        self.vertices_list = switches_list
        self.colors = ["1", "10", "11", "100", "101", "110", "111"]

    def define_colors(self):
        """
            Method to assign minimal number of colors
            Each switch is considered a vertex. Number of links between
                switches are ignored. In the end, each node from node_list
                will have its color defined
            Args:
                self: coloring class
        """
        for _, vertex in self.vertices_list.items():
            k = 0
            color_list = self.colors[:]
            color = color_list[k]
            v = vertex
            v.color = color
            for adj in v.adjacencies_list:
                # print v.name, adj.name, v.color, adj.color, k
                while color == adj.color:
                    k += 1
                    if k == len(self.colors) or len(color_list) == 0:
                        print "not possible to find enough colors"
                        return
                    else:
                        color = color_list[k]
                try:
                    if adj.color != "0":
                        color_list.remove(adj.color)
                except ValueError:
                    pass
                finally:
                    if k <= 0:
                        k = 0
                    else:
                        k -= 1
            v.color = color
            # print(v.name + ' has color ' + v.color)
        return

    def print_colors(self):
        """
            Print colors in case of troubleshoot needed
        """
        total_colors = []
        for _, v in self.vertices_list.items():
            total_colors.append(v.color)
            print v.name + ' == ' + v.color

        b = set(total_colors)
        print 'Total number of colors needed: %s ' % (len(b))
        return

    def return_colors(self):
        """
            Return a list of dictionaries with nodes and colors
        """
        list_vertex_color = []
        for _, v in self.vertices_list.items():
            list_vertex_color.append({v.name: v.color})

        return list_vertex_color
