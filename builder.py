
class Builder:

    def build_graph(self, G, data):
        print('Building Graph')
        group_list = []
        location_list = []

        for index, row in data.iterrows():

            if row['gname'] not in G:
                G.add_node(row['gname'], pos=(1,1))
                group_list.append(row['gname'])

            if row['city'] not in G:
                G.add_node(row['city'], pos=(1,1))
                location_list.append(row['city'])

            if row['city'] in G[row['gname']]:
                G[row['gname']][row['city']]['weight'] += 1
            else:
                G.add_weighted_edges_from([(row['gname'], row['city'], 1)])

        return G, group_list, location_list

    # Adding the weak ties between cells, total shared attacks on a target.
    # ie. If Taliban and ISIL attack Baghdad 5 and 10 times respectively.
    # Weak tie will have a weight of 5
    # (minimum of the two weights, summed across all shared targets)
    def add_weak_ties(self, G, group_list, location_list):
        print('Adding Weak Ties')
        for outer_cell in group_list:
            for inner_cell in group_list:
                for location in location_list:
                    if outer_cell != inner_cell and location in G[outer_cell] and location in G[inner_cell]:
                        if outer_cell not in G[inner_cell] and inner_cell not in G[outer_cell]:

                            weight = min(G[outer_cell][location]['weight'], G[inner_cell][location]['weight'])

                            G.add_weighted_edges_from([(outer_cell, inner_cell, weight)])
                            # G.add_weighted_edges_from([(inner_cell, outer_cell, weight)])
                        else:
                            G[outer_cell][inner_cell]['weight'] += min(G[outer_cell][location]['weight'], G[inner_cell][location]['weight'])
        return G
