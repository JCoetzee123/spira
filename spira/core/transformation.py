import numpy as np
from numpy.linalg import norm
import spira.all as spira

from spira.core.initializer import FieldInitializer
from spira.core.param.restrictions import RestrictType
from spira.core.descriptor import DataFieldDescriptor


class Transform(FieldInitializer):
    """ Abstract base class for generic transform. """

    def apply_to_object(self, item):
        pass

    def __call__(self, item):
        if isinstance(item, None):
            return self
        if isinstance(item, Transform):
            return item + self
        else:
            raise ValueError('Call not implemented!')

    def __add__(self, other):
        if other is None: 
            return CompoundTransform([self])
        return CompoundTransform([self, other])

    def __sub__(self, other):
        if other is None: 
            return CompoundTransform([self])
        if isinstance(other, ReversibleTransform):
            return CompoundTransform([self, -other])
        else:
            raise TypeError("Cannot subtract an irreversible transform")

    def is_identity(self):
        return True


class ReversibleTransform(Transform):
    """ Base class for a transformation that can be reversed. """

    def reverse(self, item):
        if isinstance(item, list):
            print('FAIL!')
            # from .shape import Shape
            # L = Shape(item)
            # L.reverse_transform(self)
            # return L
        else:
            return item.reverse_transform(self)

    def __add__(self, other):
        if other is None:
            return ReversibleCompoundTransform([self])
        if isinstance(other, ReversibleTransform):
            return ReversibleCompoundTransform([self, other])
        else:
            return CompoundTransform([self, other])

    def __sub__(self, other):
        if other is None: 
            return ReversibleCompoundTransform([self])
        if isinstance(other, ReversibleTransform):
            return ReversibleCompoundTransform([self, -other])
        else:
            raise TypeError("Cannot subtract an irreversible transform")

    def __neg__(self):
        pass


class CompoundTransform(Transform):
    """ A store for the concatenation of transforms. """

    def __init__(self, transforms=[], **kwargs):
        if isinstance(transforms, list):
            self.__subtransforms__ = transforms
        elif isinstance(transforms, CompoundTransform):
            self.__subtransforms__ = []
            self.__subtransforms__.extend(transforms)
        else:            
            self.__subtransforms__ = [transforms]
        super().__init__(**kwargs)

    def __add__(self, other):
        T = CompoundTransform(self)
        T.add(other)
        return T

    def __iadd__(self, other):
        self.add(other)
        return self

    def add(self, other):
        if other is None: 
            return 
        if isinstance(other, CompoundTransform):
            for c in other.__subtransforms__:
                self.add(other)
        elif isinstance(other, Transform):
            # self.elements.append(other)
            self.__subtransforms__.append(other)
        else:
            raise TypeError("Cannot add object of type " + str(type(other)) + " to transform")
        
    def apply_to_object(self, item):
        """ Apply transformation to elementals."""
        for c in self.__subtransforms__:
            item = c.apply_to_object(item)
        return item

    def is_identity(self):
        for c in self.__subtransforms__:
            if not c.is_identity(): 
                return False
        return True


class ReversibleCompoundTransform(CompoundTransform, ReversibleTransform):
    """ A store for the concatenation of reversible transformas. """

    def __make_irreversible__(self):
        self.__class__ = CompoundTransform

    def reverse(self, item):
        if isinstance(item, list):
            print('FAIL!!!')
            # from .shape import Shape
            # L = Shape(item)
            # for c in reversed(self.__subtransforms__):
            #     L = c.reverse(L)
            # return L
        else:
            for c in reversed(self.__subtransforms__):
                item = c.reverse(item)

    def reverse_on_coord(self, coord):
        for c in reversed(self.__subtransforms__):
            coord = c.reverse_on_coord(coord)
        return coord

    def reverse_on_array(self, coords):
        for c in reversed(self.__subtransforms__):
            coords = c.reverse_on_array(coords)
        return coords

    def __add__(self, other):
        T = ReversibleCompoundTransform(self)
        if other != None: 
            T.add(other)
        return T

    def __iadd__(self, other):
        self.add(other)
        return self

    def __sub__(self, other):
        T = ReversibleCompoundTransform(self)
        T.add(-other)
        return T

    def __isub__(self, other):
        self.add(-other)
        return self

    def add(self, other):
        if isinstance(other, CompoundTransform):
            for c in other.__subtransforms__:
                self.add(other)
        if isinstance(other, ReversibleTransform):
            # self.elements.append(other)
            self.__subtransforms__.append(other)
        elif isinstance(other, Transform):
            self.__make_irreversible__()
            # self.elements.append(other)
            self.__subtransforms__.append(other)
        else:
            raise TypeError("Cannot add object of type " + str(type(other)) + " to transform")

    def __neg__(self):
        T = ReversibleCompoundTransform()
        for c in reversed(self):
            T.add(-c)
        return T


def TransformationField(name='noname', number=0, datatype=0, **kwargs):
    from spira.core.transformation import Transform
    R = RestrictType(Transform)
    return DataFieldDescriptor(restrictions=R, **kwargs)
