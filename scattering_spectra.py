"""
    scattering_spectra.py
    -------------
    Acquires spectra of a particle while varying the temperature in the surrounding medium.
    Acquires a series of white light spectra, at different temperatures.
    Loops until stopped.
    The idea is to set a temperature increase and automatically registering the temperature
    at each spectra taken.

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
from special_tasks.spectrometer import abort, trigger_spectrometer
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
    pcle1 = [52.46, 52.04, 52.10]
    # pcle2 = [58.13, 41.74, 52.10]
    # pcle3 = [41.90, 48.76, 52.20]
    #pcle4 = [45.85, 53.86, 49.00]
    #pcle5 = [52.97, 55.28, 49.00]
    #pcle6 = [53.80, 49.32, 49.00]
    #pcle7 = [55.88, 51.63, 49.00]

    # Coordinates of the background
    bkg = [51.56, 47.86, 49.30]
    # Create array of particles
    particles = []
    particles.append(particle(pcle1))
    # particles.append(particle(pcle2))
    # particles.append(particle(pcle3))
    #particles.append(particle(pcle4))
    #particles.append(particle(pcle5))
    #particles.append(particle(pcle6))
    #particles.append(particle(pcle7))

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

    background = particle(bkg)

    # number_of_spectra = 7 # Number of spectra for each temperature
    number_of_accumulations = 1 # Accumulations of each spectra (for reducing noise in long-exposure images)

    #parameters for the refocusing on the particles
    dims = [.7,.7,1.5]
    accuracy = [0.1,0.1,0.1]

    name = 'spectra_temperature_white_light'
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
    # savedir2 = 'R:\\Data\\' + str(datetime.now().date()) + '\\'
    # if not os.path.exists(savedir2):
    #     os.makedirs(savedir2)
    # print('Data will also be saved in %s'%(savedir2+filename))

    #init the Adwin program and also loading the configuration file for the devices
    adw = adq()
    adw.proc_num = 9
    counter = device('APD 1')
    aom = device('AOM')
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    devs = [xpiezo,ypiezo,zpiezo]


    # Initialize the Arduino Class
    arduino = ard('COM4')
    data = np.zeros(12) # For storing Spectra
    data2 = np.zeros(7) # For storing tracking
    # For the spectra data
    header = 'Time [s], Wavelength[nm], Type, Pcle, Temp[Arduino], X [uM], Y [uM], Z [uM], Power [muW], Counts, Room Temp [C], Humidity [%]'
    # For the keep track data
    header2 = 'Time [s], X [uM], Y [uM], Z [uM], Power [muW], Counts, Temp [Arduino]'
    temperature = 1
    t_0 = time.time() # Initial time
    acquire_spectra = True
    input('Press enter when ready')
    fl = open(savedir+filename2+'.temp','a') # Appends to previous files
    fl.write(header2)
    fl.write('\n')
    fl.flush()

    fll = open(savedir+filename+'.temp','a') # Appends to previous files
    fll.write(header)
    fll.write('\n')
    fll.flush()

    print('Start the main loop for acquiring consecutive spectra:')
    while acquire_spectra:
        temp = arduino.get_flowcell_temp()
        print('Arduino temperature %s'%temp)
        for k in range(len(particles)):
            print('-> Particle %s out of %s'%(k+1,len(particles)))
            # Refocus on the particle
            center = particles[k].get_center()
            position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
            center = position.astype('float')
            particles[k].set_center(center)
            adw.go_to_position(devs,center)
            for j in range(number_of_accumulations):
                print('    ---> Accumulation %s out of %s'%(j+1,number_of_accumulations))
                trigger_spectrometer(adw)
                # Saves the data of each triggering
                dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
                t = time.time()-t_0
                room_temp = arduino.get_room_temp()
                humidity = arduino.get_room_humidity()
                power = 0 # White light power is not monitored
                new_data = [t,'WhiteLight','spectra',k+1,temp,position[0],position[1],position[2],power,np.sum(dd),room_temp,humidity]
                data = np.vstack([data,new_data])
            try:
                for item in new_data:
                    fll.write("s, " %(item))## Appends the most recent data to the temporary file
                fll.write("\n")
                fll.flush()
                np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
            #    np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header)
            except:
                print("Problem saving data")

            if k==0: # Keep track of the first particle
                # Update the centers of all particles checking the original deltas
                if len(particles)>1:
                    dx = particles[0].xcenter[-1]-particles[0].xcenter[0]
                    dy = particles[0].ycenter[-1]-particles[0].ycenter[0]
                    dz = particles[0].zcenter[-1]-particles[0].zcenter[0]
                    for i in range(len(particles)-1):
                        center = [particles[i+1].xcenter[0],particles[i+1].ycenter[0],particles[i+1].zcenter[0]]
                        center[0] += dx
                        center[1] += dy
                        center[2] += dz
                        particles[i+1].set_center(center)
                new_data2 = [t,position[0],position[1],position[2],power,np.sum(dd),temp]
                data2 = np.vstack([data2,new_data2])
                try:
                    for item in new_data2:
                        fl.write("%s, " % (item)) ## Appends the most recent data to the temporary file
                    fl.write("\n")
                    fl.flush()
                except:
                    print('Failed saving data at time %s seconds'%(t))

        print('-> Time for backgrounds...')
        bkg_center = background.get_center()
        bkg_center[2] = particles[-1].get_center()[2] # Gets the Z position of the last particle

        adw.go_to_position(devs,bkg_center)
        for j in range(number_of_accumulations):
            print('    ---> Accumulation %s out of %s'%(j+1,number_of_accumulations))
            trigger_spectrometer(adw)
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

        print('Press q to exit')
        t1 = time.time()
        while time.time()-t1 < 1:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if ord(key) == 113: #113 is ascii for letter q
                    acquire_spectra = False

    fl.close()
    fll.close()
    try:
        np.savetxt("%s%s" %(savedir,filename2),data2, fmt='%s', delimiter=",",header=header)
    except:
        print('Problem saving local data for keeping track. Check temporary files')
    print('Program finish')
