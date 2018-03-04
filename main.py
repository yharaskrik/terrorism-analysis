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
        if int(row[yearIndex]) >= 1970 and row[groupNameIndex] and row[locationIndex] and row[groupNameIndex] != 'Unknown' and row[locationIndex] != 'Unknown':

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

            locationList.append(row[locationIndex])
            groupList.append(row[groupNameIndex])
            count += 1
    # print(G.nodes())
    print(count)
    print('All nodes and edges added')


# pos = nx.spring_layout(G)
# nx.draw_networkx_nodes(G, pos, node_color='b', nodelist=locationList)
# nx.draw_networkx_nodes(G, pos, node_color='black', nodelist=groupList)
# print('Nodes drawn')
# nx.draw_networkx_edges(G, pos, edge_color='r')
# print('edges drawn')
# plt.show()
# print(G.nodes(data=True))

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
print(sorted(locationWeights.items(), key=operator.itemgetter(1))[-10:])

print('Done')
