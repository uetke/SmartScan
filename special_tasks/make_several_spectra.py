# -*- coding: utf-8 -*-
"""
    make_several_spectra.py
    -------------

    Acquires spectra of the defined coordinates after refocusing on them. 
    It is wise to run intermediate_scan_mod before running this script.
    
    AUTHOR: Aquiles Carattino
    EMAIL: carattino@physics.leidenuniv.nl
"""

from __future__ import division
import numpy as np
import time
import matplotlib.pyplot as plt
from lib.adq_mod import *
from lib.xml2dict import device,variables
from datetime import datetime
import msvcrt
import sys
import os
from lib.logger import get_all_caller,logger
from devices.powermeter1830c import PowerMeter1830c as pp
from start import adding_to_path
from special_tasks.spectrometer import abort, trigger_spectrometer
from devices.flipper import Flipper

logger=logger(filelevel=30)
        
if __name__ == '__main__': 

    #init the Adwin programm and also loading the configuration file for the devices
    adw = adq() 
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    counter = device('APD 1')   
    
    #Newport Power Meter
    pmeter = pp.via_serial(16)
    pmeter.initialize()
    pmeter.wavelength = 532
    pmeter.attenuator = True
    pmeter.filter = 'Medium'
    pmeter.go = True
    pmeter.units = 'Watts'
    
    print('The file to read will be name+.txt. Please verify that it exists\n')
    name = input('Give the name of the File to process without extension: ')
    cwd = os.getcwd()
    savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    filename = name    
    i=1
    while os.path.exists(savedir+filename+"_532.txt"):
        filename = '%s_%s' %(name,i)
        i += 1
    logger.info('%s\\%s.log' %(savedir,filename))
    print('Data will be saved in %s_532.txt'%(savedir+filename))
    
    xcenter = 50.0 #In um
    ycenter = 50.0
    zcenter = 49.15
    xdim = 30    #In um
    ydim = 30
    xacc = 0.15   #In um
    yacc = 0.15
    devs = [xpiezo,ypiezo,zpiezo]
    #parameters for the refocusing on the particles
    dims = [0.3,0.3,0.3]
    accuracy = [0.05,0.05,0.1]
    
    adw.go_to_position(devs[:3],[xcenter,ycenter,zcenter])
    header = "type,x-pos,y-pos,z-pos,laser power..."
    
    # Initialize the motorized flipper mirror
    try:
        flipper = Flipper(b'37863355')
        flipper_apd = 1 # Position going to the APD
        flipper_spec = 2 # Position going to the spectrometer
        flip = True
    except:
        print('Problem initializing the flipper mirror')
        flip = False

    data = np.loadtxt('%s%s.txt' %(savedir, name),dtype='bytes',delimiter =',').astype('str')#strange b in front of strings 

    pressing = input('Set the spectrometer and filters and press enter when ready')
    
    print('Data will be saved in %s_532.txt'%(savedir+filename))
    num_particles = sum(data[:,0]=='particle')
    num_background = sum(data[:,0]=='background')    
    
    for i in range(num_particles):
        if flip:
            if flipper_apd != flipper.getPos():
                flipper.goto(flipper_apd)
                
        center = data[i,1:4].astype('float')
        center[2] = zcenter
        adw.go_to_position(devs,center)
        data[i,1:4] = adw.focus_full(counter,devs,center,dims,accuracy,rate=1,speed=50)
        time.sleep(0.5) 
        if flip:
            if flipper_spec != flipper.getPos():
                flipper.goto(flipper_spec)
                
        trigger_spectrometer(adw)
        print('Done with particle %i of %i'%(i+1,num_particles))
        
        np.savetxt("%s%s_532.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    print('532nm particle spectra taken')
    
    #make a spectra of the selected background
    for i in range(num_background):
        if flip:
            if flipper_spec != flipper.getPos():
                flipper.goto(flipper_spec)
        center = np.append(data[i-num_background,1:3].astype('float'),np.mean(data[:num_particles,3].astype('float')))
        adw.go_to_position(devs,center)
        trigger_spectrometer(adw)
        print('Done with background %i of %i'%(i+1,num_background))
        np.savetxt("%s%s_532.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    
    np.savetxt("%s%s_532.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)   
    print('Program finished')
