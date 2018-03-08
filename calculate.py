
class Calculate:

    def total_degree(self, G, nodes):
        print('Calculating total degrees')
        return G.degree(nodes, weight='weight')