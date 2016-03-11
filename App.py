
from Coloring import Vertex
from Coloring import Coloring

n1 = Vertex("RS")
n2 = Vertex("SC")
n3 = Vertex("PR")
n4 = Vertex("SP")
n5 = Vertex("RJ")
n6 = Vertex("CE")
n7 = Vertex("MS")
n8 = Vertex("MT")
n9 = Vertex("GO")
n10 = Vertex("BS")
n11 = Vertex("PA")
n12 = Vertex("TO")
n13 = Vertex("PI")
n14 = Vertex("MA")
n15 = Vertex("RN")
n16 = Vertex("CG")
n17 = Vertex("JP")
n18 = Vertex("PE")
n19 = Vertex("AL")
n20 = Vertex("SE")
n21 = Vertex("BA")
n22 = Vertex("ES")
n23 = Vertex("MG")

n1.adjenceciesList.append(n2)
n1.adjenceciesList.append(n3)

n2.adjenceciesList.append(n1)
n2.adjenceciesList.append(n4)

n3.adjenceciesList.append(n1)
n3.adjenceciesList.append(n4)
n3.adjenceciesList.append(n7)

n4.adjenceciesList.append(n2)
n4.adjenceciesList.append(n3)
n4.adjenceciesList.append(n5)
n4.adjenceciesList.append(n23)

n5.adjenceciesList.append(n4)
n5.adjenceciesList.append(n10)
n5.adjenceciesList.append(n22)
n5.adjenceciesList.append(n6)

n6.adjenceciesList.append(n5)
n6.adjenceciesList.append(n18)
n6.adjenceciesList.append(n23)
n6.adjenceciesList.append(n14)

n7.adjenceciesList.append(n3)
n7.adjenceciesList.append(n8)

n8.adjenceciesList.append(n7)
n8.adjenceciesList.append(n9)

n9.adjenceciesList.append(n8)
n9.adjenceciesList.append(n10)
n9.adjenceciesList.append(n12)

n10.adjenceciesList.append(n5)
n10.adjenceciesList.append(n23)
n10.adjenceciesList.append(n9)
n10.adjenceciesList.append(n15)
n10.adjenceciesList.append(n11)

n11.adjenceciesList.append(n12)
n11.adjenceciesList.append(n10)
n11.adjenceciesList.append(n13)
n11.adjenceciesList.append(n14)

n12.adjenceciesList.append(n9)
n12.adjenceciesList.append(n11)

n13.adjenceciesList.append(n11)
n13.adjenceciesList.append(n18)

n14.adjenceciesList.append(n11)
n14.adjenceciesList.append(n6)

n15.adjenceciesList.append(n10)
n15.adjenceciesList.append(n17)

n16.adjenceciesList.append(n17)
n16.adjenceciesList.append(n18)

n17.adjenceciesList.append(n16)
n17.adjenceciesList.append(n15)

n18.adjenceciesList.append(n21)
n18.adjenceciesList.append(n19)
n18.adjenceciesList.append(n13)
n18.adjenceciesList.append(n6)
n18.adjenceciesList.append(n16)

n19.adjenceciesList.append(n18)
n19.adjenceciesList.append(n20)

n20.adjenceciesList.append(n19)
n20.adjenceciesList.append(n21)

n21.adjenceciesList.append(n20)
n21.adjenceciesList.append(n23)
n21.adjenceciesList.append(n22)
n21.adjenceciesList.append(n18)

n22.adjenceciesList.append(n21)
n22.adjenceciesList.append(n5)

n23.adjenceciesList.append(n21)
n23.adjenceciesList.append(n6)
n23.adjenceciesList.append(n10)
n23.adjenceciesList.append(n4)

# tests
# n18.adjenceciesList.append(n10)
# n10.adjenceciesList.append(n18)
# n6.adjenceciesList.append(n4)
# n4.adjenceciesList.append(n6)
# n11.adjenceciesList.append(n4)
# n4.adjenceciesList.append(n11)

vList = (n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11, n12, n13, n14, n15, n16,
         n17, n18, n19, n20, n21, n22, n23)

coloring = Coloring(vList)
coloring.defineColors()
# coloring.printColors()
colors = coloring.returnColors()
for color in colors:
    print color
