#!/usr/bin/env python
#-*- coding: utf-8 -*-
''' Starting point for the monitoring of the trap. 
    This program is thought for taking advantage of the QPD and the Balanced Photo-Detector
    In order to characterize the behavior of the trap at different contidions. 
'''

import sys
from pyqtgraph.Qt import QtGui

from GUI.TrapWindow import MainWindow
from lib.adq_mod import adq
from lib.xml2dict import device
import session


if __name__ == "__main__":     
    adw = adq()
    # Loads the monitor into the adwin
    adw.load('lib/adbasic/monitor.T90')
    # Loads the needed libraries for the trap
    adw.load('lib/adbasic/qpd.T98')
    session._session['adw'] = adw
    session._session['time'] = 1
    session._session['accuracy'] = 0.05
    monitor1 = device('Monitor +')
    monitor2 = device('Monitor -')
    diff = device('Diff')
    QPDX = device('QPD X')
    QPDY = device('QPD Y')
    QPDZ = device('QPD Z')
    devices = [monitor1, monitor2, diff, QPDX, QPDY, QPDZ]
    session._session['devices'] = devices
    app = QtGui.QApplication(sys.argv)
    test = MainWindow()
    test.show()
    app.exec_()