import spira
from spira import param
from copy import copy, deepcopy


RDD = spira.get_rule_deck()


class __TemplateCell__(spira.Cell):
    pass


class __TempatePrimitive__(__TemplateCell__):
    pass


class __TempateDevice__(__TemplateCell__):
    pass


class JunctionTemplate(__TempateDevice__):

    gdsdatatype = param.IntegerField(default=3)

    def create_elementals(self, elems):

        i4 = spira.SRef(RDD.VIAS.I4.PCELL, origin=(0,0))
        i5 = spira.SRef(RDD.VIAS.I5.PCELL, origin=(0,0))
        j5 = spira.SRef(RDD.VIAS.J5.PCELL, origin=(0,0))
        c5 = spira.SRef(RDD.VIAS.C5.PCELL, origin=(0,0))

        elems += i4
        elems += i5
        elems += j5
        elems += c5

        return elems


# from spira.lpe.structure import ComposeMLayers
# from spira.lpe.structure import ComposeNLayer

# class JunctionTemplate(__TempateDevice__):

#     pcell = param.BoolField()
#     gdsdatatype = param.IntegerField(default=3)

#     def create_cou(self):
#         elems = ElementList()
#         plys = [[[1, 0.5], [2.9, 7.3]]]
#         for pp in plys:
#             elems += Rectangle(point1=pp[0],
#                                point2=pp[1],
#                                layer=RDD.COU.LAYER)
#         # return elems
#         comp = ComposeMLayers(cell_elems=elems)
#         return SRef(comp)

#     def create_bas(self):
#         elems = ElementList()
#         p0 = [[[0.5, -1.4], [3.4, -0.3]]]
#         for pp in p0:
#             elems += Rectangle(point1=pp[0],
#                                point2=pp[1],
#                                layer=RDD.BAS.LAYER)
#         # return elems
#         comp = ComposeMLayers(cell_elems=elems)
#         return SRef(comp)

#     def create_res(self):
#         elems = ElementList()
#         p0 = [[[0.3, 0.3], [3.6, 3]],
#                 [[1.45, 2.8], [2.45, 5]],
#                 [[1.25, 4.75], [2.65, 6]]]
#         for pp in p0:
#             elems += Rectangle(point1=pp[0],
#                                point2=pp[1],
#                                layer=RDD.RES.LAYER)
#         # return elems
#         comp = ComposeMLayers(cell_elems=elems)
#         return SRef(comp)

#     def create_jp(self):
#         elems = ElementList()
#         plys = [[[0, -2], [3.8, 3.2]],
#                 [[1, 4.6], [2.9, 7.3]]]
#         for pp in plys:
#             elems += Rectangle(point1=pp[0],
#                                point2=pp[1],
#                                layer=RDD.JP.LAYER)
#         # return elems
#         comp = ComposeNLayer(cell_elems=elems)
#         return SRef(comp)

#     def create_rc(self):
#         elems = ElementList()
#         plys = [[[0.3, -1.6], [3.6, 3]],
#                 [[1.3, 4.8], [2.6, 6]]]
#         for pp in plys:
#             elems += Rectangle(point1=pp[0],
#                                point2=pp[1],
#                                layer=RDD.RC.LAYER)
#         # return elems
#         comp = ComposeNLayer(cell_elems=elems)
#         return SRef(comp)

#     def create_jc(self):
#         elems = ElementList()
#         plys = [[[1, 1], [2.9, 2.3]]]
#         for pp in plys:
#             elems += Rectangle(point1=pp[0],
#                                point2=pp[1],
#                                layer=RDD.JC.LAYER)
#         # return elems
#         comp = ComposeNLayer(cell_elems=elems)
#         return SRef(comp)

#     def create_jj(self):
#         elems = ElementList()
#         plys = [[[1, 0.5], [2.9, 2.3]]]
#         for pp in plys:
#             elems += Rectangle(point1=pp[0],
#                                point2=pp[1],
#                                layer=RDD.JJ.LAYER)
#         # return elems
#         comp = ComposeNLayer(cell_elems=elems)
#         return SRef(comp)

#     def create_bc(self):
#         elems = ElementList()
#         plys = [[[1.3, 6.3], [2.6, 7]]]
#         for pp in plys:
#             elems += Rectangle(point1=pp[0],
#                                point2=pp[1],
#                                layer=RDD.BC.LAYER)
#         # return elems
#         comp = ComposeNLayer(cell_elems=elems)
#         return SRef(comp)

#     def create_elementals(self, elems):

#         if self.pcell:
#             # Metal layers
#             elems += self.create_bas()
#             elems += self.create_res()
#             elems += self.create_cou()

#             # Junction layer
#             elems += self.create_jj()

#             # Protection layer
#             elems += self.create_jp()

#             # Via layers
#             elems += self.create_rc()
#             elems += self.create_jc()
#             elems += self.create_bc()
#         else:
#             rc = SRef(RDD.VIAS.RC.PCELL, origin=(0,0))
#             gc = SRef(RDD.VIAS.GC.PCELL, origin=(0,0))
#             bc = SRef(RDD.VIAS.BC.PCELL, origin=(0,0))
#             jc = SRef(RDD.VIAS.JC.PCELL, origin=(0,0))
#             cc = SRef(RDD.VIAS.CC.PCELL, origin=(0,0))

#             elems += rc
#             elems += gc
#             elems += bc
#             elems += jc
#             elems += cc

#         return elems
