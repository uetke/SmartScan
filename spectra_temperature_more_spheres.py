"""
    spectra_temperature.py
    -------------
    Acquires spectra of a particle while varying the temperature in the surrounding medium. 
    Acquires a series of 532nm spectra, at different excitation powers. 
    Loops until stopped. In between loops, the temperature has to be changed, the program refocus 
    continuously on on of the particles to keep track of it, and adjusts the relative distances.
    
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
import matplotlib.pyplot as plt

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
from devices.arduino import arduino as ard

class particle():
    def __init__(self,coords):
        self.xcenter = []
        self.ycenter = []
        self.zcenter = []
        self.xcenter.append(coords[0])
        self.ycenter.append(coords[1])
        self.zcenter.append(coords[2])
    
    def get_center(self):
        center = [self.xcenter[-1],self.ycenter[-1],self.zcenter[-1]]
        return center
    
    def set_center(self,coords):
        self.xcenter.append(coords[0])
        self.ycenter.append(coords[1])
        self.zcenter.append(coords[2])
    
if __name__ == '__main__': 
    # Coordinates of the particles
    pcle1 = [58.08, 52.21, 49.00]
    pcle2 = [49.21, 51.56, 49.00]
    pcle3 = [44.27, 50.72, 49.00]
    pcle4 = [45.85, 53.86, 49.00]
    pcle5 = [52.97, 55.28, 49.00]
    pcle6 = [53.80, 49.32, 49.00]
    pcle7 = [55.88, 51.63, 49.00]
    
    # Coordinates of the background
    bkg = [48.34, 49.36, 49.00]
    # Create array of particles
    particles = []
    particles.append(particle(pcle1))
    particles.append(particle(pcle2))
    particles.append(particle(pcle3))
    particles.append(particle(pcle4))
    particles.append(particle(pcle5))
    particles.append(particle(pcle6))
    particles.append(particle(pcle7))
    
    background = particle(bkg)
    
    number_of_spectra = 7 # Number of spectra for each temperature
    number_of_accumulations = 5 # Accumulations of each spectra (for reducing noise in long-exposure images)
    
    #parameters for the refocusing on the particles
    dims = [1,1,1.5]
    accuracy = [0.1,0.1,0.1]
    
    # Maximum and minimum laser intensities
    
    laser_min = 0 # In uW
    laser_max = 1000 # In uW
    laser_powers = np.linspace(laser_min,laser_max,number_of_spectra)
    focusing_power = 450 # In uW (The power used to refocus on the particles and to keep track during temperature changes)
    
    # How much time between refocusing
    time_for_refocusing = 5*60 # In seconds
    
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
    
    
    #init the Adwin program and also loading the configuration file for the devices
    adw = adq() 
    adw.proc_num = 9
    counter = device('APD 1')
    aom = device('AOM')
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
    
    # Initialize the Arduino Class
    
    arduino = ard('COM9')
    
    data = np.zeros(12) # For storing Spectra
    data2 = np.zeros(7) # For storing tracking
    # For the spectra data
    header = 'Time [s], Wavelength[nm], Type, Pcle, Temp[Arduino], X [uM], Y [uM], Z [uM], Power [muW], Counts, Room Temp [C], Humidity [%]' 
    # For the keep track data
    header2 = 'Time [s], X [uM], Y [uM], Z [uM], Power [muW], Counts, Temp [Arduino]' 
    temperature = 1
    t_0 = time.time() # Initial time
    
    acquire_spectra = True
    
    input('Press enter when 532nm is on and everything is ready')
    
    fl = open(savedir+filename2+'.temp','a') # Appends to previous files
    fl.write(header2)
    fl.write('\n')
    fl.flush()
    
    while acquire_spectra:
        print('Aquiring 532nm data...')
        temp = arduino.get_flowcell_temp()
        print('Starting with Arduino temperature %s'%temp)
        
        pmeter.wavelength = 532
        
        for k in range(len(particles)):
            # Refocus on the particle
            center = particles[k].get_center()
            print('-> Focusing on particle %s out of %s'%(k+1,len(particles)))
            power_aom = np.polyval(P,focusing_power)
            adw.go_to_position([aom],[power_aom])
            adw.go_to_position(devs,center)
            position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
            time_last_refocus = time.time()
            center = position.astype('float')
            particles[k].set_center(center)
            adw.go_to_position(devs,center)
            for j in range(number_of_accumulations):
                print('    ---> Accumulation %s out of s'%(j,number_of_accumulations))
                trigger_spectrometer(adw)
                
                # Saves the data of each triggering
                dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
                t = time.time()-t_0
                room_temp = arduino.get_room_temp()
                humidity = arduino.get_room_humidity()
                try:
                    power = pmeter.data*1000000
                except:
                    power = 0
                new_data = [t,'532','spectra',k+1,temp,position[0],position[1],position[2],power,np.sum(dd),room_temp,humidity]
                data = np.vstack([data,new_data])
                                
                if (time.time()-time_last_refocus>time_for_refocusing) and (j<number_of_accumulations-1):
                    print('Focusing on particle %s'%(k+1))
                    position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
                    time_last_refocus = time.time()
                    center = position.astype('float')
                    adw.go_to_position(devs,center)
                    particles[k].set_center(center)
            try:
                np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
            #    np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header)    
            except:
                print("Problem saving data")
            
        print('Time for backgrounds...')
        bkg_center = background.get_center()
        bkg_center[2] = particles[-1].get_center()[2] # Gets the Z position of the last particle
        
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
            temp = arduino.get_flowcell_temp()
            room_temp = arduino.get_room_temp()
            humidity = arduino.get_room_humidity()
            new_data = [t,'532','background',1,temp,bkg_center[0],bkg_center[1],bkg_center[2],power,np.sum(dd),room_temp,humidity]
            data = np.vstack([data,new_data])
        try:
            np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
        #    np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header) 
        except:
            print("Problem saving data")    

        print('Done with Arduino temperature %s.'%temp)
        
        # Let's start focusing on the particle
        print('The program will start refocusing on the particle')
        i = 1
        
        power_aom = np.polyval(P,focusing_power)
        adw.go_to_position([aom],[power_aom])
        adw.go_to_position([aom],[power_aom])
        center = particles[0].get_center() # Use the first particle for refocusing
        adw.go_to_position(devs,center)
        
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
            temp = arduino.get_flowcell_temp()
            new_data = [t,position[0],position[1],position[2],power,np.sum(dd),temp]
            data2 = np.vstack([data2,new_data])
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
                print(time.time()-t1)
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
            print('Problem saving local data for keeping track. Check temporar files')   
        print('Program finish')
