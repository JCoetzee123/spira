import gdspy

from copy import deepcopy
from spira.yevon.utils import clipping
from spira.yevon.gdsii.group import Group
from spira.yevon.gdsii.polygon import Polygon
from spira.yevon.gdsii.elem_list import ElementList
from spira.yevon.gdsii.base import __LayerElement__
from spira.yevon.process import get_rule_deck


RDD = get_rule_deck()


__all__ = ['PolygonGroup']


class PolygonGroup(Group, __LayerElement__):
    """ 
    Collection of polygon elements. Boolean
    operation can be applied on these polygons.

    Example
    -------
    >>> cp = spira.PolygonGroup()
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        class_string = "[SPiRA: PolygonGroup] (polygons {}, process {}, purpose {})"
        return class_string.format(self.count, self.process, self.purpose)

    def __str__(self):
        return self.__repr__()

    def __and__(self, other):
        el = ElementList()
        for e1 in self.elements:
            for e2 in other.elements:
                # e1 = deepcopy(e1)
                # e2 = deepcopy(e2)
                # shape1 = e1.shape.transform_copy(e1.transformation)
                # shape2 = e2.shape.transform_copy(e2.transformation)
                shape1 = deepcopy(e1.shape).transform(e1.transformation)
                shape2 = deepcopy(e2.shape).transform(e2.transformation)
                # if shape1 != shape2:
                # if e1.shape != e2.shape:
                # if (e1.shape != e2.shape) and (e1.layer == e2.layer):
                # if (e1.shape != e2.shape) and (e1.layer.process == e2.layer.process):
                if (shape1 != shape2) and (e1.layer.process == e2.layer.process):
                    shapes = shape1 & shape2
                    # print(shape1.points)
                    # print(shape2.points)
                    # print(shapes)
                    # print('')
                    for shape in shapes:
                        el += Polygon(shape=shape, layer=e1.layer)


                    # polygons = e1.intersection(e2)
                    # for p in polygons:
                    #     p.layer.purpose = RDD.PURPOSE.INTERSECTED
                    # for p in polygons:
                    #     el += p
        self.elements = el
        return self

    def __xor__(self, other):
        pts1, pts2 = [], []
        for e in self.elements:
            s1 = e.shape.transform_copy(e.transformation)
            pts1.append(s1.points)
        for e in other.elements:
            s1 = e.shape.transform_copy(e.transformation)
            pts2.append(s1.points)

        if (len(pts1) > 0) and (len(pts2) > 0):
            p1 = gdspy.PolygonSet(polygons=pts1)
            p2 = gdspy.PolygonSet(polygons=pts2)
    
            ply = gdspy.fast_boolean(p1, p2, operation='not')
            elems = ElementList()
            for points in ply.polygons:
                elems += Polygon(shape=points, layer=self.layer)
            self.elements = elems
        return self

    def __or__(self, other):
        raise ValueError('Not Implemented!')

    @property
    def intersect(self):
        elems = ElementList()
        el1 = deepcopy(self.elements)
        el2 = deepcopy(self.elements)
        for i, e1 in enumerate(el1):
            for j, e2 in enumerate(el2):
                if e1.shape != e2.shape:
                    # polygons = e1.intersection(e2)
                    polygons = e1 & e2
                    for p in polygons:
                        p.layer.purpose = RDD.PURPOSE.INTERSECTED
                    for p in polygons:
                        elems += p
        self.elements = elems
        return self

    @property
    def merge(self):
        elems = ElementList()
        if len(self.elements) > 1:
            points = []
            for e in self.elements:
                shape = e.shape.transform(e.transformation)
                points.append(shape.points)
            merged_points = clipping.boolean(subj=points, clip_type='or')
            for uid, pts in enumerate(merged_points):
                elems += Polygon(shape=pts, layer=self.layer)
        else:
            elems = self.elements
        self.elements = elems
        return self

    @property
    def count(self):
        return len(self.elements)

    @property
    def process(self):
        layer = RDD.GDSII.IMPORT_LAYER_MAP[self.layer]
        return layer.process

    @property
    def purpose(self):
        layer = RDD.GDSII.IMPORT_LAYER_MAP[self.layer]
        return layer.purpose

    @property
    def center(self):
        return self.bbox_info.center




