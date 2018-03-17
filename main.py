import pprint

import networkx as nx
import csv
import matplotlib.pyplot as plt
import operator

from math import sqrt


def betweenness_centrality(G, s, t, v):
    k = 2

    s_n = nx.neighbors(G, s)
    t_n = nx.neighbors(G, t)

    list_s_n = list(s_n)
    list_t_n = list(t_n)

    # print(list(s_n))
    # print(list(t_n))

    set_s_n = set(list_s_n)
    set_t_n = set(list_t_n)

    # print(set_s_n)
    # print(set_t_n)
    intersection = list(set_s_n & set_t_n)
    print(intersection)

    numerator = 0
    denominator = 0
    for node in intersection:

        edge_one = G.get_edge_data(s, node)['weight']
        edge_two = G.get_edge_data(t, node)['weight']

        # print(s + ' attacked ' + node + ' ' + str(edge_one))
        # print(t + ' attacked ' + node + ' ' + str(edge_two))

        if node == v:
            numerator += edge_one + edge_two
        denominator += edge_two + edge_one

    # print(numerator)
    # print(denominator)
    if denominator == 0:
        return None
    print(numerator / denominator)
    return numerator/ denominator


G = nx.DiGraph()

with open('data.csv', 'r') as infile:
    reader = csv.reader(infile)
    headers = next(reader)

    # parameters
    minYear = 2016
    numTopLocations = 40
    numTopGroups = 40

    # Indexes of certain predictors
    groupNameIndex = headers.index('gname')
    locationIndex = headers.index('city')
    yearIndex = headers.index('iyear')
    regionIndex = headers.index('region')
    attackTypeIndex = headers.index('attacktype1')
    claimedIndex = headers.index('claimed')

    locationList = []
    groupList = []
    data = []
    count = 0
    skipCount = 0
    for row in reader:

        if int(row[yearIndex]) >= minYear and row[groupNameIndex] and row[locationIndex] and row[groupNameIndex] != 'Unknown' and row[locationIndex] != 'Unknown':

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

# Calculating total weights for edges
for node in G.nodes:
    totalWeight = 0
    edges = G.in_edges(node, data=True)
    for edge in edges:
        # print(edge)
        if edge[1] not in locationWeights:
            locationWeights[edge[1]] = edge[2]['weight']
        else:
            locationWeights[edge[1]] += edge[2]['weight']

sortedLocationList = sorted(locationWeights.items(), key=operator.itemgetter(1))
# [-numTopLocations:]
for l in sortedLocationList:
    locationList.append(l[0])

print('Length of locations: ', len(locationList))
print('Length of groups: ', len(groupList))
# print('Degrees of nodes: ', )

degrees = [(node, val) for (node, val) in G.degree()]
# [-numTopGroups:]
topGroups = sorted(degrees, key=operator.itemgetter(1))
justGroupNames = [node for (node, val) in topGroups]

edgeList = []
for l in locationList:
    for g in justGroupNames:
        if G.has_edge(g, l):
            edgeList.append((g, l))

subGraph = G.subgraph(locationList + justGroupNames).copy()

for node in [node for node in nx.isolates(subGraph)]:
    subGraph.remove_nodes_from([node])
    if node in locationList:
        locationList.remove(node)
    elif node in justGroupNames:
        justGroupNames.remove(node)

pos = nx.spring_layout(subGraph, k=2/sqrt(len(subGraph.nodes)), scale=100.0)
nx.draw_networkx_nodes(subGraph, pos, node_color='blue', nodelist=locationList)
nx.draw_networkx_nodes(subGraph, pos, node_color='black', nodelist=justGroupNames)
print('Nodes drawn')
nx.draw_networkx_edges(subGraph, pos, edge_color='r', edgelist=edgeList)
print('edges drawn')
plt.show()

for edge in nx.edges(subGraph):
    print(edge)
    print(subGraph.get_edge_data(edge[0], edge[1]))

subGraph = subGraph.to_undirected()

# two_b = []
# for cell1 in justGroupNames:
#     for cell2 in justGroupNames:
#         if cell1 != cell2:
#             for location in locationList:
#                 c = betweenness_centrality(subGraph, cell1, cell2, location)
#                 print(c)
#                 if c:
#                     two_b.append((cell1, cell2, c))

lowest = dict()

# for cell in justGroupNames:
#     neighbors = nx.neighbors(subGraph, cell)
#
#     for neighbor in neighbors:
#         cells2 = nx.neighbors(subGraph, neighbor)
#         for cell2 in cells2:
#             lowest[cell] = dict()
#             lowest[cell][cell2] = 0

for cell in justGroupNames:
    neighbors = nx.neighbors(subGraph, cell)

    for neighbor in neighbors:
        weight1 = subGraph.get_edge_data(cell, neighbor)['weight']

        cells2 = nx.neighbors(subGraph, neighbor)

        for cell2 in cells2:
            if cell == cell2:
                pass
            weight2 = subGraph.get_edge_data(neighbor, cell2)['weight']
            lowestWeight = weight1 if weight1 < weight2 else weight2
            if cell not in lowest:
                lowest[cell] = {}
            if cell2 not in lowest[cell]:
                lowest[cell][cell2] = 0
            lowest[cell][cell2] += lowestWeight


pprint.pprint(lowest)

highest_weight = 0
cell1 = ''
cell2 = ''

highest_weights = []

for key in lowest:
    print(key)
    for key2 in lowest[key]:
        if key != key2:
            highest_weights.append((key, key2, lowest[key][key2]))

pprint.pprint(sorted(highest_weights, key=operator.itemgetter(2))[-20:])

print('Done')
