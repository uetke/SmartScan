"""
    continuous_spectra.py
    -------------
    Acquires spectra of a particle continuously after refocusing. 
    The idea is to use it while changing the temperature of the medium.
    
    AUTHOR: Aquiles Carattino
    EMAIL: carattino@physics.leidenuniv.nl

"""

from __future__ import division
import numpy as np
import time
import msvcrt
import sys
import os
import matplotlib.pyplot as plt
from datetime import datetime
from spectrometer import abort, trigger_spectrometer
import copy
from experiment import particle
from devices.flipper import Flipper

cwd = os.getcwd()
cwd = cwd.split('\\')
path = ''
# One level up from this folder
for i in range(len(cwd)-1):
    path+=cwd[i]+'\\'

if path not in sys.path:
    sys.path.insert(0, path)

    
from lib.adq_mod import adq
from lib.xml2dict import device,variables
from devices.powermeter1830c import PowerMeter1830c as pp


        
if __name__ == '__main__': 
    # Coordinates of the particle
    xcenter = 39.25
    ycenter = 55.59
    zcenter = 47.80

    x_bkg = 30.97
    y_bkg = 45.17
    
    pcle = particle([xcenter,ycenter,zcenter],'pcle',1)
    pcle_track = particle([xcenter,ycenter,zcenter],'pcle',1)
    bkg = particle([x_bkg,y_bkg,zcenter],'bkg',1)
    
    #init the Adwin program and also loading the configuration file for the devices
    adw = adq() 
    adw.proc_num = 9
    counter = device('APD 1')
    center = [xcenter,ycenter,zcenter]
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    temperature = device('Temperature')
    
    devs = [xpiezo,ypiezo,zpiezo]

    dd,ii = adw.get_timetrace_static([temperature],0.5,0.1)
    dd = np.array(dd)
    dd = 20*(dd-32768)/65536
    temp = float(np.mean(dd))*1000
    pcle.set_temp(temp)
    pcle_track.set_temp(temp)
    
    number_of_accumulations = 1 # Accumulations of each spectra (for reducing noise in long-exposure images)
    
    #parameters for the refocusing on the particles
    dims = [1,1,2]
    accuracy = [0.2,0.2,0.4] 
       
    #Parameters for keeping track of the particle
    #dims_t = [0.4,0.4,0.8]
    #accuracy_t = [0.05,0.05,0.1]
    
    # Name that the files will have
    name = 'spectra_temperature' 
    name2 = 'spectra_temperature_keep_track'
    # Directory for saving the files
    savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    
    # Not overwrite
    i=1
    filename = '%s_%s.dat'%(name,i)
    while os.path.exists(savedir+filename):
        i += 1
        filename = '%s_%s.dat' %(name,i)
    filename_pcle = '%s_%s_pcle.dat' %(name,i)
    
    filename2 = '%s_%s.dat' %(name2,i)
    filename2_pcle = '%s_%s_pcle.dat' %(name2,i)
    print('Data will be saved in %s'%(savedir+filename)) 
    
    #Newport Power Meter
    pmeter = pp.via_serial(16)
    pmeter.initialize()
    pmeter.wavelength = 532
    pmeter.attenuator = True
    pmeter.filter = 'Medium' 
    pmeter.go = True
    pmeter.units = 'Watts' 
    
    # Initialize the motorized flipper mirror
    try:
        flipper = Flipper(b'37863355')
        flipper_apd = 1 # Position going to the APD
        flipper_spec = 2 # Position going to the spectrometer
        flip = True
    except:
        print('Problem initializing the flipper mirror')
        flip = False
        
    data = np.zeros(7)
    # For the spectra data
    header = 'Time [s], Wavelength[nm], Type, Temp[mV], X [uM], Y [uM], Z [uM], Power [muW], Counts' 
    # For the keep track data
    header2 = 'Time [s], X [uM], Y [uM], Z [uM], Power [muW], Counts, Temp (mV)' 
    # For storing the pcle data
    header_pcle = 'Time [s], X[um], Y[um], Z[um], Temp'
    
    t_0 = time.time() # Initial time
    
    acquire_spectra = True
    keep_track = True

    iteration = 1
    while acquire_spectra:
        print('Entering iteration %s'%iteration)
        iteration +=1
        dd,ii = adw.get_timetrace_static([temperature],duration=0.5,acc=0.1)
        dd = np.array(dd)
        dd = 20*(dd-32768)/65536
        temp = float(np.mean(dd))*1000
        true_temp = temp*.0310-2.1136 # This calibration depends on the experiment. Use with care.
        print('Starting with Temperature %s'%true_temp)
        
        # Refocus on the particle
        center = pcle.get_center()
        if flip:
            if flipper_apd != flipper.getPos():
                flipper.goto(flipper_apd)
        print('Refocusing...')
        position = adw.focus_full(counter,devs,center,dims,accuracy,rate=2).astype('str')
        time_last_refocus = time.time()
        center = position.astype('float')
        pcle.set_center(center)
        adw.go_to_position(devs,center)

        print('Triggering the spectrometer')
        if flip:
            if flipper_spec != flipper.getPos():
                flipper.goto(flipper_spec)
                time.sleep(0.5)
        trigger_spectrometer(adw)    
        t = time.time()-t_0
        new_data = [t,'WL','spectra',temp,position[0],position[1],position[2]]
        
        data = np.vstack([data,new_data])
        data_pcle = np.hstack((pcle.tcenter,pcle.xcenter,pcle.ycenter,pcle.zcenter,pcle.temp))
        
        try:
            np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
            np.savetxt("%s%s" %(savedir,filename_pcle),data_pcle, fmt='%s', delimiter=",",header=header_pcle)
        except:
            print("Problem saving data")
            
        
        # Compare drift in particle position and update background position.
        dx = pcle.xcenter[0]-pcle.xcenter[-1]
        dy = pcle.ycenter[0]-pcle.ycenter[-1]
        dz = pcle.zcenter[0]-pcle.zcenter[-1]
        
        bkg_center = [bkg.xcenter[0]-dx,bkg.ycenter[0]-dy,bkg.zcenter[0]-dz]

        adw.go_to_position(devs,bkg_center)
        print('Background')
        if flip:
            if flipper_spec != flipper.getPos():
                flipper.goto(flipper_spec)
                time.sleep(0.5)
                
        trigger_spectrometer(adw)
        t = time.time()-t_0
        new_data = [t,'WL','background',temp,bkg_center[0],bkg_center[1],bkg_center[2]]
        data = np.vstack([data,new_data])
        data_pcle = np.hstack((pcle.tcenter,pcle.xcenter,pcle.ycenter,pcle.zcenter,pcle.temp))
        try:
            np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
            np.savetxt("%s%s" %(savedir,filename_pcle),data_pcle, fmt='%s', delimiter=",",header=header_pcle)
            #np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header) 
        except:
            print("Problem saving data")
                
        print('Done with temperature %s.'%true_temp)
        print('\n\n')
        print('Press q to exit the program')
        print('-------------------------------------------')
        t1 = time.time()
        while time.time()-t1 < 0.5:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if ord(key) == 113: #113 is ascii for letter q
                    acquire_spectra = False
        
    
    print('Program finish')
