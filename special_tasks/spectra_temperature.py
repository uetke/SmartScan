"""
    spectra_temperature.py
    -------------
    Acquires spectra of a particle while varying the temperature in the surrounding medium. 
    Starts by acquiring a 532nm spectra. Then acquires a series of 633nm spectra, at different
    excitation powers. 
    Loops until stopped. In between loops, the temperature has to be changed, the program refocus 
    continuously on the particle to keep track of them.
    
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
    xcenter = 42.38
    ycenter = 63.85
    zcenter = 52.65
    
    x_bkg = 40.77
    y_bkg = 65.78
    
    pcle = particle([xcenter,ycenter,zcenter],'pcle',1)
    pcle_track = particle([xcenter,ycenter,zcenter],'pcle',1)
    bkg = particle([x_bkg,y_bkg,zcenter],'bkg',1)
    
    #init the Adwin program and also loading the configuration file for the devices
    adw = adq() 
    adw.proc_num = 9
    counter = device('APD 1')
    aom = device('AOM')
    center = [xcenter,ycenter,zcenter]
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    temperature = device('Temperature')
    
    devs = [xpiezo,ypiezo,zpiezo]

    dd,ii = adw.get_timetrace_static([temperature],1,0.1)
    dd = np.array(dd)
    dd = 20*(dd-32768)/65536
    temp = float(np.mean(dd))*1000
    pcle.set_temp(temp)
    pcle_track.set_temp(temp)
    
    number_of_spectra = 10 # Number of spectra for each temperature
    number_of_accumulations = 6 # Accumulations of each spectra (for reducing noise in long-exposure images)
    
    #parameters for the refocusing on the particles
    dims = [0.7,0.7,1.5]
    accuracy = [0.1,0.1,0.1]

    # Maximum and minimum laser intensities
    
    laser_min = 85 # In uW
    laser_max = 250 # In uW
    laser_powers = np.linspace(laser_min,laser_max,number_of_spectra)
    
    focusing_power = 200 # In uW
    
    # How much time between refocusing
    time_for_refocusing = 1*60
    
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
    
    # Prepare the folder in network drive
    #savedir2 = 'R:\\monos\\Aquiles\\Data\\' + str(datetime.now().date()) + '\\'
    #if not os.path.exists(savedir2):
    #    os.makedirs(savedir2)
    #print('Data will also be saved in %s'%(savedir2+filename))
    
    
    # Check if the calibration of the AOM was done today and import the data for it.
    if os.path.exists(savedir+'aom_calibration.txt'):
        print('Importing AOM calibration...')
        AOM_voltage = np.loadtxt(savedir+'aom_calibration2.txt').astype('float')[6:]
        intensity = np.loadtxt(savedir+'aom_calibration.txt').astype('float')[6:]
        P = np.polyfit(intensity,AOM_voltage,2)
        print(P)
        plt.plot(intensity,AOM_voltage,'.')
        plt.plot(intensity,np.polyval(P,intensity))
        plt.ylabel('AOM voltage (V)')
        plt.xlabel('Laser intensity (uW)')
        plt.show(block=False)
    else:
        raise Exception('The AOM was not calibrated today, please do it before running this program...')

    
    
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
        
    data = np.zeros(9)
    # For the spectra data
    header = 'Time [s], Wavelength[nm], Type, Temp[mV], X [uM], Y [uM], Z [uM], Power [muW], Counts' 
    # For the keep track data
    header2 = 'Time [s], X [uM], Y [uM], Z [uM], Power [muW], Counts, Temp (mV)' 
    # For storing the pcle data
    header_pcle = 'Time [s], X[um], Y[um], Z[um], Temp'
    
    t_0 = time.time() # Initial time
    
    acquire_spectra = True
    keep_track = True
    data2 = np.zeros(7)
    
    first = True
    while acquire_spectra:
        if not first:
            print('First acquire 532nm data')
            input('Press enter when 532nm is on')

            dd,ii = adw.get_timetrace_static([temperature],duration=1,acc=0.2)
            dd = np.array(dd)
            dd = 20*(dd-32768)/65536
            temp = float(np.mean(dd))*1000
            true_temp = temp*.0310-2.1136 # This calibration depends on the experiment. Use with care.
            print('Starting with Temperature %s'%true_temp)
            
            pmeter.wavelength = 532
            # Refocus on the particle
            center = pcle_track.get_center()
            if flip:
                if flipper_apd != flipper.getPos():
                    flipper.goto(flipper_apd)
            position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
            time_last_refocus = time.time()
            center = position.astype('float')
            adw.go_to_position(devs,center)
            for j in range(number_of_accumulations):
                print('Triggering the spectrometer for 532nm data %s out of %s'%(j+1,number_of_accumulations))
                if flip:
                    if flipper_spec != flipper.getPos():
                        flipper.goto(flipper_spec)
                        time.sleep(0.5)
                trigger_spectrometer(adw)
                pcle.set_center(center)
                dd,ii = adw.get_timetrace_static([temperature],1,0.1)
                dd = np.array(dd)
                dd = 20*(dd-32768)/65536
                temp = float(np.mean(dd))*1000
                pcle.set_temp(temp)
                print('Refocusing...')
                center = pcle.get_center()
                if flip:
                    if flipper_apd != flipper.getPos():
                        flipper.goto(flipper_apd)
                        time.sleep(0.5)
                position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
                time_last_refocus = time.time()
                center = position.astype('float')
                adw.go_to_position(devs,center)
            try:
                power = pmeter.data*1000000
            except:
                power = 0
          
            dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
            t = time.time()-t_0
            new_data = [t,'532','spectra',temp,position[0],position[1],position[2],power,np.sum(dd)]
            
            data = np.vstack([data,new_data])
            data_pcle = np.hstack((pcle.tcenter,pcle.xcenter,pcle.ycenter,pcle.zcenter,pcle.temp))
            
            try:
                np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
                np.savetxt("%s%s" %(savedir,filename_pcle),data_pcle, fmt='%s', delimiter=",",header=header_pcle)
                #np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header)    
            except:
                print("Problem saving data")
                
            print('Time for backgrounds')
            
            # Compare drift in particle position and update background position.
            dx = pcle.xcenter[0]-pcle.xcenter[-1]
            dy = pcle.ycenter[0]-pcle.ycenter[-1]
            dz = pcle.zcenter[0]-pcle.zcenter[-1]
            
            bkg_center = [bkg.xcenter[0]-dx,bkg.ycenter[0]-dy,bkg.zcenter[0]-dz]

            adw.go_to_position(devs,bkg_center)
            for j in range(number_of_accumulations):
                print('Triggering the spectrometer for 532nm background %s out of %s'%(j+1,number_of_accumulations))
                if flip:
                    if flipper_spec != flipper.getPos():
                        flipper.goto(flipper_spec)
                        time.sleep(0.5)
                trigger_spectrometer(adw)
            try:
                power = pmeter.data*1000000
            except:
                power = 0
            dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
            t = time.time()-t_0
            new_data = [t,'532','background',temp,bkg_center[0],bkg_center[1],bkg_center[2],power,np.sum(dd)]
            data = np.vstack([data,new_data])
            data_pcle = np.hstack((pcle.tcenter,pcle.xcenter,pcle.ycenter,pcle.zcenter,pcle.temp))
            try:
                np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
                np.savetxt("%s%s" %(savedir,filename_pcle),data_pcle, fmt='%s', delimiter=",",header=header_pcle)
                #np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header) 
            except:
                print("Problem saving data")
            # Switch to 633nm
            print('Time to switch to 633nm')
            pmeter.wavelength = 633
            input('Press enter when ready')
            dd,ii = adw.get_timetrace_static([temperature],1,0.1)
            dd = np.array(dd)
            dd = 20*(dd-32768)/65536
            temp = float(np.mean(dd))*1000
            true_temp = temp*.0310-2.1136 # This calibration depends on the experiment. Use with care.
            print('The temperature now is %s degrees'%true_temp)
            
            for m in range(number_of_spectra):
                print('Refocusing on particle')
                power_aom = np.polyval(P,focusing_power)
                adw.go_to_position([aom],[power_aom])
                center = pcle.get_center()
                adw.go_to_position(devs,center)
                if flip:
                    if flipper_apd != flipper.getPos():
                        flipper.goto(flipper_apd)
                        time.sleep(0.5)
                position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
                time_last_refocus = time.time()
                center = position.astype('float')
                adw.go_to_position(devs,center)
                
                power_aom = np.polyval(P,laser_powers[m])
                adw.go_to_position([aom],[power_aom])
                
                for j in range(number_of_accumulations):
                    # Triggers the spectrometer
                    print('Triggering the spectrometer for 633nm data %s out of %s'%(j+1,number_of_accumulations))
                    if flip:
                        if flipper_spec != flipper.getPos():
                            flipper.goto(flipper_spec)
                            time.sleep(0.5)
                    trigger_spectrometer(adw)
                    pcle.set_center(center)
                    dd,ii = adw.get_timetrace_static([temperature],1,0.1)
                    dd = np.array(dd)
                    dd = 20*(dd-32768)/65536
                    temp = float(np.mean(dd))*1000
                    pcle.set_temp(temp)
                    if time.time()-time_last_refocus>time_for_refocusing:
                        print('Refocusing...')
                        if flip:
                            if flipper_apd != flipper.getPos():
                                flipper.goto(flipper_apd)
                                time.sleep(0.5)
                        position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
                        time_last_refocus = time.time()
                        center = position.astype('float')
                        adw.go_to_position(devs,center)
                try:
                    power = pmeter.data*1000000
                except:
                    power = 0
                # Take intensity    
                dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
                t = time.time()-t_0
                new_data = [t,'633','spectra',temp,position[0],position[1],position[2],power,np.sum(dd)]
                data = np.vstack([data,new_data])
                data_pcle = np.hstack((pcle.tcenter,pcle.xcenter,pcle.ycenter,pcle.zcenter,pcle.temp))
                try:
                    np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
                    np.savetxt("%s%s" %(savedir,filename_pcle),data_pcle, fmt='%s', delimiter=",",header=header_pcle)
                    #np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header)
                except:
                    print("Problem saving data")
                
            print('Time for backgrounds')
            # Compare drift in particle position and update background position.
            dx = pcle.xcenter[0]-pcle.xcenter[-1]
            dy = pcle.ycenter[0]-pcle.ycenter[-1]
            dz = pcle.zcenter[0]-pcle.zcenter[-1]
            
            bkg_center = [bkg.xcenter[0]-dx,bkg.ycenter[0]-dy,bkg.zcenter[0]-dz]
            adw.go_to_position(devs,bkg_center)
            for m in range(number_of_spectra):
                power_aom = np.polyval(P,laser_powers[m])
                adw.go_to_position([aom],[power_aom])
                for j in range(number_of_accumulations):
                    print('Triggering the spectrometer for 633nm background %s out of %s'%(j+1,number_of_accumulations))
                    if flip:
                        if flipper_spec != flipper.getPos():
                            flipper.goto(flipper_spec)
                            time.sleep(0.5)
                    trigger_spectrometer(adw)
                try:
                    power = pmeter.data*1000000
                except:
                    power = 0
                dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
                t = time.time()-t_0
                new_data = [t,'633','background',temp,position[0],position[1],position[2],power,np.sum(dd)]
                data = np.vstack([data,new_data])
                data_pcle = np.hstack((pcle.tcenter,pcle.xcenter,pcle.ycenter,pcle.zcenter,pcle.temp))
                try:
                    np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
                    np.savetxt("%s%s" %(savedir,filename_pcle),data_pcle, fmt='%s', delimiter=",",header=header_pcle)
                    #np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header) 
                except:
                    print("Problem saving data")
                    
            true_temp = temp*.0310-2.1136 # This calibration depends on the experiment. Use with care.
            print('Done with temperature %s.'%true_temp)

            
            print('Time for a final 532nm spectra to check reshaping')
            input('Enter when ready with the 532nm \n')
            
            pmeter.wavelength = 532
            # Refocus on the particle
            center = pcle.get_center()
            adw.go_to_position(devs,center)
            if flip:
                if flipper_apd != flipper.getPos():
                    flipper.goto(flipper_apd)
                    time.sleep(0.5)
            position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
            time_last_refocus = time.time()
            center = position.astype('float')
            adw.go_to_position(devs,center)
            for j in range(number_of_accumulations):
                print('Triggering the spectrometer for 532nm data %s out of %s'%(j+1,number_of_accumulations))
                if flip:
                    if flipper_spec != flipper.getPos():
                        flipper.goto(flipper_spec)
                        time.sleep(0.5)
                trigger_spectrometer(adw)
                pcle.set_center(center)
                dd,ii = adw.get_timetrace_static([temperature],1,0.1)
                dd = np.array(dd)
                dd = 20*(dd-32768)/65536
                temp = float(np.mean(dd))*1000
                pcle.set_temp(temp)
                
                if (time.time()-time_last_refocus>time_for_refocusing) and (j<number_of_accumulations-1):
                    print('Refocusing...')
                    center = pcle.get_center()
                    if flip:
                        if flipper_apd != flipper.getPos():
                            flipper.goto(flipper_apd)
                            time.sleep(0.5)
                    position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
                    time_last_refocus = time.time()
                    center = position.astype('float')
                    adw.go_to_position(devs,center)
            try:
                power = pmeter.data*1000000
            except:
                power = 0
          
            dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
            t = time.time()-t_0
            new_data = [t,'532','spectra',temp,position[0],position[1],position[2],power,np.sum(dd)]
            data = np.vstack([data,new_data])
            data_pcle = np.hstack((pcle.tcenter,pcle.xcenter,pcle.ycenter,pcle.zcenter,pcle.temp))
            try:
                np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
                np.savetxt("%s%s" %(savedir,filename_pcle),data_pcle, fmt='%s', delimiter=",",header=header_pcle)
                #np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header)    
            except:
                print("Problem saving data")
                
            print('Time for backgrounds')
            
            # Compare drift in particle position and update background position.
            dx = pcle.xcenter[0]-pcle.xcenter[-1]
            dy = pcle.ycenter[0]-pcle.ycenter[-1]
            dz = pcle.zcenter[0]-pcle.zcenter[-1]
            
            bkg_center = [bkg.xcenter[0]-dx,bkg.ycenter[0]-dy,bkg.zcenter[0]-dz]

            adw.go_to_position(devs,bkg_center)
            for j in range(number_of_accumulations):
                print('Triggering the spectrometer for 532nm background %s out of %s'%(j+1,number_of_accumulations))
                if flip:
                    if flipper_spec != flipper.getPos():
                        flipper.goto(flipper_spec)
                        time.sleep(0.5)
                trigger_spectrometer(adw)
            try:
                power = pmeter.data*1000000
            except:
                power = 0
            dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
            t = time.time()-t_0
            new_data = [t,'532','background',temp,bkg_center[0],bkg_center[1],bkg_center[2],power,np.sum(dd)]
            data = np.vstack([data,new_data])
            data_pcle = np.hstack((pcle.tcenter,pcle.xcenter,pcle.ycenter,pcle.zcenter,pcle.temp))
            try:
                np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
                np.savetxt("%s%s" %(savedir,filename_pcle),data_pcle, fmt='%s', delimiter=",",header=header_pcle)
                #np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header) 
            except:
                print("Problem saving data")
        
        if first:
            first = False
        answer = input('Do you want to take more spectra at a different temperature?[y/n]')
        
        if answer == 'n':
            keep_track = False
            acquire_spectra = False
        
        print('The program will start refocusing on the particle')
        # Let's start focusing on the particle
        i = 1
        
        power_aom = np.polyval(P,focusing_power)
        adw.go_to_position([aom],[power_aom])
        center = pcle.get_center()
        
        adw.go_to_position(devs,center)
        if flip:
            if flipper_apd != flipper.getPos():
                flipper.goto(flipper_apd)
                time.sleep(0.5)
        while keep_track:
            print('Entering iteration %s...'%i)
            i+=1
            # Take position
            position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
            center = position.astype('float')
            pcle_track.set_center(center)
            dd,ii = adw.get_timetrace_static([temperature],1,0.1)
            dd = np.array(dd)
            dd = 20*(dd-32768)/65536
            temp = float(np.mean(dd))*1000
            pcle_track.set_temp(temp)
            
            adw.go_to_position(devs,center)
            # Take power
            try:
                power = pmeter.data*1000000
            except:
                power = 0
            # Take intensity
            dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
            
            t = time.time()-t_0
            new_data = [t,position[0],position[1],position[2],power,np.sum(dd),temp]
            data2 = np.vstack([data2,new_data])
            data_pcle = np.hstack((pcle_track.tcenter,pcle_track.xcenter,pcle_track.ycenter,pcle_track.zcenter,pcle_track.temp))
            try:
                np.savetxt("%s%s" %(savedir,filename2),data2, fmt='%s', delimiter=",",header=header2)
                np.savetxt("%s%s" %(savedir,filename2_pcle),data_pcle, fmt='%s', delimiter=",",header=header_pcle)
               # np.savetxt("%s%s" %(savedir2,filename2),data2, fmt='%s', delimiter=",",header=header2)
            except:
                print("Problem saving data")
            print('Press q to exit and start acquiring spectra')
            t1 = time.time()
            while time.time()-t1 < 5:
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if ord(key) == 113: #113 is ascii for letter q
                        keep_track = False
        keep_track = True
    
    print('Program finish')
