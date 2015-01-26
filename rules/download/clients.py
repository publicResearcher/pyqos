#!/usr/bin/python
# Author: Anthony Ruhier
# QoS for upload

import tools
from config import LAN_IF, DOWNLOAD, UPLOAD
from rules.qos_formulas import burst_formula, cburst_formula

MAX_DOWNLOAD = DOWNLOAD


def interactive_class():
    """
    Interactive Class, for low latency, high priority packets such as VOIP and
    DNS.

    Low priority, pass before everything else. Uses htb then pfifo.
    """
    parent = "1:11"
    classid = "1:110"
    prio = 10
    mark = 110
    rate = MAX_DOWNLOAD * 10/100
    ceil = MAX_DOWNLOAD * 90/100
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)

    tools.class_add(LAN_IF, parent, classid, rate=rate, ceil=ceil,
                    burst=burst, cburst=cburst, prio=prio)
    tools.qdisc_add(LAN_IF, parent=classid,
                    handle=tools.get_child_qdiscid(classid),
                    algorithm="pfifo")
    tools.filter_add(LAN_IF, parent="1:0", prio=prio, handle=mark,
                     flowid=classid)


def tcp_ack_class():
    """
    Class for TCP ACK.

    It's important to receive quickly the TCP ACK when uploading. Uses htb then
    sfq.
    """
    parent = "1:11"
    classid = "1:120"
    prio = 20
    mark = 120
    rate = UPLOAD / 10
    ceil = MAX_DOWNLOAD / 10
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)

    tools.class_add(LAN_IF, parent, classid, rate=rate, ceil=ceil,
                    burst=burst, cburst=cburst, prio=prio)
    tools.qdisc_add(LAN_IF, parent=classid,
                    handle=tools.get_child_qdiscid(classid),
                    algorithm="sfq", perturb=10)
    tools.filter_add(LAN_IF, parent="1:0", prio=prio, handle=mark,
                     flowid=classid)


def ssh_class():
    """
    Class for SSH connections.

    We want the ssh connections to be smooth !
    SFQ will mix the packets if there are several SSH connections in parallel
    and ensure that none has the priority
    """
    parent = "1:11"
    classid = "1:1100"
    prio = 30
    mark = 1100
    rate = 400
    ceil = MAX_DOWNLOAD
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)

    tools.class_add(LAN_IF, parent, classid, rate=rate, ceil=ceil,
                    burst=burst, cburst=cburst, prio=prio)
    tools.qdisc_add(LAN_IF, parent=classid,
                    handle=tools.get_child_qdiscid(classid),
                    algorithm="sfq", perturb=10)
    tools.filter_add(LAN_IF, parent="1:0", prio=prio, handle=mark,
                     flowid=classid)


def http_class():
    """
    Class for HTTP/HTTPS connections.
    """
    parent = "1:11"
    classid = "1:1200"
    prio = 40
    mark = 1200
    rate = MAX_DOWNLOAD * 10/100
    ceil = MAX_DOWNLOAD
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)

    tools.class_add(LAN_IF, parent, classid, rate=rate, ceil=ceil,
                    burst=burst, cburst=cburst, prio=prio)
    tools.qdisc_add(LAN_IF, parent=classid,
                    handle=tools.get_child_qdiscid(classid),
                    algorithm="sfq", perturb=10)
    tools.filter_add(LAN_IF, parent="1:0", prio=prio, handle=mark,
                     flowid=classid)


def default_class():
    """
    Default class
    """
    parent = "1:11"
    classid = "1:1500"
    prio = 100
    mark = 1500
    rate = MAX_DOWNLOAD * 20/100
    ceil = MAX_DOWNLOAD
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)

    tools.class_add(LAN_IF, parent, classid, rate=rate, ceil=ceil,
                    burst=burst, cburst=cburst, prio=prio)
    tools.qdisc_add(LAN_IF, parent=classid,
                    handle=tools.get_child_qdiscid(classid),
                    algorithm="sfq", perturb=10)
    tools.filter_add(LAN_IF, parent="1:0", prio=prio, handle=mark,
                     flowid=classid)


def apply_qos():
    """
    Apply the QoS for the OUTPUT
    """
    # Creating the client branch (htb)
    rate = DOWNLOAD * 30/100
    ceil = MAX_DOWNLOAD
    burst = burst_formula(rate) * 3
    cburst = cburst_formula(rate, burst)
    tools.class_add(LAN_IF, parent="1:1", classid="1:11",
                    rate=rate, ceil=ceil,
                    burst=burst, cburst=cburst, prio=0)

    interactive_class()
    tcp_ack_class()
    ssh_class()
    http_class()
    default_class()