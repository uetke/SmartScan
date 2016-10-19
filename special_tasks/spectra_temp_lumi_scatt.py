# This file is work in progress.
# Do not run it!
"""
    spectra_temperature.py
    -------------
    Acquires spectra of several particles while varying the temperature in the surrounding medium.
    Acquires a series of accumulations of 532nm spectra and of scattering spectra.
    Loops until stopped. In between loops, the temperature has to be changed, the program refocus
    continuously on on of the particles to keep track of them, adjusting the relative distances.

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
import copy
import matplotlib.pyplot as plt
from devices.powermeter1830c import PowerMeter1830c as pp
from devices.flipper import Flipper
from experiment import particle
from lib.adq_mod import adq
from lib.xml2dict import device,variables
from spectrometer import abort, trigger_spectrometer

cwd = os.getcwd()
cwd = cwd.split('\\')
path = ''
# One level up from this folder
for i in range(len(cwd)-1):
    path+=cwd[i]+'\\'

if path not in sys.path:
    sys.path.insert(0, path)


if __name__ == '__main__':
    # Coordinates of the particles
    
    name_pcles = 'S160104_good_1'
    
    #pcle1 = [52.74, 56.01, 49.45]
    #pcle2 = [50.49, 58.78, 49.45]
    #pcle3 = [58.38, 59.25, 49.45]
    #pcle4 = [42.12, 54.96, 49.45]
    #pcle5 = [46.77, 52.45, 49.45]
    #pcle6 = [47.30, 51.04, 49.45]
    #pcle7 = [51.95, 50.31, 49.45]
    #pcle8 = [53.99, 53.76, 49.45]
    #pcle9 = [51.58, 53.76, 49.45]
    #pcle10 = [45.36, 47.43, 49.45]
    #pcle11 = [46.30, 48.22, 49.45]
    #pcle12 = [48.13, 47.17, 49.45]
    #pcle13 = [47.03, 43.77, 49.45]
    #pcle14 = [46.20, 43.35, 49.45]
    #pcle15 = [44.11, 46.70, 49.45]
    #pcle16 = [41.33, 53.71, 49.45]
    #pcle17 = [41.86, 42.10, 49.45]
    #pcle18 = [43.22, 43.30, 49.45]
    #pcle19 = [45.00, 42.25, 49.45]
    #pcle20 = [47.87, 41.21, 49.45]
    #pcle21 = [50.07, 42.62, 49.45]
    #pcle22 = [51.38, 45.55, 49.45]
    #pcle23 = [56.87, 45.18, 49.45]
    #pcle24 = [58.33, 44.19, 49.45]
    #pcle25 = [59.12, 45.55, 49.45]
    #pcle26 = [58.28, 49.47, 49.45]
    #pcle27 = [55.72, 43.88, 49.45]
    #pcle28 = [43.58, 57.11, 49.45]

    # Coordinates of the background
    #bkg = [52.41, 47.55, 49.45]
    ## Create array of particles
    particles = []
    #particles.append(particle(pcle1,'pcle',1))
    #particles.append(particle(pcle2,'pcle',2))
    #particles.append(particle(pcle3,'pcle',3))
    #particles.append(particle(pcle4,'pcle',4))
    #particles.append(particle(pcle5,'pcle',5))
    #particles.append(particle(pcle6,'pcle',6))
    #particles.append(particle(pcle7,'pcle',7))
    #particles.append(particle(pcle8,'pcle',8))
    #particles.append(particle(pcle9,'pcle',9))
    #particles.append(particle(pcle10,'pcle',10))
    #particles.append(particle(pcle11,'pcle',11))
    #particles.append(particle(pcle12,'pcle',12))
    #particles.append(particle(pcle13,'pcle',13))
    #particles.append(particle(pcle14,'pcle',14))
    #particles.append(particle(pcle15,'pcle',15))
    #particles.append(particle(pcle16,'pcle',16))
    #particles.append(particle(pcle17,'pcle',17))
    #particles.append(particle(pcle18,'pcle',18))
    #particles.append(particle(pcle19,'pcle',19))
    #particles.append(particle(pcle20,'pcle',20))
    #particles.append(particle(pcle21,'pcle',21))
    #particles.append(particle(pcle22,'pcle',22))
    #particles.append(particle(pcle23,'pcle',23))
    #particles.append(particle(pcle24,'pcle',24))
    #particles.append(particle(pcle25,'pcle',25))
    #particles.append(particle(pcle26,'pcle',26))
    #particles.append(particle(pcle27,'pcle',27))
    #particles.append(particle(pcle28,'pcle',28))
    

    ##################################################################################
    #   The next few lines are for updating the coordinates of the particles         #
    #  in case there is the need for re_starting the program. Only the coordinates   #
    #  of the first particle (the one used for tracking) are needed. The other       #
    #  coordinates will be updated based on this one.                                #
    #  It has to be commented out for a normal execution.                            #
    ##################################################################################

    #new_center_first_particle = [39.14999999999983,47.36000000000002,64.09999999999994] # Get this value from the keep_track_temp.
    #particles[0].set_center(new_center_first_particle)
    ## Update the coordinates of the other particles
    #dx = particles[0].xcenter[-1]-particles[0].xcenter[0]
    #dy = particles[0].ycenter[-1]-particles[0].ycenter[0]
    #dz = particles[0].zcenter[-1]-particles[0].zcenter[0]
    #for i in range(len(particles)-1):
    #    center = [particles[i+1].xcenter[0],particles[i+1].ycenter[0],particles[i+1].zcenter[0]]
    #    center[0] += dx
    #    center[1] += dy
    #    center[2] += dz
    #    particles[i+1].set_center(center)
    #/********************************************************************************/#

    #background = particle(bkg,'bkg',1)

    number_of_accumulations = 4 # Accumulations of each spectra (for reducing noise in long-exposure images)

    #parameters for the refocusing on the particles
    dims = [1,1,1.5]
    accuracy = [0.1,0.1,0.1]

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

    ## Prepare the folder in network drive
    #savedir2 = 'R:\\monos\\Aquiles\\Data\\' + str(datetime.now().date()) + '\\'
    #if not os.path.exists(savedir2):
    #    os.makedirs(savedir2)
    #print('Data will also be saved in %s'%(savedir2+filename))

    data = np.loadtxt('%s%s.txt' %(savedir, name_pcles),dtype='bytes',delimiter =',').astype('str')#strange b in front of strings 
    num_particles = sum(data[:,0]=='particle')
    
    for i in range(num_particles):
        center = data[i,1:4].astype('float')
        particles.append(particle(center,'pcle',i+1))
    
    center = data[-1,1:4].astype('float')
    background = particle(center,'bkg',1)   
    
    
    data = np.zeros(10) # For storing Spectra
    data2 = np.zeros(7) # For storing tracking
    # For the spectra data
    header = 'Time [s], Wavelength[nm], Type, Pcle, Temp[mV], X [uM], Y [uM], Z [uM], Power [muW], Counts'
    # For the keep track data
    header2 = 'Time [s], X [uM], Y [uM], Z [uM], Power [muW], Counts, Temp [mV]'
    temperature = 1
    t_0 = time.time() # Initial time

    acquire_spectra = True

    input('Press enter when WhiteLight is on and everything is ready')

    fl = open(savedir+filename2+'.temp','a') # Appends to previous files
    fl.write(header2)
    fl.write('\n')
    fl.flush()
    
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
        
    #init the Adwin program and also loading the configuration file for the devices
    adw = adq() 
    adw.proc_num = 9
    counter = device('APD 1')

    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    temperature = device('Temperature')
    
    devs = [xpiezo,ypiezo,zpiezo]
        
    while acquire_spectra:
        print('Aquiring 532 data...')
        dd,ii = adw.get_timetrace_static([temperature],duration=1,acc=0.2)
        dd = np.array(dd)
        dd = 20*(dd-32768)/65536
        temp = float(np.mean(dd))*1000
        true_temp = temp*.0310-2.1136 # This calibration depends on the experiment. Use with care.
        print('Starting with temperature %s'%true_temp)

        pmeter.wavelength = 532
        input('Spectrometer ready for 532?')
        # Will skip the spectra of the first particle, used only for tracking
        for k in range(1,len(particles)):
            for j in range(number_of_accumulations):
                print('-> Particle %s out of %s'%(k+1,len(particles)))
                # Refocus on the particle
                center = particles[k].get_center()
                adw.go_to_position(devs,center)
                if flip:
                    if flipper_apd != flipper.getPos():
                        flipper.goto(flipper_apd)
                position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
                time_last_refocus = time.time()
                center = position.astype('float')
                particles[k].set_center(center)
                adw.go_to_position(devs,center) 
                dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
                intensity = np.sum(dd)                
                print('---> Accumulation %s out of %s'%(j+1,number_of_accumulations))
                if flip:
                    if flipper_spec != flipper.getPos():
                        flipper.goto(flipper_spec)
                        time.sleep(0.5)
                trigger_spectrometer(adw)
                # Saves the data of each triggering
                
                t = time.time()-t_0
                try:
                    power = pmeter.data*1000000
                except:
                    power = 0
                dd,ii = adw.get_timetrace_static([temperature],duration=1,acc=0.2)
                dd = np.array(dd)
                dd = 20*(dd-32768)/65536
                temp = float(np.mean(dd))*1000
                new_data = [t,'532','spectra',k+1,temp,position[0],position[1],position[2],power,intensity]
                data = np.vstack([data,new_data])
                try:
                    np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
                except:
                    print("Problem saving data")

        print('-> Time for backgrounds...')
        
        # Compare drift in particle position and update background position.
        dx = particles[-1].xcenter[0]-particles[-1].xcenter[-1]
        dy = particles[-1].ycenter[0]-particles[-1].ycenter[-1]
        
        bkg_center = [background.xcenter[0]-dx,background.ycenter[0]-dy,background.zcenter[0]]
        bkg_center[2] = particles[-1].get_center()[2] # Gets the Z position of the last particle

        adw.go_to_position(devs,bkg_center)
        for j in range(number_of_accumulations):
            print('--->Bkg Accumulation %s out of %s'%(j+1,number_of_accumulations))
            dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
            intensity = np.sum(dd)
            if flip:
                if flipper_spec != flipper.getPos():
                    flipper.goto(flipper_spec)
                    time.sleep(0.5)
            trigger_spectrometer(adw)
            try:
                power = pmeter.data*1000000
            except:
                power = 0
            

            dd,ii = adw.get_timetrace_static([temperature],duration=1,acc=0.2)
            dd = np.array(dd)
            dd = 20*(dd-32768)/65536
            temp = float(np.mean(dd))*1000
            t = time.time()-t_0
            new_data = [t,'532','background',1,temp,bkg_center[0],bkg_center[1],bkg_center[2],power,intensity]
            data = np.vstack([data,new_data])
        try:
            np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
        #    np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header)
        except:
            print("Problem saving data")
        true_temp = temp*.0310-2.1136 # This calibration depends on the experiment. Use with care.
        print('Done with 532 at temperature %s.'%true_temp)
        
        input('Now is time for White Light. Prepare everything...')

        print('Aquiring WhiteLight data...')
        dd,ii = adw.get_timetrace_static([temperature],duration=1,acc=0.2)
        dd = np.array(dd)
        dd = 20*(dd-32768)/65536
        temp = float(np.mean(dd))*1000
        true_temp = temp*.0310-2.1136 # This calibration depends on the experiment. Use with care.
        print('Starting with temperature %s'%true_temp)

        pmeter.wavelength = 532

        for k in range(1,len(particles)):
            j=1 # White light doesnt need accumulations
            
            print('-> Particle %s out of %s'%(k+1,len(particles)))
            # Refocus on the particle
            center = particles[k].get_center()
            adw.go_to_position(devs,center)
            if flip:
                if flipper_apd != flipper.getPos():
                    flipper.goto(flipper_apd)
            position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
            time_last_refocus = time.time()
            center = position.astype('float')
            particles[k].set_center(center)
            adw.go_to_position(devs,center)
            dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
            intensity = np.sum(dd)              
            if flip:
                if flipper_spec != flipper.getPos():
                    flipper.goto(flipper_spec)
                    time.sleep(0.5)
            trigger_spectrometer(adw)
            # Saves the data of each triggering
            
            t = time.time()-t_0
            try:
                power = pmeter.data*1000000
            except:
                power = 0
            dd,ii = adw.get_timetrace_static([temperature],duration=1,acc=0.2)
            dd = np.array(dd)
            dd = 20*(dd-32768)/65536
            temp = float(np.mean(dd))*1000
            new_data = [t,'0','spectra',k+1,temp,position[0],position[1],position[2],power,intensity]
            data = np.vstack([data,new_data])
            try:
                np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
            except:
                print("Problem saving data")

        print('-> Time for backgrounds...')
        
        # Compare drift in particle position and update background position.
        dx = particles[-1].xcenter[0]-particles[-1].xcenter[-1]
        dy = particles[-1].ycenter[0]-particles[-1].ycenter[-1]
        
        bkg_center = [background.xcenter[0]-dx,background.ycenter[0]-dy,background.zcenter[0]]
        bkg_center[2] = particles[-1].get_center()[2] # Gets the Z position of the last particle

        adw.go_to_position(devs,bkg_center)
        if flip:
            if flipper_apd != flipper.getPos():
                flipper.goto(flipper_apd)
        dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
        intensity = np.sum(dd)
        if flip:
            if flipper_spec != flipper.getPos():
                flipper.goto(flipper_spec)
                time.sleep(0.5)
        trigger_spectrometer(adw)
        try:
            power = pmeter.data*1000000
        except:
            power = 0
        

        dd,ii = adw.get_timetrace_static([temperature],duration=1,acc=0.2)
        dd = np.array(dd)
        dd = 20*(dd-32768)/65536
        temp = float(np.mean(dd))*1000
        t = time.time()-t_0
        new_data = [t,'0','background',1,temp,bkg_center[0],bkg_center[1],bkg_center[2],power,intensity]
        data = np.vstack([data,new_data])
        try:
            np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
        except:
            print("Problem saving data")
        
        true_temp = temp*.0310-2.1136 # This calibration depends on the experiment. Use with care.
        print('Done with WhiteLight at temperature %s.'%true_temp)        

        # Let's start focusing on the particle
        print('The program will start refocusing on the particle')
        i = 1

        center = particles[0].get_center() # Use the first particle for refocusing
        adw.go_to_position(devs,center)
        if flip:
            if flipper_apd != flipper.getPos():
                flipper.goto(flipper_apd)
        keep_track = True
        while keep_track:
            print('Entering iteration %s...'%i)
            i+=1
            # Take position
            
            position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
            center = position.astype('float')
            adw.go_to_position(devs,center)
            particles[0].set_center(center)
            # Take power
            try:
                power = pmeter.data*1000000
            except:
                power = 0
            # Take intensity
            dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)

            t = time.time()-t_0
            dd,ii = adw.get_timetrace_static([temperature],duration=1,acc=0.2)
            dd = np.array(dd)
            dd = 20*(dd-32768)/65536
            temp = float(np.mean(dd))*1000
            true_temp = temp*.0310-2.1136 # This calibration depends on the experiment. Use with care.
            
            print('     --> Temperature: %s'%(true_temp))
            new_data2 = [t,position[0],position[1],position[2],power,np.sum(dd),temp]
            data2 = np.vstack([data2,new_data2])
            try:
                for item in new_data2:
                    fl.write("%s, " % (item)) ## Appends the most recent data to the temporary file
                fl.write("\n")
                fl.flush()
            except:
                print('Failed saving data at time %s seconds'%(t))
            print('Press q to exit and start acquiring spectra')
            t1 = time.time()
            while time.time()-t1 < 2:
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if ord(key) == 113: #113 is ascii for letter q
                        keep_track = False

        # Once finished keeping track, update the centers of all particles checking the original deltas
        dx = particles[0].xcenter[-1]-particles[0].xcenter[0]
        dy = particles[0].ycenter[-1]-particles[0].ycenter[0]
        dz = particles[0].zcenter[-1]-particles[0].zcenter[0]
        for i in range(len(particles)-1):
            center = [particles[i+1].xcenter[0],particles[i+1].ycenter[0],particles[i+1].zcenter[0]]
            center[0] += dx
            center[1] += dy
            center[2] += dz
            particles[i+1].set_center(center)

        answer = input('Do you want to take more spectra at a different temperature?[y/n]')
        if answer == 'n':
            keep_track = False
            acquire_spectra = False


    fl.close()
    try:
        np.savetxt("%s%s" %(savedir,filename2),data2, fmt='%s', delimiter=",",header=header)
    except:
        print('Problem saving local data for keeping track. Check temporary files')
    print('Program finished')
