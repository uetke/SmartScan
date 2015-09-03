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

from lib.xml2dict import device,variables

global _session 
_session = {}
_session['adw'] = adq()
_session['adw'].load('lib/adbasic/qpd.T98')

if __name__ == "__main__":   
    global _session
    _session = {}
    _session['adw'] = adq()
    _session['time'] = 1
    _session['accuracy'] = 0.05
    
    qpdx = device('QPD x')
    qpdy = device('QPD y')
    qpdz = device('QPD z')
    diffx = device('Diff +')
    diffy = device('Diff -')
    monitor = device('Monitor')
    
    devices = [qpdx,qpdy,qpdz,diffx,diffy,monitor]
    _session['devices'] = devices
    
    app = QtGui.QApplication(sys.argv)
    test = MainWindow() 
    test.show()
    app.exec_()