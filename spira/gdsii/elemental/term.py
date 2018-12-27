import spira
import numpy as np

from spira import param
from copy import copy, deepcopy
from spira.gdsii.elemental.port import PortAbstract
from spira.core.initializer import ElementalInitializer


class Term(PortAbstract):
    """
    Terminals are horizontal ports that connect SRef instances
    in the horizontal plane. They typcially represents the
    i/o ports of a components.

    Examples
    --------
    >>> term = spira.Term()
    """

    width = param.FloatField(default=2)
    length = param.FloatField(default=0.1)

    def __init__(self, port=None, polygon=None, **kwargs):
        super().__init__(port=port, polygon=polygon, **kwargs)

        from spira import shapes
        if polygon is None:
            rect_shape = shapes.RectangleShape(
                p1=[0, 0],
                p2=[self.width, self.length]
            )
            pp = spira.Polygons(
                shape=rect_shape,
                gdslayer=spira.Layer(number=65)
            )
            pp.rotate(angle=90-self.orientation, center=self.midpoint)
            pp.move(midpoint=pp.center, destination=self.midpoint)
            self.polygon = pp
        else:
            self.polygon = polygon

        arrow_shape = shapes.Arrow(
            rotation=self.orientation,
            wh = self.width/20,
            wb = self.width/40,
            hh = self.width/4,
            hb = self.width/2,
        )

        self.arrow = spira.Polygons(
            shape=arrow_shape,
            gdslayer=spira.Layer(number=77)
        )

    def __repr__(self):
        return ("[SPiRA: Term] (name {}, number {}, midpoint {}, " +
            "width {}, orientation {})").format(self.name,
            self.gdslayer.number, self.midpoint,
            self.width, self.orientation
        )

    def _copy(self):
        new_port = Term(parent=self.parent,
            name=self.name,
            midpoint=self.midpoint,
            width=self.width,
            length=self.length,
            gdslayer=deepcopy(self.gdslayer),
            poly_layer=deepcopy(self.poly_layer),
            text_layer=deepcopy(self.text_layer),
            orientation=self.orientation)
        return new_port










