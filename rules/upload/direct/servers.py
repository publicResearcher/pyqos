#!/usr/bin/python
# Author: Anthony Ruhier
# QoS for upload

from config import INTERFACES
from rules.qos_formulas import burst_formula, cburst_formula
from built_in_classes import FQCodelClass, PFIFOClass

UPLOAD = INTERFACES["public_if"]["speed"]
MIN_UPLOAD = 200


class GRE_online(PFIFOClass):
    """
    Class for gre_tunnel

    As almost all traffic is going through the tunnel, very high priority.
    Uses htb then fq-codel
    """
    parent = "1:1"
    classid = "1:100"
    prio = 20
    mark = 100
    rate = UPLOAD - MIN_UPLOAD
    ceil = UPLOAD
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)
    limit = cburst
    interval = 15


class Default(FQCodelClass):
    """
    Class for gre_tunnel

    As almost all traffic is going through the tunnel, very high priority.
    Uses htb then fq-codel
    """
    classid = "1:500"
    prio = 50
    mark = 500
    rate = UPLOAD
    burst = burst_formula(rate)
    limit = burst
    interval = 15


class Torrents(FQCodelClass):
    """
    Class for torrents

    Very low priority. Uses htb then fq-codel
    """
    classid = "1:600"
    prio = 100
    mark = 600
    rate = MIN_UPLOAD
    ceil = UPLOAD
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)
    limit = cburst
    interval = 15
