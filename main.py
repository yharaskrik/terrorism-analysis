import networkx as nx
import csv
import matplotlib.pyplot as plt

G = nx.DiGraph()

with open('data.csv', 'r') as infile:
    reader = csv.reader(infile)
    headers = next(reader)

    groupNameIndex = headers.index('gname')
    locationIndex = headers.index('city')
    yearIndex = headers.index('iyear')
    regionIndex = headers.index('region')
    attackTypeIndex = headers.index('attacktype1')
    claimedIndex = headers.index('claimed')
    print(groupNameIndex)
    print(locationIndex)
    locationList = []
    groupList = []
    data = []
    count = 0
    skipCount = 0
    for row in reader:
        if skipCount < 0:
            skipCount += 1
            continue
        else:
            skipCount += 1
        # print(row[regionIndex])
        if int(row[yearIndex]) >= 2016 and row[groupNameIndex] and row[locationIndex] and row[groupNameIndex] != 'Unknown' and row[locationIndex] != 'Unknown':

            if row[groupNameIndex] not in G:
                # print('Adding: ', row[groupNameIndex])
                G.add_node(row[groupNameIndex])

            if row[locationIndex] not in G:
                # print('Adding: ', row[locationIndex])
                G.add_node(row[locationIndex])

            if row[locationIndex] in G[row[groupNameIndex]]:
                G[row[groupNameIndex]][row[locationIndex]]['weight'] += 1
                # print('Weight is now: ', G[row[groupNameIndex]][row[locationIndex]]['weight'])
            else:
                G.add_weighted_edges_from([(row[groupNameIndex], row[locationIndex], 1)])

            # locationList.append(row[locationIndex])
            if row[groupNameIndex] not in groupList:
                groupList.append(row[groupNameIndex])
            count += 1
    # print(G.nodes())
    print(count)
    print('All nodes and edges added')

locationWeights = dict()

for node in G.nodes:
    totalWeight = 0
    edges = G.in_edges(node, data=True)
    for edge in edges:
        print(edge)
        if edge[1] not in locationWeights:
            locationWeights[edge[1]] = edge[2]['weight']
        else:
            locationWeights[edge[1]] += edge[2]['weight']
import operator
sortedLocationList = sorted(locationWeights.items(), key=operator.itemgetter(1))[-50:]
print(sortedLocationList)
for l in sortedLocationList:
    locationList.append(l[0])

print('Length of locations: ', len(locationList))
print('Length of groups: ', len(groupList))
# print('Degrees of nodes: ', )

degrees = [(node, val) for (node, val) in G.degree()]
print(sorted(degrees, key=operator.itemgetter(1))[-20:])
topGroups = sorted(degrees, key=operator.itemgetter(1))[-20:]
justGroupNames = [node for (node, val) in topGroups]

edgeList = []
for l in locationList:
    for g in justGroupNames:
        if G.has_edge(g, l):
            edgeList.append((g, l))

print(edgeList)

subGraph = G.subgraph(locationList + justGroupNames)

pos = nx.spring_layout(subGraph)
nx.draw_networkx_nodes(subGraph, pos, node_color='blue', nodelist=locationList)
nx.draw_networkx_nodes(subGraph, pos, node_color='black', nodelist=justGroupNames)
print('Nodes drawn')
nx.draw_networkx_edges(subGraph, pos, edge_color='r', edgelist=edgeList)
print('edges drawn')
plt.show()
print(G.nodes(data=True))

print('Done')
