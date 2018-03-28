import builder
import calculate
import file
import filter
import math
import time
import subgraph
import networkx as nx
import collections
from pprint import pprint
from statistics import median, mean

import matplotlib.pyplot as plt
import multiprocessing

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
    'Subset': [1],
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

min_year = 1984

# number of countries, cells, locations, total number of attacks
# how much data we actually used
# ranked cities of most attacks (rank based on degree), and cells with most attacks (cell based graph, total degree)

# pre 2000 post 2000 graphs cells as nodes and edges at shared attacks
# average clustering coefficient
# higher betweenness centrality

# Pre 2000 north america
# post 2000 north america
# average path length for each region and global
# num nodes, num edges

#just global
# global clustering coefficient
# betweenness
# average degree and max degree
# % max degree
# % of size of largest component
# of components

r = file.File()
f = filter.Filter()
b = builder.Builder()
c = calculate.Calculate()
s = subgraph.SubGraph()
# p = Plot()

# Read the dat into memory
all_data = r.read_data('data.csv')
print('Filtering data for min_year = ', min_year)
all_data = f.filter(all_data, year=min_year, max_year=2000)

r.write_line('# of data rows: ', len(all_data))

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
    countries = []

    group_location = {}

    edge_dict = {}

    print('Getting all lat and lon, adding city ndoes')
    for index, row in data.iterrows():

        lat = row['latitude']
        lon = row['longitude']

        if not lat or not lon:
            continue

        if row['country'] not in countries:
            countries.append(row['country'])

        if row['city'] not in City_G and row['city']:
            City_G.add_node(row['city'], pos=(lon, lat), text=row['city'])
            cities.append(row['city'])
            # print(row['city'])

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

    if key == 'Global':
        r.write_line('# Countries: ', len(countries))
        r.write_line('# Cells: ', len(groups))
        r.write_line('# Cities: ', len(cities))

    list_of_city_groups = []
    for city in edge_dict:
        list_of_city_groups.append({city: edge_dict[city]})

    # pool = multiprocessing.Pool()
    #
    # results = []
    # loop_Range = len(list_of_city_groups) - 25 if len(list_of_city_groups) > 25 else len(list_of_city_groups)
    # now = time.time()
    # print(len(list_of_city_groups))
    # print(now)
    # for i in range(0, loop_Range):
    #     result = pool.apply_async(calc_weights, args=(i, i, i + 25, list_of_city_groups))
    #     results += result.get()
    # pool.join()
    # print(results)
    results = calc_weights(0, 0, len(list_of_city_groups), list_of_city_groups)
    print('Length of results: ', len(results))
    end = time.time()
    # print((end-now) / 60)
    print(results)
    City_G.add_weighted_edges_from(results)
    print('City nodes', len(City_G.nodes))
    print('City edges', len(City_G.edges))
    # p.fr2(City_G)

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

    # p.fr2(Group_G)
    print('Groups nodes', len(Group_G.nodes))
    print('Groups edges', len(Group_G.edges))

    # # Betweenness centrality of the City graph
    # betweenness_centrality = nx.betweenness_centrality(City_G)
    # # Remove cells so we only get centrality for locations
    # betweenness_centrality = f.filter_dict(betweenness_centrality, cities)
    # sorted_betweenness_centrality = f.sort_dict(betweenness_centrality)
    # # Outputting the centrality data
    # r.write_line('City betweenness centralities', sorted_betweenness_centrality[:20])

    # Betweenness centrality for the group graph
    betweenness_centrality = nx.betweenness_centrality(Group_G)
    # Remove cells so we only get centrality for locations
    betweenness_centrality = f.filter_dict(betweenness_centrality, groups)
    sorted_betweenness_centrality = f.sort_dict(betweenness_centrality)
    # Outputting the centrality data
    r.write_line('Group betweenness centralities', sorted_betweenness_centrality[:20])

    # # Calculating the degree of just the nodes for locations, total # of attacks on those locations
    # total_location_degrees = c.total_degree(City_G, cities)
    # sorted_total_location_degrees = f.sort_list(total_location_degrees)
    # # Outputting the total in degree of locations
    # r.write_line('Total in_degree of each location node.', sorted_total_location_degrees[:20])

    # Calculating total out degree of each cell
    total_cell_degrees = c.total_degree(Group_G, groups)
    sorted_total_cell_degrees = f.sort_list(total_cell_degrees)
    avg_degree = mean([x[1] for x in sorted_total_cell_degrees])
    mediun_degree = median([x[1] for x in sorted_total_cell_degrees])
    print('Average degree of cells')
    print(mediun_degree)
    r.write_line('Average degree of cells', avg_degree)
    # Outputting the total out degree of terrorist cells
    r.write_line('Total out_degree of each of the terrorist cells', sorted_total_cell_degrees[:20])

    # sorting the local clustering coefficients for the terrorist cells
    sorted_local_clustering_coefficients = f.sort_dict(nx.clustering(Group_G, groups, weight='weight'))
    top_cells = [l[0] for l in sorted_local_clustering_coefficients[:int(len(sorted_local_clustering_coefficients))]]
    # Outputting the sorted local clustering coefficients for the cells
    r.write_line('Local clustering coefficients for the terrorist cells', sorted_local_clustering_coefficients[:20])

    # sorting the local clustering coefficients for the locations
    # sorted_local_clustering_coefficients = f.sort_dict(nx.clustering(City_G, cities, weight='weight'))
    # top_cities = [l[0] for l in sorted_local_clustering_coefficients[:int(len(sorted_local_clustering_coefficients))]]
    # # Outputting the sorted local clustering coefficients for the cells
    # r.write_line('Local clustering coefficients for the terrorist cells', sorted_local_clustering_coefficients[:20])

    connected_graph = Group_G.copy()

    avg = 0
    avg_weight = 0
    count = 0
    total = 0

    for g in nx.connected_component_subgraphs(connected_graph):
        if len(g.nodes) > count:
            avg_weight = nx.average_shortest_path_length(g, weight='weight')
            avg = nx.average_shortest_path_length(g)
            count = len(g.nodes)
        total += 1
    r.write_line('# Connected subgraphs (cells): ' + key + ': ', total)
    print('Average: ', avg)
    print('Average Weight: ', avg_weight)

    if key == 'Subset':
        degree_sequence = sorted([d for n, d in Group_G.degree()], reverse=True)  # degree sequence
        # print "Degree sequence", degree_sequence
        degreeCount = collections.Counter(degree_sequence)
        deg, cnt = zip(*degreeCount.items())

        fig, ax = plt.subplots()
        plt.bar(deg, cnt, width=0.80, color='black')

        plt.title("Degree Histogram")
        plt.ylabel("Count")
        plt.xlabel("Degree")
        # ax.set_xticks([d + 0.4 for d in deg])
        # ax.set_xticklabels(deg)

        # draw graph in inset
        plt.axes([0.4, 0.4, 0.5, 0.5])
        Gcc = sorted(nx.connected_component_subgraphs(Group_G), key=len, reverse=True)[0]
        pos = nx.spring_layout(Group_G)
        plt.axis('off')
        nx.draw_networkx_nodes(Group_G, pos, node_size=20, node_color='black')
        nx.draw_networkx_edges(Group_G, pos, alpha=0.4)
        plt.savefig('plot' + str(min_year) + str(key) + '.png')
        plt.show()
    break