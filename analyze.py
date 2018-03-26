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
import multiprocessing

from plot import Plot
import shapefile


def calc_weights(procnum, start, end, data):
    return_list = []
    for city in data[start:end]:
        city_name = next(iter(city))

        for c_city in data[start+1:]:
            c_city_name = next(iter(c_city))
            total_shared = 0

            if city_name == c_city_name:
                continue

            for g in city[city_name]:

                occurance = c_city[c_city_name].count(g)
                if occurance > 0:
                    total_shared += 1
                    c_city[c_city_name].remove(g)

            if total_shared > 0:
                return_list.append((city_name, c_city_name, total_shared))
                # print((city_name, c_city_name, total_shared))
    # print(end)
    # print(len(data))
    # print('--------')
    return return_list


regions = {
    # 'Subset': [1],
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

min_year = 1970

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

    City_G = nx.Graph()

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

        if row['city'] not in City_G and row['city']:
            City_G.add_node(row['city'], pos=(lon, lat), text=row['city'])
            cities.append(row['city'])
            print(row['city'])

        if row['gname'] not in groups:
            groups.append(row['gname'])

        if row['gname'] not in group_location:
            group_location[row['gname']] = {'cities': {row['city']: 1}, 'count': 1, 'lat': [lat], 'lon': [lon]}
        elif row['city'] not in group_location[row['gname']]['cities']:
            group_location[row['gname']]['cities'][row['city']] = 1
            group_location[row['gname']]['lat'].append(lat)
            group_location[row['gname']]['lon'].append(lon)
            group_location[row['gname']]['count'] += 1
        else:
            group_location[row['gname']]['cities'][row['city']] += 1
            group_location[row['gname']]['count'] += 1

        gname = row['gname']
        city = row['city']

        if city not in edge_dict:
            edge_dict[city] = [gname]
        else:
            if gname not in edge_dict[city]:
                edge_dict[city].append(gname)

    list_of_city_groups = []
    for city in edge_dict:
        list_of_city_groups.append({city: edge_dict[city]})

    pool = multiprocessing.Pool()

    results = []
    loop_Range = len(list_of_city_groups) - 25 if len(list_of_city_groups) > 25 else len(list_of_city_groups)
    now = time.time()
    print(len(list_of_city_groups))
    print(now)
    for i in range(0, loop_Range):
        result = pool.apply_async(calc_weights, args=(i, i, i + 25, list_of_city_groups))
        results += result.get()

    pool.close()
    pool.join()
    # print(results)
    print(len(results))
    end = time.time()
    print((end-now) / 60)

    City_G.add_weighted_edges_from(results)
    print('City nodes', len(City_G.nodes))
    print('City edges', len(City_G.edges))
    p.fr2(City_G)

    # Building the Group as Node, Shared attacks as edge weights graph
    Group_G = nx.Graph()
    for item in group_location:
        avg_lat = mean(group_location[item]['lat'])
        avg_lon = mean(group_location[item]['lon'])
        Group_G.add_node(item, pos=(avg_lon, avg_lat), text=item)

    not_if_cound = 0
    if_count = 0
    for outer_group in group_location:
        for inner_group in group_location:
            not_if_cound += 1
            if outer_group != inner_group:
                for city in group_location[outer_group]['cities']:
                    if city in group_location[inner_group]['cities'] and (outer_group, inner_group) not in list(Group_G.edges):
                        Group_G.add_weighted_edges_from([(outer_group, inner_group, min(group_location[outer_group]['cities'][city], group_location[inner_group]['cities'][city]))])
                    if_count += 1

    p.fr2(Group_G)
    print('Groups nodes', len(Group_G.nodes))
    print('Groups edges', len(Group_G.edges))

    break

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

