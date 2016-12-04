# -*- coding: utf-8 -*-
"""
    Acquires timetraces on two APDs of the defined coordinates after refocusing on them.
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
from devices.powermeter1830c import PowerMeter1830c as pp
import msvcrt
import sys
import os

from start import adding_to_path


adding_to_path('lib')

cwd = os.getcwd()
savedir = cwd + '\\' + str(datetime.now().date()) + '\\'
#names of the parameters
par=variables('Par')
fpar=variables('FPar')
data=variables('Data')
fifo=variables('Fifo')


if __name__ == '__main__':

    #init the Adwin programm and also loading the configuration file for the devices
    adw = adq()
    aom = device('AOM')
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    counter = device('APD 1')
    apd1 = device('APD 1')
    apd2 = device('APD 2')
    temperature = device('Temperature')

    datafile = 'S190917_better_532'

    number_of_timetraces = 5
    laser_min = 80 # In uW
    laser_max = 350 # In uW
    laser_powers = np.linspace(laser_min,laser_max,number_of_timetraces)

    focusing_power = 200 # In uW

    pcle_to_track = 33 # The particle to keep track

    cwd = os.getcwd()
    savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
    if not os.path.exists(savedir):
        os.makedirs(savedir)

    # Check if the calibration of the AOM was done today and import the data for it.
    if os.path.exists(savedir+'aom_calibration.txt'):
        print('Importing AOM calibration...')
        AOM_voltage = np.loadtxt(savedir+'aom_calibration2.txt').astype('float')[6:]
        intensity = np.loadtxt(savedir+'aom_calibration.txt').astype('float')[6:]
        P = np.polyfit(intensity,AOM_voltage,2)
        print(P)
        #plt.plot(intensity,AOM_voltage,'.')
        #plt.plot(intensity,np.polyval(P,intensity))
        #plt.ylabel('AOM voltage (V)')
        #plt.xlabel('Laser intensity (uW)')
        #plt.show(block=False)
    else:
        raise Exception('The AOM was not calibrated today, please do it before running this program...')


    name = 'AS_to_S_Temp_Dependence_'
    filename = name
    i=1
    filename = '%s_%s' %(name,i)
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

    header = "Time,pcle,temp,power,x-pos,y-pos,z-pos,apd1,apd2"
    header2 = "Time,x-pos,y-pos,z-pos,temp"

    data = np.loadtxt('%s%s.txt' %(savedir, datafile),dtype='bytes',delimiter =',').astype('str')

    num_particles = sum(data[:,0]=='particle')

    particles = []
    for i in range(num_particles):
        center = data[i,1:4].astype('float')
        particles.append(particle(center,'pcle',i+1))

    pcle_track = particles[pcle_to_track]

    data = np.zeros(9)
    data2 = np.zeros(5)

    acquire_timetrace = True
    keep_track = True

    #Newport Power Meter
    pmeter = pp.via_serial(16)
    pmeter.initialize()
    pmeter.wavelength = 633
    pmeter.attenuator = True
    pmeter.filter = 'Medium'
    pmeter.go = True
    pmeter.units = 'Watts'
    first = True
    while acquire_timetrace:
        if not first:
            answer = input('Do you want to take more timetraces at a different temperature?[y/n]')
            if answer == 'n':
                keep_track = False
                acquire_timetrace = False
                break
            for i in range(num_particles):
                dd,ii = adw.get_timetrace_static([temperature],duration=0.2,acc=0.2)
                dd = np.array(dd)
                dd = 20*(dd-32768)/65536
                temp = float(np.mean(dd))*1000
                true_temp = temp*.0310-2.1136 # This calibration depends on the experiment. Use with care.

                print('Starting with Temperature %s'%true_temp)
                power_aom = np.polyval(P,focusing_power)
                adw.go_to_position([aom],[power_aom])
                center = particles[i].get_center()
                adw.go_to_position(devs,center)
                position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
                center = position.astype('float')
                adw.go_to_position(devs,center)
                particles[i].set_center(center)
                particles[i].set_temp(temp)

                for m in range(number_of_timetraces):

                    power_aom = np.polyval(P,laser_powers[m])
                    adw.go_to_position([aom],[power_aom])
                    print('Laser power: %3iuW'%laser_powers[m])
                    print('Acquire APD1')
                    dd,ii = adw.get_timetrace_static([apd1],duration=1,acc=0.2)
                    dd = np.array(dd)
                    ad1 = int(np.sum(dd))

                    print('Acquire APD2')
                    dd,ii = adw.get_timetrace_static([apd2],duration=1,acc=0.2)
                    dd = np.array(dd)
                    ad2 = int(np.sum(dd))
                    try:
                        power = pmeter.data*1000000
                    except:
                        power = 0


                    t = time.time()
                    new_data = [t,i,temp,power,position[0],position[1],position[2],ad1,ad2]
                    data = np.vstack([data,new_data])

                    np.savetxt("%s%s" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)

                print('Done with %s of %s particles' %(i+1, num_particles))

        first = False
        pcle_track.set_center(particles[pcle_to_track].get_center())

        center = pcle_track.get_center()
        adw.go_to_position(devs,center)
        i=1
        power_aom = np.polyval(P,focusing_power)
        adw.go_to_position([aom],[power_aom])
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
            print('Press q to exit and start acquiring timetraces')
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

    print('Done with the timetraces\n')
    print('Program finished')
