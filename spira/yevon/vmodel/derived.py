import numpy as np

from copy import deepcopy

from spira.yevon.process.gdsii_layer import Layer
from spira.yevon.process.gdsii_layer import __DerivedDoubleLayer__
from spira.yevon.process.gdsii_layer import __DerivedLayerAnd__
from spira.yevon.process.gdsii_layer import __DerivedLayerXor__

from spira.yevon.gdsii.elem_list import ElementList
from spira.yevon.gdsii.polygon import Polygon
from spira.yevon.gdsii.polygon_group import PolygonGroup
from spira.yevon.filters.layer_filter import LayerFilterAllow
from spira.yevon.geometry.edges.edges import Edge
from spira.yevon.process import get_rule_deck


RDD = get_rule_deck()


__all__ = [
    'get_derived_elements',
]


def _derived_elements(elems, derived_layer):
    """ Derived elements are generated from derived layers using
    layer operations as specified in the RDD. """

    if isinstance(derived_layer, Layer):
        LF = LayerFilterAllow(layers=[derived_layer])
        el = LF(elems.polygons)
        pg = PolygonGroup(elements=el, layer=derived_layer)
        return pg
    elif isinstance(derived_layer, __DerivedDoubleLayer__):
        p1 = _derived_elements(elems, derived_layer.layer1)
        p2 = _derived_elements(elems, derived_layer.layer2)
        if isinstance(derived_layer, __DerivedLayerAnd__):
            pg = p1 & p2
        elif isinstance(derived_layer, __DerivedLayerXor__):
            pg = p1 ^ p2
        return pg
    else:
        raise Exception("Unexpected type for parameter 'derived_layer' : %s" % str(type(derived_layer)))


def get_derived_elements(elements, mapping, store_as_edge=False):
    """ Given a list of elements and a list of tuples (DerivedLayer, PPLayer),
    create new elements according to the boolean operations of the DerivedLayer
    and place these elements on the specified PPLayer. """

    derived_layers = mapping.keys()
    export_layers = mapping.values()
    elems = ElementList()
    for derived_layer, export_layer in zip(derived_layers, export_layers):
        layer = deepcopy(export_layer)
        pg = _derived_elements(elems=elements, derived_layer=derived_layer)
        for p in pg.elements:
            if store_as_edge is True:
                elems += Edge(shape=p.shape, layer=layer)
            else:
                elems += Polygon(shape=p.shape, layer=layer)
    return elems


# TODO: Implement this using an adapter?
def get_derived_edge_ports():
    """ Generate ports from the derived edge polygons. """
    pass





