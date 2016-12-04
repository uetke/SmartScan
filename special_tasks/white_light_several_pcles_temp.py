# -*- coding: utf-8 -*-
"""
    Acquires spectra of the defined coordinates after refocusing on them. 
    After the loop it keeps refocusing in a reference particle until stopped for a new measurement.
    
    It is wise to run intermediate_scan_mod before running this script.
"""

from __future__ import division
import numpy as np
import time
import matplotlib.pyplot as plt
from lib.adq_mod import *
from lib.xml2dict import device,variables
from datetime import datetime
from experiment import particle
import msvcrt
import sys
import os
from devices.flipper import Flipper
from start import adding_to_path
from spectrometer import abort, trigger_spectrometer

adding_to_path('lib')


cwd = os.getcwd()
savedir = cwd + '\\' + str(datetime.now().date()) + '\\'
#names of the parameters
par=variables('Par')
fpar=variables('FPar')
data=variables('Data')
fifo=variables('Fifo')



def abort(filename):
    header = "type,x-pos,y-pos,z-pos,first scan time" + ",time_%s"*(len(data[0,:])-5) %tuple(range((len(data[0,:])-5)))
    np.savetxt("%s%s_abort.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    sys.exit(0)
        
if __name__ == '__main__': 

    #init the Adwin programm and also loading the configuration file for the devices
    adw = adq() 
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    counter = device('APD 1')   
    temperature = device('Temperature')
   
    #print('The file to read will be name+_data.txt. Please verify that it exists\n')
    datafile = 'S160908_better_WhiteLight'
    cwd = os.getcwd()
    savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    name = 'Temp_Dependence_'  
    filename = name  
    i=1
    while os.path.exists(savedir+filename+".txt"):
        filename = '%s_%s' %(name,i)
        i += 1
    
    filename2 = filename + '_tracking.txt'
    filename+=".txt"
    print('Data will be saved in %s'%(savedir+filename))

    devs = [xpiezo,ypiezo,zpiezo]
    #parameters for the refocusing on the particles
    dims = [1,1,1]
    accuracy = [0.05,0.05,0.1]

    header = "Time,WL,type,pcle,temp,x-pos,y-pos,z-pos"
    header2 = "Time,x-pos,y-pos,z-pos,temp"
    try:
        flipper = Flipper(b'37863355')
        flipper_apd = 1 # Position going to the APD
        flipper_spec = 2 # Position going to the spectrometer
        flip = True
    except:
        print('Problem initializing the flipper mirror')
        flip = False
        

    data = np.loadtxt('%s%s.txt' %(savedir, datafile),dtype='bytes',delimiter =',').astype('str')
    
    num_particles = sum(data[:,0]=='particle')
    num_background = sum(data[:,0]=='background')  
    
    particles = []
    for i in range(num_particles):
        center = data[i,1:4].astype('float')
        particles.append(particle(center,'pcle',i+1))
    
    pcle_track = particles[-1]
    
    backgrounds = []
    for i in range(num_background):
        center = np.append(data[i-num_background,1:3].astype('float'),np.mean(data[:num_particles,3].astype('float')))
        backgrounds.append(particle(center,'bkg',i+1))
    
    data = np.zeros(8)
    data2 = np.zeros(5)
    acquire_spectra = True 
    keep_track = True
    print('Now is time to acquire White Light Spectra\n')
    pressing = input('Please set up the spectrometer and press enter when ready')
    
    while acquire_spectra:
        answer = input('Do you want to take more spectra at a different temperature?[y/n]')
        if answer == 'n':
            keep_track = False
            acquire_spectra = False
            break
        for i in range(num_particles):
            dd,ii = adw.get_timetrace_static([temperature],duration=1,acc=0.2)
            dd = np.array(dd)
            dd = 20*(dd-32768)/65536
            temp = float(np.mean(dd))*1000
            true_temp = temp*.0310-2.1136 # This calibration depends on the experiment. Use with care.
            
            print('Starting with Temperature %s'%true_temp)
            center = particles[i].get_center()
            adw.go_to_position(devs,center)
            if flip:
                if flipper_apd != flipper.getPos():
                    flipper.goto(flipper_apd)
            position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
            center = position.astype('float')
            adw.go_to_position(devs,center)
            particles[i].set_center(center)
            particles[i].set_temp(temp)
            
            if flip:
                if flipper_spec != flipper.getPos():
                    flipper.goto(flipper_spec)
                    time.sleep(0.5)
            t = time.time()
            trigger_spectrometer(adw)
            new_data = [t,'0','spectra',i,temp,position[0],position[1],position[2]]
            data = np.vstack([data,new_data])
            
            np.savetxt("%s%s" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
                
            print('Done with %s of %s particles' %(i+1, num_particles))
        
        pcle_track.set_center(particles[-1].get_center())
        # Make a spectra of the selected backgrounds
        
        print('Taking Spectra of Bakgrounds')
        for i in range(num_background):
            # Compare drift in particle position and update background position.
            dx = particles[-1].xcenter[0]-particles[-1].xcenter[-1]
            dy = particles[-1].ycenter[0]-particles[-1].ycenter[-1]
            dz = particles[-1].zcenter[0]-particles[-1].zcenter[-1]
                        
            bkg_center = [backgrounds[i].xcenter[0]-dx,backgrounds[i].ycenter[0]-dy,backgrounds[i].zcenter[0]-dz]
            backgrounds[i].set_center(bkg_center)

            adw.go_to_position(devs,bkg_center)
            if flip:
                if flipper_spec != flipper.getPos():
                    flipper.goto(flipper_spec)
                    time.sleep(0.5)
            trigger_spectrometer(adw)
            
            dd,ii = adw.get_timetrace_static([temperature],duration=1,acc=0.2)
            dd = np.array(dd)
            dd = 20*(dd-32768)/65536
            temp = float(np.mean(dd))*1000
            
            new_data = [t,'WL','background',i,temp,bkg_center[0],bkg_center[1],bkg_center[2]]
            data = np.vstack([data,new_data]) 
            np.savetxt("%s%s" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
            print('Done with %s of %s backgrounds'%(i,num_background))
        
        center = pcle_track.get_center()
        adw.go_to_position(devs,center)
        if flip:
            if flipper_apd != flipper.getPos():
                flipper.goto(flipper_apd)
                time.sleep(0.5)
        i=1
        while keep_track:
            print('Entering iteration %s...'%i)
            i+=1
            # Take position
            position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
            center = position.astype('float')
            pcle_track.set_center(center)
            dd,ii = adw.get_timetrace_static([temperature],.4,0.1)
            dd = np.array(dd)
            dd = 20*(dd-32768)/65536
            temp = float(np.mean(dd))*1000
            pcle_track.set_temp(temp)

            t = time.time()
            new_data = [t,position[0],position[1],position[2],temp]
            data2 = np.vstack([data2,new_data])
            try:
                np.savetxt("%s%s" %(savedir,filename2),data2, fmt='%s', delimiter=",",header=header2)
            except:
                print("Problem saving data")
            print('Press q to exit and start acquiring spectra')
            t1 = time.time()
            while time.time()-t1 < 2:
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if ord(key) == 113: #113 is ascii for letter q
                        keep_track = False
        keep_track = True
        
        ## Update coordinates
        # Once finished keeping track, update the centers of all particles checking the original deltas
        dx = pcle_track.xcenter[-1]-pcle_track.xcenter[0]
        dy = pcle_track.ycenter[-1]-pcle_track.ycenter[0]
        dz = pcle_track.zcenter[-1]-pcle_track.zcenter[0]
        for i in range(len(particles)):
            center = [particles[i].xcenter[0],particles[i].ycenter[0],particles[i].zcenter[0]]
            center[0] += dx
            center[1] += dy
            center[2] += dz
            particles[i].set_center(center)
        
        
    np.savetxt("%s%s" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    
    print('Done with the White Light\n')
    print('Program finished')
