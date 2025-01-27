import spira.all as spira
import numpy as np
from spira.yevon.gdsii.cell import Cell

from spira.yevon.geometry.route.route_shaper import RouteSimple
from spira.yevon.geometry.route.route_shaper import RouteGeneral
from spira.yevon.geometry.route.route_shaper import RouteArcShape
from spira.yevon.geometry.route.route_shaper import RouteSquareShape
from spira.yevon.process import get_rule_deck

from spira.yevon.geometry.ports.port import PortParameter
from spira.core.parameters.variables import *
from spira.yevon.process.gdsii_layer import LayerParameter
from spira.core.parameters.descriptor import Parameter, FunctionParameter
from copy import deepcopy


RDD = get_rule_deck()


class __Manhattan__(Cell):

    port1 = PortParameter(default=None)
    port2 = PortParameter(default=None)

    length = NumberParameter(default=20)
    layer = LayerParameter(number=13)
    # gds_layer = LayerParameter(number=13)
    # layer = PhysicalLayerParameter(default=RDD.DEF.PDEFAULT)
    # layer = PhysicalLayerParameter()
    # bend_type = StringParameter(default='rectangle')
    bend_type = StringParameter(default='circular')

    b1 = Parameter(fdef_name='create_arc_bend_1')
    b2 = Parameter(fdef_name='create_arc_bend_2')

    p1 = Parameter(fdef_name='create_port1_position')
    p2 = Parameter(fdef_name='create_port2_position')

    quadrant_one = Parameter(fdef_name='create_quadrant_one')
    quadrant_two = Parameter(fdef_name='create_quadrant_two')
    quadrant_three = Parameter(fdef_name='create_quadrant_three')
    quadrant_four = Parameter(fdef_name='create_quadrant_four')

    def get_radius(self):
        if self.port1 and self.port2:
            if hasattr(self, '__radius__'):
                return self.__radius__
            else:
                dx = abs(self.p2[0] - self.p1[0])
                dy = abs(self.p2[1] - self.p1[1])
                if dx <= dy:
                    self.__radius__ = dx*0.2
                elif dy <= dx:
                    self.__radius__ = dy*0.2
                # if dx <= dy:
                #     self.__radius__ = dx
                # elif dy <= dx:
                #     self.__radius__ = dy
                return self.__radius__

    def set_radius(self, value):
        self.__radius__ = value

    radius = FunctionParameter(get_radius, set_radius)

    def route_straight(self, p1, p2):
        route_shape = RouteSimple(
            port1=p1, port2=p2,
            path_type='straight',
            width_type='straight'
        )
        # route_shape.apply_merge
        R1 = RouteGeneral(route_shape=route_shape, connect_layer=self.layer)
        S = spira.SRef(R1)
        S.connect(port=S.ports['P1'], destination=p1)
        # S.connect(port=p1, destination=p2)

        # T = spira.Rotation(rotation=p2.orientation, center=p1.midpoint)
        # S.transform(T)
        # r1.rotate(angle=p2.orientation+90, center=R1.port_input.midpoint)
        # r1._rotate(rotation=p2.orientation-90, center=R1.port_input.midpoint)
        # S.move(midpoint=(0,0), destination=p1.midpoint)
        return S

    def create_port1_position(self):
        angle = np.mod(self.port1.orientation, 360)
        if angle == 90:
            p1 = [self.port1.midpoint[0], self.port1.midpoint[1]]
        if angle == 180:
            p1 = [self.port1.midpoint[1], -self.port1.midpoint[0]]
        if angle == 270:
            p1 = [-self.port1.midpoint[0], -self.port1.midpoint[1]]
        if angle == 0:
            p1 = [-self.port1.midpoint[1], self.port1.midpoint[0]]
        return p1

    def create_port2_position(self):
        angle = np.mod(self.port1.orientation, 360)
        if angle == 90:
            p2 = [self.port2.midpoint[0], self.port2.midpoint[1]]
        if angle == 180:
            p2 = [self.port2.midpoint[1], -self.port2.midpoint[0]]
        if angle == 270:
            p2 = [-self.port2.midpoint[0], -self.port2.midpoint[1]]
        if angle == 0:
            p2 = [-self.port2.midpoint[1], self.port2.midpoint[0]]
        return p2

    def create_arc_bend_1(self):
        if self.bend_type == 'circular':
            rs = RouteArcShape(
                radius=self.radius,
                width=self.port1.width,
                start_angle=0, theta=90
            )
        if self.bend_type == 'rectangle':
            rs = RouteSquareShape(
                width=self.port1.width,
                size=(self.radius, self.radius)
            )
        B1 = RouteGeneral(route_shape=rs, connect_layer=self.layer)
        return spira.SRef(B1)

    def create_arc_bend_2(self):
        if self.bend_type == 'circular':
            rs = RouteArcShape(
                radius=self.radius,
                width=self.port1.width,
                start_angle=0, theta=-90
            )
        if self.bend_type == 'rectangle':
            rs = RouteSquareShape(
                width=self.port1.width,
                size=(self.radius, self.radius)
            )
        B1 = RouteGeneral(
            route_shape=rs, 
            connect_layer=self.layer
        )
        return spira.SRef(B1)

