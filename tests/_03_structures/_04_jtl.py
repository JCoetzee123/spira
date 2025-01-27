import spira.all as spira

from tests._03_structures._02_jj import Junction
from spira.yevon.process import get_rule_deck


RDD = get_rule_deck()


class Jtl(spira.Circuit):
    """  """

    def get_transforms(self):
        t1 = spira.Translation(translation=(0, 0))
        t2 = spira.Translation(translation=(150, 0))
        return [t1, t2]

    def create_routes(self, elems):
        elems += spira.Rectangle(p1=(4, -4), p2=(146, 4), layer=RDD.PLAYER.M2.METAL)
        elems += spira.Rectangle(p1=(-3, -4), p2=(-30, 4), layer=RDD.PLAYER.M2.METAL)
        return elems

    def create_elementals(self, elems):
        t1, t2 = self.get_transforms()
        jj = Junction()
        elems += spira.SRef(alias='S1', reference=jj, transformation=t1)
        return elems


# ----------------------------------------------------------------------------------------


if __name__ == '__main__':

    D = Jtl(pcell=True)

    from spira.yevon.vmodel.virtual import virtual_connect
    v_model = virtual_connect(device=D.expand_flatcopy())
    v_model.gdsii_output_virtual_connect()

    # D.gdsii_output()
    D.netlist_output()

