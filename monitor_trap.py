#!/usr/bin/env python
#-*- coding: utf-8 -*-
''' Starting point for the monitoring of the trap. 
    This program is thought for taking advantage of the QPD and the Balanced Photo-Detector
    In order to characterize the behavior of the trap at different contidions. 
'''

import sys
from pyqtgraph.Qt import QtGui

from GUI.TrapWindow import MainWindow
from lib.xml2dict import device

import _session

if __name__ == "__main__":   
    _session.time = 1.5
    _session.accuracy = 0.05
    _session.apdtime = 1.5
    _session.apdacc = 50E-6
    
    _session.device['qpdx'] = device('QPD X')
    _session.device['qpdy'] = device('QPD Y')
    _session.device['qpdz'] = device('QPD Z')
    _session.device['diffx'] = device('Monitor +')
    _session.device['diffy'] = device('Monitor -')
    _session.device['monitor'] = device('Diff')
    _session.device['apd1'] = device('APD 1')  
    
    
    if _session.adw.adw.Test_Version() != 1: # Not clear if this means the ADwin is booted or not
        _session.adw.boot()
        _session.adw.init_port7()
        print('Booting the ADwin...')
            
        
    _session.adw.load('lib/adbasic/init_adwin.T98')
    _session.adw.start(8)
    _session.adw.wait(8)
    _session.adw.load('lib/adbasic/monitor.T90')
    _session.adw.load('lib/adbasic/adwin.T99')
   
    devices = []
    for i in _session.device:
        devices.append(_session.device[i])

    _session.devices = devices
    app = QtGui.QApplication(sys.argv)
    test = MainWindow()
    test.show()
    app.exec_()