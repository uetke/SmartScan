"""
    spectra_temperature_more_particles_move_grating.py
    -------------
    Acquires spectra of a particle while varying the temperature in the surrounding medium.
    The program also communicates with the spectrometer computer to change the position
    of the grating. This enables to get rid of the dark lines observed in the past.
    Acquires a series of White-Light spectra. Then 532nm spectra and then 633 spectra at different excitation powers.
    Loops until stopped.
    In between loops, the temperature has to be changed, the program refocus
    continuously on one of the particles to keep track of it, and adjusts the relative distances of all the others.

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
from spectrometer import abort, trigger_spectrometer, client_spectrometer
import copy

# Adds the needed folders to the path of python
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

def acquire_spectra(particle,how,spec,spec_wl):
    """ Function for acquiring spectra of an array of particles.
        ..particle: Object of class particle
        ..how: Dictionary with the information on the type of spectra to acquire.
                how['type']: fixed, variable
                              fixed is used when no change in intensity is required.
                              variable is used when the intensity changes.
                how['device']: The decice to which to set a particular value.
                                This is to keep in mind the possibility of taking spectra with
                                two different lasers, for instance.
                how['values']: When used a type variable, the value to set to the device
                how['description']: Description for output to screen.
        ..spec: client_spectrometer class
        ..spec_wl: list with the min and max wavelengths to send to the spectrometer when
                    accumulating
    """"
    global adw
    global number_of_accumulations
    # Refocus on the particle
    center = particle[k].get_center()
    print('Focusing on particle %s'%(k+1))
    position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
    time_last_refocus = time.time()
    center = position.astype('float')
    particle.set_center(center)
    adw.go_to_position(devs,center)
    wavelengths = np.linspace(spec_wl[0],spec_wl[1],number_of_accumulations)
    if how['type'] == 'fixed':
        accumulate_spectrometer(wavelengths,spec)

    elif how['type'] == 'variable':
        for m in range(number_of_spectra):
            dev = how['device']
            values = how['values']
            adw.go_to_position([dev],[values[m]])
            accumulate_spectrometer(wavelengths,spec)
            if (time.time()-time_last_refocus>=time_for_refocusing):
                position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
                time_last_refocus = time.time()
                center = position.astype('float')
                particle.set_center(center)
                adw.go_to_position(devs,center)
    return particle

def accumulate_spectrometer(wavelengths,spec):
    global number_of_accumulations
    global time_for_refocusing
    global adw

    time_last_refocus = time.time()
    for j in range(number_of_accumulations):
        print('Triggering the spectrometer for %s out of %s on particle %s'%(j+1,number_of_accumulations))
        wl = wavelengths[j]
        print('Moving the spectrometer to wavelength %s'%wl)
        spec.goto(wl)
        trigger_spectrometer(adw)

if __name__ == '__main__':
    # Coordinates of the particles
    pcle1 = [58.08, 52.21, 49.00]
    pcle2 = [49.21, 51.56, 49.00]
    # Coordinates of the background
    bkg = [48.34, 49.36, 49.00]
    # Create array of particles
    particles = []
    particles.append(particle(pcle1))
    particles.append(particle(pcle2))

    background = particle(bkg)

    number_of_spectra = 7 # Number of spectra for each temperature
    number_of_accumulations = 5 # Accumulations of each spectra (for reducing noise in long-exposure images)

    #parameters for the refocusing on the particles
    dims = [1,1,1.5]
    accuracy = [0.1,0.1,0.1]

    # Value that the AOM will have while focusing with 633nm
    focusing_aom = 1.25
    # How much time between refocusing
    time_for_refocusing = 5*60 # In seconds
    # Central wavelength for the spectrometer
    central_wavelength = 633
    # Min and max range of wavelengths in which to accumulate
    min_wl,max_wl = 631,635

    # This step is important to check if the spectrometer makes noise
    client_spectrometer.goto(central_wavelength)


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

    while acquire_spectra:
        print('First acquire White Light data')
        input('Press enter when White light is on')
        temp = arduino.get_flowcell_temp()
        print('Starting with Arduino temperature %s'%temp)

        pmeter.wavelength = 532
        for k in range(len(particles)):
            # Refocus on the particle
            center = particles[k].get_center()
            print('Focusing on particle %s'%(k+1))
            position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
            time_last_refocus = time.time()
            center = position.astype('float')
            particles[k].set_center(center)
            adw.go_to_position(devs,center)
            for j in range(number_of_accumulations):
                print('Triggering the spectrometer for White Light data %s out of %s on particle %s'%(j+1,number_of_accumulations,k+1))
                trigger_spectrometer(adw)
                if (time.time()-time_last_refocus>time_for_refocusing) and (j<number_of_accumulations-1):
                    print('Focusing on particle %s'%(k+1))
                    position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
                    time_last_refocus = time.time()
                    center = position.astype('float')
                    adw.go_to_position(devs,center)
                    particles[k].set_center(center)
            try:
                power = pmeter.data*1000000
            except:
                power = 0

            dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
            t = time.time()-t_0
            room_temp = arduino.get_room_temp()
            humidity = arduino.get_room_humidity()

            new_data = [t,'532','spectra',k+1,temp,position[0],position[1],position[2],power,np.sum(dd),room_temp,humidity]
            data = np.vstack([data,new_data])
            try:
                np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
            #    np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header)
            except:
                print("Problem saving data")


        print('First acquire 532nm data')
        input('Press enter when 532nm is on')
        temp = arduino.get_flowcell_temp()
        print('Starting with Arduino temperature %s'%temp)

        pmeter.wavelength = 532

        for k in range(len(particles)):
            # Refocus on the particle
            center = particles[k].get_center()
            print('Focusing on particle %s'%(k+1))
            position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
            time_last_refocus = time.time()
            center = position.astype('float')
            particles[k].set_center(center)
            adw.go_to_position(devs,center)
            for j in range(number_of_accumulations):
                print('Triggering the spectrometer for 532nm data %s out of %s on particle %s'%(j+1,number_of_accumulations,k+1))
                trigger_spectrometer(adw)
                if (time.time()-time_last_refocus>time_for_refocusing) and (j<number_of_accumulations-1):
                    print('Focusing on particle %s'%(k+1))
                    position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
                    time_last_refocus = time.time()
                    center = position.astype('float')
                    adw.go_to_position(devs,center)
                    particles[k].set_center(center)
            try:
                power = pmeter.data*1000000
            except:
                power = 0

            dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
            t = time.time()-t_0
            room_temp = arduino.get_room_temp()
            humidity = arduino.get_room_humidity()

            new_data = [t,'532','spectra',k+1,temp,position[0],position[1],position[2],power,np.sum(dd),room_temp,humidity]
            data = np.vstack([data,new_data])
            try:
                np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
            #    np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header)
            except:
                print("Problem saving data")

        print('Time for backgrounds')
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
        # Switch to 633nm
        print('Time to switch to 633nm')
        pmeter.wavelength = 633
        input('Press enter when ready')
        #temp = input('Enter the value of the multimeter')



        for k in range(len(particles)):
            for m in range(number_of_spectra):
                temp = arduino.get_flowcell_temp()
                print('Arduino temperature %s'%temp)
                print('Focusing on particle %s'%(k+1))
                power_aom = focusing_aom
                adw.go_to_position([aom],[power_aom])

                center = particles[k].get_center()
                position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
                time_last_refocus = time.time()
                center = position.astype('float')
                particles[k].set_center(center)
                adw.go_to_position(devs,center)

                time_last_refocus = time.time()

                power_aom = 1.5-m*1./number_of_spectra
                adw.go_to_position([aom],[power_aom])

                for j in range(number_of_accumulations):
                    # Triggers the spectrometer
                    print('Acquiring 633nm data. Intensity %s out of %s. Accumulation %s out of %s. Particle %s.'%(m+1,number_of_spectra,j+1,number_of_accumulations,k+1))
                    trigger_spectrometer(adw)

                    if time.time()-time_last_refocus>time_for_refocusing:
                        print('Refocusing...')
                        position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
                        time_last_refocus = time.time()
                        center = position.astype('float')
                        adw.go_to_position(devs,center)
                        particles[k].set_center(center)
                try:
                    power = pmeter.data*1000000
                except:
                    power = 0
                # Take intensity
                room_temp = arduino.get_room_temp()
                humidity = arduino.get_room_humidity()
                dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
                t = time.time()-t_0
                new_data = [t,'633','spectra',k+1,temp,position[0],position[1],position[2],power,np.sum(dd),room_temp,humidity]
                data = np.vstack([data,new_data])
                try:
                    np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
                #    np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header)
                except:
                    print("Problem saving data")

        print('Time for backgrounds')
        bkg_center = background.get_center()
        bkg_center[2] = particles[-1].get_center()[2] # Gets the Z position of the last particle

        adw.go_to_position(devs,bkg_center)

        for m in range(number_of_spectra):
            power_aom = 1.5-m*1./number_of_spectra
            adw.go_to_position([aom],[power_aom])
            for j in range(number_of_accumulations):
                print('633nm background %s out of %s, accumulation %s out of %s'%(m+1,number_of_spectra,j+1,number_of_accumulations))
                trigger_spectrometer(adw)
            try:
                power = pmeter.data*1000000
            except:
                power = 0

            temp = arduino.get_flowcell_temp()
            room_temp = arduino.get_room_temp()
            humidity = arduino.get_room_humidity()
            dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
            t = time.time()-t_0
            new_data = [t,'633','background',1,temp,bkg_center[0],bkg_center[1],bkg_center[2],power,np.sum(dd),room_temp,humidity]
            data = np.vstack([data,new_data])
            try:
                np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
            #    np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header)
            except:
                print("Problem saving data")

        print('Done with Arduino temperature %s.'%temp)
        #temp = input('Enter the value of the multimeter')
        #temp = float(temp)
        #final_temp = (temp-100)/.385
        #print('The final temperature is %s and the initial temperature was %s'%(final_temp,true_temp))

        print('Time for a final 532nm spectra to check reshaping')
        input('Enter when ready with the 532nm \n')

        pmeter.wavelength = 532
        # Refocus on the particle

        for k in range(len(particles)):
            # Refocus on the particle
            center = particles[k].get_center()
            position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
            time_last_refocus = time.time()
            center = position.astype('float')
            particles[k].set_center(center)
            adw.go_to_position(devs,center)
            for j in range(number_of_accumulations):
                print('Triggering the spectrometer for 532nm data %s out of %s on particle %s'%(j+1,number_of_accumulations,k+1))
                trigger_spectrometer(adw)
                if (time.time()-time_last_refocus>time_for_refocusing) and (j<number_of_accumulations-1):
                    print('Refocusing...')
                    position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
                    time_last_refocus = time.time()
                    center = position.astype('float')
                    adw.go_to_position(devs,center)
                    particles[k].set_center(center)
            try:
                power = pmeter.data*1000000
            except:
                power = 0

            temp = arduino.get_flowcell_temp()
            room_temp = arduino.get_room_temp()
            humidity = arduino.get_room_humidity()

            dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
            t = time.time()-t_0
            new_data = [t,'532','spectra',k+1,temp,position[0],position[1],position[2],power,np.sum(dd),room_temp,humidity]
            data = np.vstack([data,new_data])
            try:
                np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
                np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header)
            except:
                print("Problem saving data")

        answer = input('Do you want to take more spectra at a different temperature?[y/n]')
        keep_track = True
        if answer == 'n':
            keep_track = False
            acquire_spectra = False
        else:
        # Let's start focusing on the particle
            print('The program will start refocusing on the particle')
            i = 1

            power_aom = focusing_aom
            adw.go_to_position([aom],[power_aom])
            center = particles[0].get_center() # Use the first particle for refocusing
            adw.go_to_position(devs,center)
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

        print('Program finish')
