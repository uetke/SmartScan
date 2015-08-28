"""
    spectra_temperature.py
    -------------
    Acquires spectra of a particle while varying the temperature in the surrounding medium. 
    Starts by acquiring a 532nm spectra. Then acquires a series of 633nm spectra, at different
    excitation powers. 
    Loops until stopped. En between loops, the temperature has to be changed, the program refocus 
    continuously on the particle to keep track of it.
    
    AUTHOR: Aquiles Carattino
    EMAIL: carattino@physics.leidenuniv.nl

"""

from __future__ import division
import numpy as np
import time
import msvcrt
import sys
import os
from datetime import datetime
from spectrometer import abort, trigger_spectrometer
import copy

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
from devices.powermeter1830c import powermeter1830c as pp


        
if __name__ == '__main__': 
    # Coordinates of the particle
    xcenter = 34.13
    ycenter = 62.43
    zcenter = 53.10
    
    number_of_spectra = 10 # Number of spectra for each temperature
    number_of_accumulations = 10 # Accumulations of each spectra (for reducing noise in long-exposure images)
    
    #parameters for the refocusing on the particles
    dims = [1,1,1.5]
    accuracy = [0.1,0.1,0.1]

    focusing_aom = 1.25
    
    # How much time between refocusing
    time_for_refocusing = 5*60
    
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
    filename2 = '%s_%s.dat' %(name2,i)
    print('Data will be saved in %s'%(savedir+filename))
    
    # Prepare the folder in network drive
    savedir2 = 'R:\\monos\\Aquiles\\Data\\' + str(datetime.now().date()) + '\\'
    if not os.path.exists(savedir2):
        os.makedirs(savedir2)
    print('Data will also be saved in %s'%(savedir2+filename))
    #init the Adwin program and also loading the configuration file for the devices
    adw = adq() 
    adw.proc_num = 9
    counter = device('APD 1')
    aom = device('AOM')
    center = [xcenter,ycenter,zcenter]
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    devs = [xpiezo,ypiezo,zpiezo]
    
    #Newport Power Meter
    pmeter = pp(0)
    pmeter.initialize()
    pmeter.wavelength = 532
    pmeter.attenuator = True
    pmeter.filter = 'Medium' 
    pmeter.go = True
    pmeter.units = 'Watts' 
    
    data = np.zeros(9)
    # For the spectra data
    header = 'Time [s], Wavelength[nm], Type, Temp[Ohms], X [uM], Y [uM], Z [uM], Power [muW], Counts' 
    # For the keep track data
    header2 = 'Time [s], X [uM], Y [uM], Z [uM], Power [muW], Counts' 
    temperature = 1
    t_0 = time.time() # Initial time
    
    acquire_spectra = True
    keep_track = True
    
    while acquire_spectra:
        print('First acquire 532nm data')
        input('Press enter when 532nm is on')
        temp = input('Enter the value of the multimeter: ')
        temp = float(temp)
        true_temp = (temp-100)/.385
        print('Starting with Temperature %s'%true_temp)
        
        pmeter.wavelength = 532
        # Refocus on the particle
        position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
        time_last_refocus = time.time()
        center = position.astype('float')
        adw.go_to_position(devs,center)
        for j in range(number_of_accumulations):
            print('Triggering the spectrometer for 532nm data %s out of %s'%(j+1,number_of_accumulations))
            trigger_spectrometer(adw)
            if (time.time()-time_last_refocus>time_for_refocusing) and (j<number_of_accumulations-1):
                print('Refocusing...')
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
        try:
            np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
            np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header)    
        except:
            print("Problem saving data")
            
        print('Time for backgrounds')
        bkg_center = copy.copy(center)
        bkg_center[0] += 1 # 1 micrometer to the right of the particle.
        adw.go_to_position(devs,bkg_center)
        for j in range(number_of_accumulations):
            print('Triggering the spectrometer for 532nm background %s out of %s'%(j+1,number_of_accumulations))
            trigger_spectrometer(adw)
        try:
            power = pmeter.data*1000000
        except:
            power = 0
        dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
        t = time.time()-t_0
        new_data = [t,'532','background',temp,bkg_center[0],bkg_center[1],bkg_center[2],power,np.sum(dd)]
        data = np.vstack([data,new_data])
        try:
            np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
            np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header) 
        except:
            print("Problem saving data")
        # Switch to 633nm
        print('Time to switch to 633nm')
        pmeter.wavelength = 633
        input('Press enter when ready')
        temp = input('Enter the value of the multimeter')
        temp = float(temp)
        true_temp = (temp-100)/.385
        print('The temperature now is %s degrees'%true_temp)
        
        for m in range(number_of_spectra):
            print('Refocusing on particle')
            power_aom = focusing_aom
            adw.go_to_position([aom],[power_aom])
            adw.go_to_position(devs,center)
            position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
            time_last_refocus = time.time()
            center = position.astype('float')
            adw.go_to_position(devs,center)
            
            power_aom = 1.5-m*1./number_of_spectra
            adw.go_to_position([aom],[power_aom])
            
            for j in range(number_of_accumulations):
                # Triggers the spectrometer
                print('Triggering the spectrometer for 633nm data %s out of %s'%(j+1,number_of_accumulations))
                trigger_spectrometer(adw)

                if time.time()-time_last_refocus>time_for_refocusing:
                    print('Refocusing...')
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
            try:
                np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
                np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header)
            except:
                print("Problem saving data")
            
        print('Time for backgrounds')
        bkg_center = copy.copy(center)
        bkg_center[0] += 1 # 1 micrometer to the right of the particle.
        adw.go_to_position(devs,bkg_center)
        
        for m in range(number_of_spectra):
            power_aom = 1.5-m*1./number_of_spectra
            adw.go_to_position([aom],[power_aom])
            for j in range(number_of_accumulations):
                print('Triggering the spectrometer for 633nm background %s out of %s'%(j+1,number_of_accumulations))
                trigger_spectrometer(adw)
            try:
                power = pmeter.data*1000000
            except:
                power = 0
            dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
            t = time.time()-t_0
            new_data = [t,'633','background',temp,position[0],position[1],position[2],power,np.sum(dd)]
            data = np.vstack([data,new_data])
            try:
                np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
                np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header) 
            except:
                print("Problem saving data")
        
        print('Done with temperature %s.'%true_temp)
        temp = input('Enter the value of the multimeter')
        temp = float(temp)
        final_temp = (temp-100)/.385
        print('The final temperature is %s and the initial temperature was %s'%(final_temp,true_temp))
        
        print('Time for a final 532nm spectra to check reshaping')
        input('Enter when ready with the 532nm \n')
        
        pmeter.wavelength = 532
        # Refocus on the particle
        adw.go_to_position(devs,center)
        position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
        time_last_refocus = time.time()
        center = position.astype('float')
        adw.go_to_position(devs,center)

        for j in range(number_of_accumulations):
            print('Triggering the spectrometer for 532nm data %s out of %s'%(j+1,number_of_accumulations))
            trigger_spectrometer(adw)
            if (time.time()-time_last_refocus>time_for_refocusing) and (j<number_of_accumulations-1):
                print('Refocusing...')
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
        try:
            np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
            np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header)    
        except:
            print("Problem saving data")
        
        answer = input('Do you want to take more spectra at a different temperature?[y/n]')
        
        if answer == 'n':
            keep_track = False
            acquire_spectra = False
        
        print('The programm will start refocusing on the particle')
        # Let's start focusing on the particle
        i = 1
        data2 = np.zeros(6)
        power_aom = focusing_aom
        adw.go_to_position([aom],[power_aom])
        adw.go_to_position(devs,center)
        while keep_track:
            print('Entering iteration %s...'%i)
            i+=1
            # Take position
            position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
            center = position.astype('float')
            adw.go_to_position(devs,center)
            # Take power
            try:
                power = pmeter.data*1000000
            except:
                power = 0
            # Take intensity
            dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
            
            t = time.time()-t_0
            new_data = [t,position[0],position[1],position[2],power,np.sum(dd)]
            data2 = np.vstack([data2,new_data])
            try:
                np.savetxt("%s%s" %(savedir,filename2),data2, fmt='%s', delimiter=",",header=header2)
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
