import builder
import calculate
import file
import filter
import subgraph
import networkx as nx
from pprint import pprint
import matplotlib.pyplot as plt

regions = {
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

r = file.File()
f = filter.Filter()
b = builder.Builder()
c = calculate.Calculate()
s = subgraph.SubGraph()

# Read the dat into memory
all_data = r.read_data('data.csv')
print('Filtering data for min_year = ', min_year)
all_data = f.filter(all_data, year=min_year)

for key in regions:

    region = regions[key]
    print('Checking region: ' + key)
    r.write_line('Region: ' + key, '\n')

    G = nx.DiGraph()

    # Filter out the data we do not want based on year and region
    # Also filters out missing and unknown data
    print('Filtering on region: ', key)
    data = f.filter(all_data, region=region)

    # # Builds the networkx graph
    # # adds weights = totaling the number of edges between two nodes
    # G, group_list, location_list = b.build_graph(G, data)
    #
    # # Convert to undirected graph and calculates the betweenness centrality
    # U_G = nx.to_undirected(G).copy()
    # betweenness_centrality = nx.betweenness_centrality(U_G)
    #
    # # Remove cells so we only get centrality for locations
    # betweenness_centrality = f.filter_dict(betweenness_centrality, location_list)
    # sorted_betweenness_centrality = f.sort_dict(betweenness_centrality)
    #
    # # Outputting the centrality data
    # r.write_line('Location betweenness centralities', sorted_betweenness_centrality)
    #
    # # Calculating the degree of just the nodes for locations, total # of attacks on those locations
    # total_location_degrees = c.total_degree(G, location_list)
    # sorted_total_location_degrees = f.sort_list(total_location_degrees)
    #
    # # Outputting the total in degree of locations
    # r.write_line('Total in_degree of each location node.', sorted_total_location_degrees)
    #
    # # Calculating total out degree of each cell
    # total_cell_degrees = c.total_degree(G, group_list)
    # sorted_total_cell_degrees = f.sort_list(total_cell_degrees)
    #
    # # Outputting the total out degree of terrorist cells
    # r.write_line('Total out_degree of each of the terrorist cells', sorted_total_cell_degrees)
    #
    # # Converting back to an undirected graph
    # U_G = nx.to_undirected(G).copy()
    #
    # # Calculating ties between cells based on total number of shared target-attacks
    # U_G = b.add_weak_ties(U_G, group_list, location_list)
    #
    # # sorting the local clustering coefficients for the terrorist cells
    # sorted_local_clustering_coefficients = f.sort_dict(nx.clustering(U_G, group_list, weight='weight'))
    #
    # # Outputting the sorted local clustering coefficients for the cells
    # r.write_line('Local clustering coefficients for the terrorist cells', sorted_local_clustering_coefficients)
    #
    # # Sorting the local clustering coefficients for the locations
    # sorted_local_clustering_coefficients = f.sort_dict(nx.clustering(U_G, location_list, weight='weight'))
    #
    # # Outputting the sorted local clustering coefficients for the cells
    # r.write_line('Local clustering coefficients for the terror locations', sorted_local_clustering_coefficients)
    #
    # # Making a subgraph of just the cell-cell edges, excluding all locations
    # C_G = s.create_sub_graph(U_G, group_list)
    #
    # # Calculating the clustering coefficients of the cells excluding all locations.
    # sorted_local_clustering_coefficients = f.sort_dict(nx.clustering(C_G, weight='weight'))
    #
    # # Outputting the sorted local clustering coefficients for just the cells excluding the locations
    # r.write_line('Local clustering coefficients for the terror cells excluding the locations', sorted_local_clustering_coefficients)

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

        # pos = nx.spring_layout(C_G)
        # nx.draw_networkx_edges(C_G, pos)
        # plt.show()
        # plt.savefig('plots/plot-' + key + '.png')
    # break
