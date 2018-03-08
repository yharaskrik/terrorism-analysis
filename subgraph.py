import networkx as nx


class SubGraph:

    def create_sub_graph(self, G, nodes, isolate=False):
        print('Creating Subgraph')
        sub_graph = G.subgraph(nodes).copy()

        if isolate:
            for node in [node for node in nx.isolates(sub_graph)]:
                sub_graph.remove_nodes_from([node])
        return sub_graph
