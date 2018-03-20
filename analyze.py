import builder
import calculate
import file
import filter
import math
import time
import subgraph
import networkx as nx
from pprint import pprint
import matplotlib.pyplot as plt
from statistics import median, mean

from plot import Plot
import shapefile

regions = {
    # 'Subset': [10],
    'Global': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    'North America': [1],
    'Central America & Caribbean': [2],
    'South America': [3],
    'East Asia': [4],
    'Southeast Asia': [5],
    'South Asia': [6],
    'Central Asia': [7],
    'Western Asia': [8],
    'Western Europe': [8],
    'Eastern Europe': [9],
    'Middle East & North Africa': [10],
    'Sub-Saharan Africa': [11],
    'Australasia & Oceania': [12]
}

region_name = ['North America', 'Central America & Caribbean', 'South America', 'East Asia',
               'Southeast Asia', 'South Asia', 'Central Asia', 'Western Asia', 'Western Europe',
               'Eastern Europe', 'Middle East & North Africa', 'Sub-Saharan Africa', 'Australasia & Oceania']

min_year = 2000

# number of countries, cells, locations, total number of attacks
# how much data we actually used
# ranked cities of most attacks (rank based on degree), and cells with most attacks (cell based graph, total degree)

# pre 2000 post 2000 graphs cells as nodes and edges at shared attacks
# average clustering coefficient
# higher betweenness centrality

r = file.File()
f = filter.Filter()
b = builder.Builder()
c = calculate.Calculate()
s = subgraph.SubGraph()
p = Plot()

# Read the dat into memory
all_data = r.read_data('data.csv')
print('Filtering data for min_year = ', min_year)
all_data = f.filter(all_data, year=min_year)

for key in regions:

    region = regions[key]
    print('Checking region: ' + key)
    r.write_line('Region: ' + key, '\n')

    G = nx.DiGraph()

    U_G = nx.Graph()

    # Filter out the data we do not want based on year and region
    # Also filters out missing and unknown data
    print('Filtering on region: ', key)
    data = f.filter(all_data, region=region)

    groups = []
    cities = []

    group_location = {}

    edge_dict = {}

    print('Getting all lat and lon, adding city ndoes')
    for index, row in data.iterrows():

        lat = row['latitude']
        lon = row['longitude']

        if not lat or not lon:
            continue

        if row['city'] not in U_G:
            U_G.add_node(row['city'], pos=(lon, lat), text=row['city'])
            cities.append(row['city'])

        if row['gname'] not in groups:
            groups.append(row['gname'])

        if row['gname'] not in group_location:
            group_location[row['gname']] = {'cities': [row['city']], 'count': 1, 'lat': [lat], 'lon': [lon]}
        elif row['city'] not in group_location[row['gname']]['cities']:
            group_location[row['gname']]['cities'].append(row['city'])
            group_location[row['gname']]['lat'].append(lat)
            group_location[row['gname']]['lon'].append(lon)
            group_location[row['gname']]['count'] += 1
        else:
            group_location[row['gname']]['count'] += 1

        gname = row['gname']
        city = row['city']

        if city not in edge_dict:
            edge_dict[city] = {gname: 1}
        else:
            if gname not in edge_dict[city]:
                edge_dict[city][gname] = 1
            else:
                edge_dict[city][gname] += 1

    Group_G = nx.Graph()

    # print(group_location)
    print(groups)

    for item in group_location:
        # print(item)
        # print(group_location[item])
        avg_lat = mean(group_location[item]['lat'])
        avg_lon = mean(group_location[item]['lon'])
        Group_G.add_node(item, pos=(avg_lon, avg_lat), text=item)

    p.fr2(Group_G)

    break

    print(U_G.nodes)
    count = 0
    print('Data Length:', len(data))
    print('Group length: ', len(groups))
    print('Locations length: ', len(cities))
    for group in groups:
        sub_data = data[data['gname'] == group]

        for outer_index in range(0, len(sub_data) - 1):
            outer_row = sub_data.iloc[[outer_index]]
            outer_city = outer_row['city'].values[0]
            for inner_index in range(outer_index + 1, len(sub_data)):
                inner_row = sub_data.iloc[[inner_index]]
                inner_city = inner_row['city'].values[0]
                if outer_city != inner_city:
                    if outer_city not in U_G[inner_city]:
                        U_G.add_weighted_edges_from([(outer_city, inner_city, 1)])
                    else:
                        U_G[outer_city][inner_city]['weight'] += 1

                count += 1
                if count % 1000 == 0:
                    print(time.time())
                    print(len(groups) * len(data) * math.log(len(data), 10), ' - ', count)

    print('#Edges:', len(U_G.edges))
    avg_edge_weight = sum([U_G.get_edge_data(*edge)['weight'] for edge in U_G.edges]) / len(U_G.edges)
    cut_off = sorted([U_G.get_edge_data(*edge)['weight'] for edge in U_G.edges])[-int(len(U_G.edges) * 0.2):]
    mean_weight = mean(cut_off)
    median_weight = median(cut_off)
    print(median(cut_off))
    print(mean(cut_off))
    print(avg_edge_weight)

    edges_to_remove = [edge for edge in U_G.edges if U_G.get_edge_data(*edge)['weight'] < mean_weight]
    U_G.remove_edges_from(edges_to_remove)
    # U_G.remove_nodes_from(list(nx.isolates(U_G)))
    print('#Remove: ', len(edges_to_remove))

    print(len(U_G.edges))
    p.fr2(U_G, cities)
    break

    if key == 'Global':
        print('Creating plot for the global terrorist network')

        spots = {}
        G = nx.Graph()
        for index in regions[key]:
            spots[region_name[index - 1]] = {}
            G.add_node(region_name[index - 1])

        for index, row in data.iterrows():
            if row.gname in spots[region_name[row.region - 1]]:
                spots[region_name[row.region - 1]][row.gname] += 1
            else:
                spots[region_name[row.region - 1]][row.gname] = 1

        pprint(spots)

        done = []
        for reg in spots:
            done.append(reg)
            for inner_reg in spots:
                total_weight = 0
                if inner_reg not in done:
                    for outer_group in spots[reg]:
                        if outer_group in spots[inner_reg]:
                            total_weight += min(spots[reg][outer_group], spots[inner_reg][outer_group])

                if total_weight != 0:
                    G.add_weighted_edges_from([(reg, inner_reg, total_weight)])

        pos = nx.circular_layout(G)
        nx.draw_circular(G, with_labels=True)
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
        plt.show()
        continue

    # Continue onto not global stuff as global has too much data.

    # Builds the networkx graph
    # adds weights = totaling the number of edges between two nodes
    G, group_list, location_list = b.build_graph(G, data)

    # Convert to undirected graph and calculates the betweenness centrality
    U_G = nx.to_undirected(G).copy()
    betweenness_centrality = nx.betweenness_centrality(U_G)

    # Remove cells so we only get centrality for locations
    betweenness_centrality = f.filter_dict(betweenness_centrality, location_list)
    sorted_betweenness_centrality = f.sort_dict(betweenness_centrality)

    # Outputting the centrality data
    r.write_line('Location betweenness centralities', sorted_betweenness_centrality)

    # Calculating the degree of just the nodes for locations, total # of attacks on those locations
    total_location_degrees = c.total_degree(G, location_list)
    sorted_total_location_degrees = f.sort_list(total_location_degrees)

    # Outputting the total in degree of locations
    r.write_line('Total in_degree of each location node.', sorted_total_location_degrees)

    # Calculating total out degree of each cell
    total_cell_degrees = c.total_degree(G, group_list)
    sorted_total_cell_degrees = f.sort_list(total_cell_degrees)

    # Outputting the total out degree of terrorist cells
    r.write_line('Total out_degree of each of the terrorist cells', sorted_total_cell_degrees)

    # Converting back to an undirected graph
    U_G = nx.to_undirected(G).copy()

    # Calculating ties between cells based on total number of shared target-attacks
    U_G = b.add_weak_ties(U_G, group_list, location_list)

    # sorting the local clustering coefficients for the terrorist cells
    sorted_local_clustering_coefficients = f.sort_dict(nx.clustering(U_G, group_list, weight='weight'))
    top_cells = [l[0] for l in sorted_local_clustering_coefficients[:int(len(sorted_local_clustering_coefficients))]]

    # Outputting the sorted local clustering coefficients for the cells
    r.write_line('Local clustering coefficients for the terrorist cells', sorted_local_clustering_coefficients)

    # Sorting the local clustering coefficients for the locations
    sorted_local_clustering_coefficients = f.sort_dict(nx.clustering(U_G, location_list, weight='weight'))

    # Outputting the sorted local clustering coefficients for the cells
    r.write_line('Local clustering coefficients for the terror locations', sorted_local_clustering_coefficients)

    # Making a subgraph of just the cell-cell edges, excluding all locations
    C_G = s.create_sub_graph(U_G, group_list)

    T_G = s.create_sub_graph(U_G, top_cells)

    p = Plot()
    p.fruchterman_reingold(T_G)
    break
    # pos = nx.circular_layout(T_G)
    # nx.draw_circular(T_G, with_labels=False)
    # labels = nx.get_edge_attributes(T_G, 'weight')
    # nx.draw_networkx_edge_labels(T_G, pos, edge_labels=labels)
    # plt.savefig('plots/plot-' + key + 'circular.png')

    # Calculating the clustering coefficients of the cells excluding all locations.
    sorted_local_clustering_coefficients = f.sort_dict(nx.clustering(C_G, weight='weight'))

    # Outputting the sorted local clustering coefficients for just the cells excluding the locations
    r.write_line('Local clustering coefficients for the terror cells excluding the locations', sorted_local_clustering_coefficients)

