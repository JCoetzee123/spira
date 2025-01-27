import os
import gdspy
import spira.all as spira
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.offline as offline
from spira import log as LOG
from spira.yevon.io import *
from spira.yevon.utils.geometry import scale_coord_down as scd
from spira.core.typed_graph import EdgeCapacitor, EdgeInductor
from spira.yevon.visualization import color
from spira import settings
from spira.core.outputs.base import Outputs
from spira.yevon.process import get_rule_deck


RDD = get_rule_deck()


class PlotlyGraph(object):

    def netlist_output(self):
        self._plotly_netlist(G=self.netlist.g, graphname=self.name)

    def _plotly_netlist(self, G, graphname, labeltext='id'):
        edges = self._create_edges(G)
        nodes = self._create_nodes(G, labeltext)

        edge_trace = go.Scatter(
            x=edges['x_pos'],
            y=edges['y_pos'],
            line=dict(width=1.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        node_trace = go.Scatter(
            x=nodes['x_pos'],
            y=nodes['y_pos'],
            text=nodes['text'],
            name='markers',
            mode='markers',
            hoverinfo='text',
            marker=dict(
                color=nodes['color'],
                size=30,
                line=dict(width=2))
            )

        edge_label_trace = go.Scatter(
            x=edges['x_labels'],
            y=edges['y_labels'],
            text=edges['text'],
            mode='markers',
            hoverinfo='text',
            marker=dict(
                color='#6666FF',
                size=2,
                line=dict(width=4))
            )

        fig = go.Figure(
            data=[edge_trace, node_trace, edge_label_trace],
            layout=go.Layout(
                title='<br>' + graphname,
                titlefont=dict(size=24),
                showlegend=False,
                width=1900,
                height=900,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=20),
                xaxis=go.layout.XAxis(
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False
                ),
                yaxis=go.layout.YAxis(
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False
                )
            )
        )

        directory = os.getcwd() + '/debug/'
        file_name = directory + str(graphname) + '.html'

        if not os.path.exists(directory):
            os.makedirs(directory)

        offline.plot(fig, filename=file_name)

    def _create_edges(self, G):

        edges = {}

        edges['x_pos'] = []
        edges['y_pos'] = []

        edges['x_labels'] = []
        edges['y_labels'] = []

        edges['text'] = []

        for e in G.edges():
            x0, y0 = G.node[e[0]]['position']
            x1, y1 = G.node[e[1]]['position']

            edges['x_pos'] += [x0, x1, None]
            edges['y_pos'] += [y0, y1, None]

            x = x0 + (x1-x0)/2.0
            y = y0 + (y1-y0)/2.0

            edges['x_labels'].append(x)
            edges['y_labels'].append(y)

            edge = G[e[0]][e[1]]

            if 'process_polygon' in edge:
                if isinstance(edge['process_polygon'], EdgeCapacitor):
                    edges['text'].append(edge['process_polygon'].id)
                if isinstance(edge['process_polygon'], EdgeInductor):
                    edges['text'].append(edge['process_polygon'].id)

        return edges

    def _create_nodes(self, G, labeltext):

        nodes = {}
        nodes['x_pos'] = []
        nodes['y_pos'] = []
        nodes['text'] = []
        nodes['color'] = []

        for n in G.nodes():
            x, y = G.node[n]['position']
            nodes['x_pos'].append(x)
            nodes['y_pos'].append(y)

            node_value = None
            if 'device_reference' in G.node[n]:
                node_value = G.node[n]['device_reference']
            elif 'branch_node' in G.node[n]:
                node_value = G.node[n]['branch_node']
            elif 'process_polygon' in G.node[n]:
                node_value = G.node[n]['process_polygon']

            if node_value is not None:
                nodes['text'].append('({}) {}'.format(n, str(node_value)))
                nodes['color'].append(G.node[n]['display'].color.hexcode)

        return nodes


class BokehGraph(object):

    def bokeh_netlist(self):
        pass


Outputs.mixin(PlotlyGraph)
Outputs.mixin(BokehGraph)

