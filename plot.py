import math
import networkx as nx
import plotly.plotly as py
import plotly
from plotly.graph_objs import *
import shapefile

class Plot:

    def fr2(self, G, nodes=None):
        axis = dict(showline=False,  # hide axis line, grid, ticklabels and  title
                    zeroline=False,
                    showgrid=False,
                    showticklabels=False,
                    title=''
                    )
        layout = Layout(title="Terrorist attack locations",
                        font=Font(size=12),
                        showlegend=False,
                        autosize=False,
                        width=2000,
                        height=2000,
                        xaxis=XAxis(axis),
                        yaxis=YAxis(axis),
                        margin=Margin(
                            l=40,
                            r=40,
                            b=85,
                            t=100,
                        ),
                        hovermode='closest',
                        annotations=Annotations([
                            Annotation(
                                showarrow=False,
                                text='This igraph.Graph has the Kamada-Kawai layout',
                                xref='paper',
                                yref='paper',
                                x=0,
                                y=-0.1,
                                xanchor='left',
                                yanchor='bottom',
                                font=Font(
                                    size=14
                                )
                            )
                        ]),
                        )
        pos = nx.get_node_attributes(G, 'pos')
        N = G.nodes
        E = G.edges

        Xv = [pos[k][0] for k in N if not isinstance(k, float)]
        Yv = [pos[k][1] for k in N if not isinstance(k, float)]

        print('Nodes after', len(Xv))
        print('Nodes after', len(Yv))
        Xed = []
        Yed = []
        for edge in E:
            if isinstance(edge[0], float) or isinstance(edge[1], float):
                continue
            Xed += [pos[edge[0]][0], pos[edge[1]][0], None]
            Yed += [pos[edge[0]][1], pos[edge[1]][1], None]

        print('Edges after', len(Xed) / 3)
        print('Edges after', len(Yed) / 3)
        return

        trace3 = Scatter(x=Xed,
                         y=Yed,
                         mode='lines',
                         line=Line(color='rgb(210,0,0)', width=1),
                         hoverinfo='none'
                         )
        trace4 = Scatter(x=Xv,
                         y=Yv,
                         mode='markers',
                         name='net',
                         marker=Marker(symbol='dot',
                                       size=5,
                                       color='#6959CD',
                                       line=Line(color='rgb(50,50,50)', width=0.5)
                                       ),
                         text=nodes,
                         hoverinfo='text'
                         )

        sf = shapefile.Reader('TM_WORLD_BORDERS_SIMPL')

        shapes = sf.shapes()

        shape_graph = nx.Graph()
        for shape in shapes:
            for point_num in range(0, len(shape.points)):
                shape_graph.add_node(str(shape.points[point_num]), pos=shape.points[point_num])
            for point_num in range(0, len(shape.points) - 1):
                shape_graph.add_edge(str(shape.points[point_num]), str(shape.points[point_num + 1]))

        pos = nx.get_node_attributes(shape_graph, 'pos')
        N = shape_graph.nodes
        E = shape_graph.edges
        Xv = [pos[k][0] for k in N]
        Yv = [pos[k][1] for k in N]
        Xed = []
        Yed = []
        for edge in E:
            Xed += [pos[edge[0]][0], pos[edge[1]][0], None]
            Yed += [pos[edge[0]][1], pos[edge[1]][1], None]

        trace5 = Scatter(x=Xed,
                         y=Yed,
                         mode='lines',
                         line=Line(color='rgb(210,210,210)', width=1),
                         hoverinfo='none'
                         )
        trace6 = Scatter(x=Xv,
                         y=Yv,
                         mode='markers',
                         name='net',
                         marker=Marker(symbol='dot',
                                       size=5,
                                       color='#6959CD',
                                       line=Line(color='rgb(50,50,50)', width=0.5)
                                       ),
                         text=nodes,
                         hoverinfo='none'
                         )

        print('Total edges in border graph', len(shape_graph.edges))

        annot = "This networkx.Graph has the Fruchterman-Reingold layout<br>Code:" + \
                "<a href='http://nbviewer.ipython.org/gist/empet/07ea33b2e4e0b84193bd'> [2]</a>"

        data1 = Data([trace3, trace4, trace5])
        fig1 = Figure(data=data1, layout=layout)
        fig1['layout']['annotations'][0]['text'] = annot
        plotly.offline.plot(fig1, filename='Coautorship-network-nx.html')

    def fruchterman_reingold(self, G):
        # G = nx.random_geometric_graph(200, 0.125)
        pos = nx.get_node_attributes(G, 'pos')

        dmin = 1
        ncenter = 0
        for n in pos:
            x, y = pos[n]
            d = (x - 0.5) ** 2 + (y - 0.5) ** 2
            if d < dmin:
                ncenter = n
                dmin = d

        edge_trace = Scatter(
            x=[],
            y=[],
            line=Line(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        for edge in G.edges():
            x0, y0 = G.node[edge[0]]['pos']
            x1, y1 = G.node[edge[1]]['pos']
            edge_trace['x'] += [x0, x1, None]
            edge_trace['y'] += [y0, y1, None]

        node_trace = Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            marker=Marker(
                showscale=True,
                # colorscale options
                # 'Greys' | 'Greens' | 'Bluered' | 'Hot' | 'Picnic' | 'Portland' |
                # Jet' | 'RdBu' | 'Blackbody' | 'Earth' | 'Electric' | 'YIOrRd' | 'YIGnBu'
                colorscale='YIGnBu',
                reversescale=True,
                color=[],
                size=10,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                ),
                line=dict(width=2)))

        for node in G.nodes():
            x, y = G.node[node]['pos']
            node_trace['x'].append(x)
            node_trace['y'].append(y)

        fig = Figure(data=Data([edge_trace, node_trace]),
                     layout=Layout(
                         title='<br>Network graph made with Python',
                         titlefont=dict(size=16),
                         showlegend=False,
                         hovermode='closest',
                         margin=dict(b=20, l=5, r=5, t=40),
                         annotations=[dict(
                             text="Python code: <a href='https://plot.ly/ipython-notebooks/network-graphs/'> https://plot.ly/ipython-notebooks/network-graphs/</a>",
                             showarrow=False,
                             xref="paper", yref="paper",
                             x=0.005, y=-0.002)],
                         xaxis=XAxis(showgrid=False, zeroline=False, showticklabels=False),
                         yaxis=YAxis(showgrid=False, zeroline=False, showticklabels=False)))

        plotly.offline.plot(fig, filename='networkx.html')