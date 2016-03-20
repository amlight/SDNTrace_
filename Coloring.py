# class Vertex(object):
#
#    def __init__(self, name):
#        self.name = str(name)
#        self.color = "0"
#        self.adjenceciesList = []


class Coloring(object):

    def __init__(self, verticesList):
        self.verticesList = verticesList
        self.colors = ["1", "10", "11", "100", "101", "110", "111"]

    def defineColors(self):
        for i in range(len(self.verticesList)):
            k = 0
            colorList = self.colors[:]
            color = colorList[k]
            v = self.verticesList[i]
            v.color = color
            for adj in v.adjenceciesList:
                # print v.name, adj.name, v.color, adj.color, k
                while color == adj.color:
                    k = k + 1
                    if k == len(self.colors) or len(colorList) == 0:
                        print "not possible to find enough colors"
                        return
                    else:
                        color = colorList[k]
                try:
                    if(adj.color != "0"):
                        colorList.remove(adj.color)
                        if k <= 0:
                            k = 0
                        else:
                            k = k - 1
                except:
                    # print(ValueError);
                    pass
            v.color = color
            # print(v.name + ' has color ' + v.color);
        return

    def printColors(self):
        totalColors = []
        for v in self.verticesList:
            totalColors.append(v.color)
            print v.name + ' == ' + v.color

        b = set(totalColors)
        print 'Total number of colors needed: %s ' % (len(b))
        return

    def returnColors(self):
        list_vertex_color = []
        for v in self.verticesList:
            list_vertex_color.append({v.name: v.color})

        return list_vertex_color
