import spira
from spira import param
from copy import deepcopy
from spira.lpe.containers import __CellContainer__


RDD = spira.get_rule_deck()


class BoundingBox(__CellContainer__):
    """ Add a GROUND bbox to Device for primitive and DRC
    detection, since GROUND is only in Mask Cell. """

    midpoint = param.MidPointField()
    rotation = param.FloatField(default=0)
    reflection = param.BoolField(default=False)
    magnification = param.FloatField(default=1)

    def create_elementals(self, elems):
        setter = {}
        c_cell = deepcopy(self.cell)
        polygons = c_cell.elementals.flat_copy()
        for p in polygons:
            layer = p.gdslayer.number
            setter[layer] = 'not_set'
        for p in polygons:
            for pl in RDD.PLAYER.get_physical_layers(purposes=['METAL', 'GND']):
                if pl.layer == p.gdslayer:
                    if setter[pl.layer.number] == 'not_set':
                        l1 = spira.Layer(name='BoundingBox', number=pl.layer.number, datatype=9)
                        ply = spira.Polygons(shape=self.cell.pbox, gdslayer=l1)
                        if self.rotation:
                            ply.rotate(angle=self.rotation)
                        if self.reflection:
                            ply.reflect()
                        ply.center = self.midpoint
                        elems += ply
                        setter[pl.layer.number] = 'already_set'
        return elems