import numpy as np
import networkx as nx
import spira.all as spira

from copy import deepcopy
from spira.core.parameters.variables import GraphParameter, StringParameter
from spira.core.parameters.descriptor import Parameter
from spira.yevon.geometry.coord import Coord
from spira.yevon.vmodel.geometry import GeometryParameter
from spira.yevon.geometry.ports.base import __Port__
from spira.yevon.process import get_rule_deck


RDD = get_rule_deck()


__all__ = ['Net']


ELM_TYPE = {1: 'line', 2: 'triangle'}


from spira.core.transformable import Transformable
from spira.core.parameters.initializer import ParameterInitializer
class __Net__(Transformable, ParameterInitializer):
    """  """

    @property
    def count(self):
        return nx.number_of_nodes(self.g)


class Net(__Net__):
    """
    Constructs a graph from the physical geometry
    generated from the list of elements.
    """

    # g = GraphParameter()
    g = Parameter()

    mesh_data = Parameter(fdef_name='create_mesh_data')
    geometry = GeometryParameter(allow_none=True, default=None)

    lines = Parameter(fdef_name='create_lines')
    triangles = Parameter(fdef_name='create_triangles')
    physical_triangles = Parameter(fdef_name='create_physical_triangles')
    physical_lines = Parameter(fdef_name='create_physical_lines')

    name = StringParameter(default='no_name')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'g' in kwargs:
            self.g = kwargs['g']
        else:
            self.g = nx.Graph()
            self._generate_mesh_graph()

    def __repr__(self):
        if self.geometry is None:
            class_string = "[SPiRA: Net] (name \'{}\', nodes {})"
            return class_string.format(self.name, self.count)
        else:
            class_string = "[SPiRA: Net] (name \'{}\', nodes {}, geometry {})"
            return class_string.format(self.name, self.count, self.geometry.process.symbol)

    def __str__(self):
        return self.__repr__()

    def _generate_mesh_graph(self):
        """ Create a graph from the meshed geometry. """
        ll = len(self.mesh_data.points)
        A = np.zeros((ll, ll), dtype=np.int64)

        for n, triangle in enumerate(self.triangles):
            self._add_edges(n, triangle, A)
        for n, triangle in enumerate(self.triangles):
            self._add_positions(n, triangle)

    def _add_edges(self, n, tri, A):
        def update_adj(self, t1, adj_mat, v_pair):
            if (adj_mat[v_pair[0]][v_pair[1]] != 0):
                t2 = adj_mat[v_pair[0]][v_pair[1]] - 1
                self.g.add_edge(t1, t2, label=None)
            else:
                adj_mat[v_pair[0]][v_pair[1]] = t1 + 1
                adj_mat[v_pair[1]][v_pair[0]] = t1 + 1
        v1 = [tri[0], tri[1], tri[2]]
        v2 = [tri[1], tri[2], tri[0]]
        for v_pair in list(zip(v1, v2)):
            update_adj(self, n, A, v_pair)

    def _add_positions(self, n, triangle):
        from spira import settings
        pp = self.mesh_data.points
        grids_per_unit = settings.get_grids_per_unit()
        n1, n2, n3 = pp[triangle[0]], pp[triangle[1]], pp[triangle[2]]
        x = (n1[0] + n2[0] + n3[0]) / 3
        y = (n1[1] + n2[1] + n3[1]) / 3
        x = x * grids_per_unit
        y = y * grids_per_unit
        self.g.node[n]['vertex'] = triangle
        self.g.node[n]['position'] = Coord(x, y)
        self.g.node[n]['display'] = RDD.DISPLAY.STYLE_SET[RDD.PLAYER.METAL]

    def create_mesh_data(self):
        return self.geometry.mesh_data

    def add_new_node(self, n, D, polygon, position, display):
        num = self.g.number_of_nodes()
        self.g.add_node(num+1, position=position, device_reference=D, process_polygon=polygon, display=display)
        self.g.add_edge(n, num+1)

    def create_triangles(self):
        if 'triangle' not in self.mesh_data.cells:
            raise ValueError('Triangle not found in cells')
        return self.mesh_data.cells['triangle']

    def create_lines(self):
        if 'line' not in self.mesh_data.cells:
            raise ValueError('Line not found in cells')
        return self.mesh_data.cells['line']

    def create_physical_triangles(self):
        if 'triangle' not in self.mesh_data.cell_data:
            raise ValueError('Triangle not in meshio cell_data')
        if 'gmsh:physical' not in self.mesh_data.cell_data['triangle']:
            raise ValueError('Physical not found in meshio triangle')
        return self.mesh_data.cell_data['triangle']['gmsh:physical'].tolist()

    def create_physical_lines(self):
        if 'line' not in self.mesh_data.cell_data:
            raise ValueError('Line not in meshio cell_data')
        if 'gmsh:physical' not in self.mesh_data.cell_data['line']:
            raise ValueError('Physical not found in meshio triangle')
        return self.mesh_data.cell_data['line']['gmsh:physical'].tolist()

    def process_triangles(self):
        """
        Arguments
        ---------
        tri : list
            The surface_id of the triangle
            corresponding to the index value.
        name -> 5_0_1 (layer_datatype_polyid)
        value -> [1 2] (1=surface_id 2=triangle)
        """

        triangles = {}
        for name, value in self.mesh_data.field_data.items():
            for n in self.g.nodes():
                surface_id = value[0]
                if self.physical_triangles[n] == surface_id:
                    layer = int(name.split('_')[0])
                    datatype = int(name.split('_')[1])
                    key = (layer, datatype)
                    if key in triangles:
                        triangles[key].append(n)
                    else:
                        triangles[key] = [n]
        return triangles

    def process_lines(self):
        """
        Arguments
        ---------
        tri : list
            The surface_id of the triangle
            corresponding to the index value.
        name -> 5_0_1 (layer_datatype_polyid)
        value -> [1 2] (1=surface_id 2=triangle)
        """

        lines = {}
        for name, value in self.mesh_data.field_data.items():
            # print(name, value)
            # print(self.physical_lines)
            for n in self.physical_lines:
                line_id = value[0]
                if n == line_id:
                    # print(name)
                    # print(value)
                    # print('')
                    polygon_string = name.split('_')[0]
                    polygon_uid = int(name.split('_')[1])
                    key = (polygon_string, polygon_uid)
                    if key in lines:
                        lines[key].append(n)
                    else:
                        lines[key] = [n]
        return lines

    def get_triangles_connected_to_line(self):
        """
        Labeling of an edge line:
        polygon_uid_i [line elm_type]
        [SPiRA: Polygon 'M5']_17_0 [2 1]

        Labeling of triangle:
        layer datatype [triangle elm_type]
        50_1_0_0 [1 2]
        """

        # lines = []
        # for v in self.process_lines().values():
        #     lines.extend(v)
        # print(lines)
        # triangles = {}
        # for n in nodes:
        #     for node, triangle in enumerate(self.triangles):
        #         if n == node:
        #             triangles[n] = triangle
        # return triangles

    def triangle_nodes(self):
        """ Get triangle field_data in list form. """
        nodes = []
        for v in self.process_triangles().values():
            nodes.extend(v)
        triangles = {}
        for n in nodes:
            for node, triangle in enumerate(self.triangles):
                if n == node:
                    triangles[n] = triangle
        return triangles

    def transform(self, transformation):
        for n in self.g.nodes():
            self.g.node[n]['position'] = transformation.apply_to_coord(self.g.node[n]['position'])
        return self




# FIXME: Maybe convert this to a BranchList class.
class CellNet(__Net__):
    """  """

    _ID = 0

    __stored_paths__ = []
    __branch_nodes__ = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __remove_nodes__(self):
        """
        Nodes to be removed:
        1. Are not a branch node.
        2. Are not a device node.
        3. Branch nodes must equal the branch id.
        """
        locked_nodes = []
        remove_nodes = []
        text = self.__get_called_id__()
        for n in self.g.nodes():
            if 'branch_node' in self.g.node[n]:
                if isinstance(self.g.node[n]['branch_node'], spira.Label):
                    if self.g.node[n]['branch_node'].text == text:
                        locked_nodes.append(n)
            elif 'device_reference' in self.g.node[n]:
                D = self.g.node[n]['device_reference']
                if isinstance(D, spira.Port):
                    locked_nodes.append(n)
                elif isinstance(D, spira.ContactPort):
                    locked_nodes.append(n)
        for n in self.g.nodes():
            if n not in locked_nodes:
                remove_nodes.append(n)
        self.g.remove_nodes_from(remove_nodes)

    def __validate_path__(self, path):
        # from spira.netex.devices import Via
        """ Test if path contains masternodes. """
        valid = True
        s, t = path[0], path[-1]
        if self.__is_path_stored__(s, t):
            valid = False
        if s not in self.__branch_nodes__:
            valid = False
        if t not in self.__branch_nodes__:
            valid = False
        for n in path[1:-1]:
            if 'device_reference' in self.g.node[n]:
                D = self.g.node[n]['device_reference']
                # if issubclass(type(D), __Port__):
                #     if not isinstance(D, spira.Port):
                #         valid = False
                if issubclass(type(D), __Port__):
                    valid = False
                if issubclass(type(D), spira.SRef):
                    valid = False
        return valid

    def __store_branch_paths__(self, s, t):
        if nx.has_path(self.g, s, t):
            p = nx.shortest_path(self.g, source=s, target=t)
            if self.__validate_path__(p):
                self.__stored_paths__.append(p)

    def __is_path_stored__(self, s, t):
        for path in self.__stored_paths__:
            if (s in path) and (t in path):
                return True
        return False

    def __reset_stored_paths__(self):
        self.__stored_paths__ = []

    def __increment_caller_id__(self):
        self._ID += 1

    def __get_called_id__(self):
        return '__{}__'.format(self._ID)

    def __branch_id__(self, i, s, t):
        ntype = 'nodetype: {}'.format('branch_node')
        number = 'number: {}'.format(i)

        Ds = self.g.node[s]['device_reference']
        Dt = self.g.node[t]['device_reference']

        if issubclass(type(Ds), spira.SRef):
            source = 'source: {}'.format(Ds.reference.name)
        # elif isinstance(Ds, spira.Port):
        elif isinstance(Ds, (spira.ContactPort, spira.Port)):
            source = 'source: {}'.format(Ds.name)

        if issubclass(type(Dt), spira.SRef):
            target = 'target: {}'.format(Dt.reference.name)
        # elif isinstance(Dt, spira.spira.Port):
        elif isinstance(Ds, (spira.ContactPort, spira.Port)):
            target = 'target: {}'.format(Dt.name)

        # if issubclass(type(Ds), spira.SRef):
        #     source = 'source: {}'.format(Ds.reference.name)
        # elif issubclass(type(Ds), __Port__):
        #     if isinstance(Ds, spira.Port):
        #         source = 'source: {}'.format(Ds.name)

        # if issubclass(type(Dt), spira.SRef):
        #     target = 'target: {}'.format(Dt.reference.name)
        # elif issubclass(type(Dt), __Port__):
        #     if not isinstance(Dt, spira.spira.Port):
        #         target = 'target: {}'.format(Dt.name)

        return "\n".join([ntype, number, source, target])

    @property
    def branch_nodes(self):
        """ Nodes that defines different conducting branches. """
        branch_nodes = list()
        for n in self.g.nodes():
            if 'device_reference' in self.g.node[n]:
                D = self.g.node[n]['device_reference']
                if isinstance(D, spira.SRef):
                    branch_nodes.append(n)
                if isinstance(D, spira.Port):
                    branch_nodes.append(n)
                if isinstance(D, spira.ContactPort):
                    branch_nodes.append(n)
                if isinstance(D, spira.BranchPort):
                    branch_nodes.append(n)
        return branch_nodes

    @property
    def master_nodes(self):
        """ Excludes via devices with only two edges (series). """
        from spira.netex.devices import Via
        branch_nodes = list()
        for n in self.g.nodes():
            if 'device_reference' in self.g.node[n]:
                D = self.g.node[n]['device_reference']
                if issubclass(type(D), spira.SRef):
                    if issubclass(type(D.ref), Via):
                        if len([i for i in self.g[n]]) > 2:
                            branch_nodes.append(n)
                    else:
                        branch_nodes.append(n)
                if issubclass(type(D), __Port__):
                    branch_nodes.append(n)
        return branch_nodes

    @property
    def terminal_nodes(self):
        """ Nodes that defines different conducting branches. """
        branch_nodes = list()
        for n in self.g.nodes():
            if 'device_reference' in self.g.node[n]:
                D = self.g.node[n]['device_reference']
                if issubclass(type(D), spira.Port):
                    if not isinstance(D, spira.spira.Port):
                        branch_nodes.append(n)
        return branch_nodes

    def detect_dummy_nodes(self):

        for sg in nx.connected_component_subgraphs(self.g, copy=True):
            s = self.__branch_nodes__[0]

            paths = []
            for t in filter(lambda x: x not in [s], self.__branch_nodes__):
                # if nx.has_path(self.g, s, t):
                #     p = nx.shortest_path(self.g, source=s, target=t)
                #     paths.append(p)
                if nx.has_path(self.g, s, t):
                    for p in nx.all_simple_paths(self.g, source=s, target=t):
                        paths.append(p)

            new_paths = []
            for p1 in paths:
                for p2 in filter(lambda x: x not in [p1], paths):
                    set_2 = frozenset(p2)
                    intersecting_paths = [x for x in p1 if x in set_2]
                    new_paths.append(intersecting_paths)

            dummies = set()
            for path in new_paths:
                p = list(path)
                dummies.add(p[-1])

            for i, n in enumerate(dummies):
                if 'branch_node' in self.g.node[n]:
                    N = self.g.node[n]['branch_node']
                    port = BranchPort(
                        name='D{}'.format(i), 
                        midpoint=N.position, 
                        process=RDD.PROCESS.M2, 
                        purpose=RDD.PURPOSE.PORT.BRANCH
                    )
                    self.g.node[n]['device_reference'] = port
                    self.g.node[n]['display'] = RDD.DISPLAY.STYLE_SET[port.layer]
                    del self.g.node[n]['branch_node']

    def generate_branches(self):
        """  """

        self.__reset_stored_paths__()
        self.__increment_caller_id__()

        self.__branch_nodes__ = self.branch_nodes

        for sg in nx.connected_component_subgraphs(self.g, copy=True):
            for s in self.__branch_nodes__:
                # targets = filter(lambda x: x not in [s], self.master_nodes)
                targets = filter(lambda x: x not in [s], self.__branch_nodes__)
                for t in targets:
                    self.__store_branch_paths__(s, t)

            for i, path in enumerate(self.__stored_paths__):
                text = self.__get_called_id__()
                node_id = self.__branch_id__(i, path[0], path[-1])
                for n in path[1:-1]:
                    ply = self.g.node[n]['process_polygon']
                    label = spira.Label(position=ply.center, text=text, layer=ply.layer)
                    self.g.node[n]['branch_node'] = label

        self.__remove_nodes__()

        return self.g


# TODO!!!
# Create a T-shape and a L-shape.
# Create cross-over connector.



