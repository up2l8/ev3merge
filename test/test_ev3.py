
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import os
import ev3
from lxml import etree

DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')

def test_ev3():
    ev3a = ev3.Ev3(os.path.join(DATA_DIR, 'XY_Initialize.ev3'))
    ev3b = ev3.Ev3(os.path.join(DATA_DIR, 'XY_Initialize.ev3'))
    ev3a.merge(ev3b)

    ev3a.write(open('asdf.ev3', 'wb'))

if __name__ == '__main__':
    test_ev3()
