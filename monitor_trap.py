#!/usr/bin/env python
#-*- coding: utf-8 -*-
''' Starting point for the monitoring of the trap.
    This program is thought for taking advantage of the QPD and the Balanced Photo-Detector
    In order to characterize the behavior of the trap at different conditions.
'''

import sys
from pyqtgraph.Qt import QtGui

from GUI.Trap.Monitor import Monitor
from lib.xml2dict import device

import _session

if __name__ == "__main__":
    _session.time = 1.5
    _session.accuracy = 0.05
    _session.apdtime = 1.5
    _session.apdacc = 50E-6
    _session.monitor_timeresol = 100 # In ms

    _session.device['qpdx'] = device('QPD X')
    _session.device['qpdy'] = device('QPD Y')
    _session.device['qpdz'] = device('QPD Z')
    _session.device['diffx'] = device('Monitor +')
    _session.device['diffy'] = device('Monitor -')
    _session.device['monitor'] = device('Diff')
    _session.device['apd1'] = device('APD 1')
    _session.device['lock'] = device('Lock-in')
    _session.device['xpiezo'] = device('x piezo')
    _session.device['ypiezo'] = device('y piezo')
    _session.device['zpiezo'] = device('z piezo')
    
    devices = []
    for i in _session.device:
        devices.append(_session.device[i])

    _session.devices = devices
    app = QtGui.QApplication(sys.argv)
    signMonitor = Monitor()
    signMonitor.show()
    app.exec_()