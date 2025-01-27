import spira.all as spira

from tests._03_structures._02_jj import Junction
from spira.yevon.process import get_rule_deck


RDD = get_rule_deck()


class JtlBias(spira.Circuit):

    def get_transforms(self):
        t1 = spira.Translation(translation=(0, 0))
        t2 = spira.Translation(translation=(150, 0))
        return [t1, t2]

    def create_routes(self, elems):
        elems += spira.Rectangle(p1=(4, -4), p2=(146, 4), layer=RDD.PLAYER.M2.METAL)
        elems += spira.Rectangle(p1=(-3, -4), p2=(-30, 4), layer=RDD.PLAYER.M2.METAL)
        elems += spira.Rectangle(p1=(153, -4), p2=(180, 4), layer=RDD.PLAYER.M2.METAL)
        elems += spira.Rectangle(p1=(60, 0), p2=(80, 50), layer=RDD.PLAYER.M2.METAL)
        return elems

    def create_elementals(self, elems):
        t1, t2 = self.get_transforms()

        jj = Junction()

        elems += spira.SRef(alias='S1', reference=jj, transformation=t1)
        elems += spira.SRef(alias='S2', reference=jj, transformation=t2)

        return elems


# ------------------------------------------------------------------------------------


if __name__ == '__main__':

    D = JtlBias(pcell=True)

    D.gdsii_output()
    D.netlist_output()



