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

    width = param.FloatField(default=2*1e6)
    length = param.FloatField(default=0.1*1e6)

    layer1 = param.LayerField()
    layer2 = param.LayerField()

    port1 = param.DataField(fdef_name='create_port1')
    port2 = param.DataField(fdef_name='create_port2')

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
                gdslayer=spira.Layer(number=63)
            )
            pp.rotate(angle=self.orientation, center=self.midpoint)
            # pp.rotate(angle=90-self.orientation, center=self.midpoint)
            pp.move(midpoint=pp.center, destination=self.midpoint)
            self.polygon = pp
        else:
            self.polygon = polygon

        arrow_shape = shapes.ArrowShape(
            a = self.width/10,
            b = self.width/20,
            c = self.width/5
        )

        arrow_shape.apply_merge
        # arrow_shape.rotate(angle=self.orientation)

        self.arrow = spira.Polygons(
            shape=arrow_shape,
            gdslayer=spira.Layer(number=77)
        )

        self.arrow.rotate(angle=self.orientation)
        # self.arrow.rotate(angle=90-self.orientation)

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
            orientation=self.orientation)
        return new_port

    def create_port1(self):
        port = spira.Port(name='P1', midpoint=self.midpoint, gdslayer=self.layer1)
        return port

    def create_port2(self):
        port = spira.Port(name='P2', midpoint=self.midpoint, gdslayer=self.layer2)
        return port










