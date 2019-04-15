import spira.all as spira
import numpy as np
from copy import deepcopy
from numpy.linalg import norm
from spira.core.mixin import MixinBowl
from spira.core.transformation import TransformationField


class __Transformable__(MixinBowl):

    def transform(self, transformation):
        return self

    def transform_copy(self, transformation):
        T = deepcopy(self)
        T.transform(transformation)
        return T

    def reverse_transform(self, transformation):
        return self.transform(-transformation)

    def reverse_transform_copy(self, transformation):
        T = deepcopy(self)
        T.reverse_transform(transformation)
        return T


class Transformable(__Transformable__):
    """ Object that can be transformed. """

    from spira.core.transformation import Transform

    __transform_type__ = Transform

    transformation = TransformationField(allow_none=True, default=None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # def __init__(self, transformation=None, **kwargs):
    #     if (not 'transformation' in kwargs) or (transformation != None):
    #         kwargs['transformation'] = transformation
    #     super().__init__(self, **kwargs)

    def transform(self, transformation=None):
        if isinstance(transformation, self.__transform_type__):
            # self.transformation = self.transformation + transformation
            if self.transformation is None:
                self.transformation = transformation
            else:
                self.transformation += transformation
        elif transformation is None:
            return
        else:
            raise TypeError("Wrong type " + str(type(transformation)) + " for transformation in Transformable")
        return self

    def expand_transform(self):
        """ Tries to propagate the transformation as deep 
        as possible in the hierarchy. """
        return self




