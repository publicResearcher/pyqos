#!/usr/bin/python

from config import INTERFACES
from rules.qos_formulas import burst_formula
from built_in_classes import RootHTBClass
from .clients import Main as Clients
from .servers import Main as Servers


def apply_qos():
    gre_home = INTERFACES["gre-home"]
    root_class = RootHTBClass(
        interface=gre_home["name"],
        rate=gre_home["speed"],
        burst=burst_formula(gre_home["speed"]),
        qdisc_prefix_id="1:",
        default=1500
    )
    root_class.add_child(Clients())
    root_class.add_child(Servers())

    root_class.apply_qos()
