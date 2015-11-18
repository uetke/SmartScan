"""
    spectra_white_light_some_T.py
    -------------
    Acquires spectra of a particle while varying the temperature in the surrounding medium.
    Acquires a series of white light spectra, at different central wavelengths.
    Loops until stopped. In between loops, the temperature has to be changed, the program refocus
    continuously on one of the particles to keep track of it, and adjusts the relative distances.

    AUTHOR: Aquiles Carattino
    EMAIL: carattino@physics.leidenuniv.nl

"""

import numpy as np
import time
import msvcrt
import sys
import os
from datetime import datetime
import pickle
from experiment import *


if __name__ == '__main__':
    # Initialize the class for the experiment
    exp = experiment()

    # Coordinates of the particles
    pcle = 'pcle'
    pcle1 = [32.08, 50.11, 51.20]
    # pcle2 = [47.36, 43.09, 47.00]
    # pcle3 = [48.04, 49.11, 47.00]
    # pcle4 = [60.67, 38.33, 47.00]
    #pcle5 = [52.97, 55.28, 49.00]
    #pcle6 = [53.80, 49.32, 49.00]
    #pcle7 = [55.88, 51.63, 49.00]

    # Coordinates of the background
    bkg = [43.00, 41.00, 51.20]

    # Create array of particles
    particles = []
    particles.append(particle(pcle1,pcle,1))
    # particles.append(particle(pcle2,pcle,2))
    # particles.append(particle(pcle3,pcle,3))
    # particles.append(particle(pcle4,pcle,4))

    background = particle(bkg,'bkg',1)

    ##################################################################################
    #   The next few lines are for updating the coordinates of the particles         #
    #  in case there is the need for re_starting the program. Only the coordinates   #
    #  of the first particle (the one used for tracking) are needed. The other       #
    #  coordinates will be updated based on this one.                                #
    #  It has to be commented out for a normal execution.                            #
    ##################################################################################

    # new_center_first_particle = [28.46, 34.93, 50.5] # Get this value from the keep_track_temp.
    # particles[0].set_center(new_center_first_particle)
    # # Update the coordinates of the other particles
    # dx = particles[0].xcenter[-1]-particles[0].xcenter[0]
    # dy = particles[0].ycenter[-1]-particles[0].ycenter[0]
    # dz = particles[0].zcenter[-1]-particles[0].zcenter[0]
    # for i in range(len(particles)-1):
    #    center = [particles[i+1].xcenter[0],particles[i+1].ycenter[0],particles[i+1].zcenter[0]]
    #    center[0] += dx
    #    center[1] += dy
    #    center[2] += dz
    #    particles[i+1].set_center(center)
    # # Update background position
    # center = [background.xcenter[0],background.ycenter[0],background.zcenter[0]]
    # center[0] += dx
    # center[1] += dy
    # center[2] += dz
    # background.set_center(center)
    #/********************************************************************************/#

    exp.number_of_accumulations = 5 # Accumulations of each spectra (for reducing noise in long-exposure images)
    # Wavelengths for the acquisition at different central positions.
    spec_wl = [575, 595] # Minimum and maximum of the central wavelength
    #parameters for the refocusing on the particles
    exp.dims = [1,1,1.5]
    exp.accuracy = [0.1,0.1,0.1]

    # How much time between refocusing
    exp.time_for_refocusing = 1 # In seconds

    # Saving the files
    name = 'spectra_temperature'
    name2 = 'keep_track'
    savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    # Not overwrite
    i=1
    filename = '%s_%s.dat'%(name,i)
    while os.path.exists(savedir+filename) or os.path.exists(savedir+filename+'.temp'):
        i += 1
        filename = '%s_%s.dat' %(name,i)
    print('Data will be saved in %s'%(savedir+filename))
    filename2 = '%s_%s.dat'%(name2,i)
    print('The keep track will be saved in %s'%(savedir+filename2))

    header = 'Time(s),\t Wavelength(nm),\t Central_wavelength(nm),\t Temperature(V),\t Description,\t \
        Pcle,\t Power(uW),\t Counts,\t X(um),\t Y(um),\t Z(um)'

    # For the keep track data
    header2 = 'Time [s], X [um], Y [um], Z [um], Counts, Temp [mV]'


    ## Making header.
    fl = open(savedir+filename+'.temp','a') # Appends to previous files
    fl.write(header)
    fl.write('\n')
    fl.flush()

    ## Making header.
    fll = open(savedir+filename2+'.temp','a') # Appends to previous files
    fll.write(header)
    fll.write('\n')
    fll.flush()
    data2 = np.zeros(6) # For storing tracking
    ##
    t_0 = time.time() # Initial time
    acquire_spectra = True

    input('Press enter when WhiteLight is on and everything is ready')
    while acquire_spectra:
        print('Aquiring WhiteLight data...')
        temp = exp.adw.adc(exp.temp,2)
        print('Starting with temperature %s'%temp)

        #exp.pmeter.wavelength = 532

        for k in range(len(particles)):
            print('-> Particle %s out of %s'%(k+1,len(particles)))
            how = {'type':'fixed',
                    'device':None,
                    'values': 0,
                    'description': 'White light'}

            particles[k] = exp.acquire_spectra(particles[k],how,spec_wl)
            while exp.spec.remaining_data>0:
                fl.write(exp.spec.get_data())
                fl.write('\n')
                fl.flush()
        print('##############################################')
        print('-> Time for backgrounds...')


        dx = particles[0].xcenter[-1]-particles[0].xcenter[0]
        dy = particles[0].ycenter[-1]-particles[0].ycenter[0]
        dz = particles[0].zcenter[-1]-particles[0].zcenter[0]
        center = [background.xcenter[0],background.ycenter[0],background.zcenter[0]]
        center[0] += dx
        center[1] += dy
        center[2] += dz
        background.set_center(center)

        bkg_center = background.get_center()
        bkg_center[2] = particles[-1].get_center()[2] # Gets the Z position of the last particle
        background.set_center(bkg_center)
        exp.acquire_spectra(background,how,spec_wl)
        while exp.spec.remaining_data>0:
            fl.write(exp.spec.get_data())
            fl.write('\n')
            fl.flush()
        print('Done with temperature %s.'%temp)
        print('start to keep track of the particles.')

        keep_track = True
        while keep_track:
            print('Entering iteration %s...'%i)
            particles[0] = exp.keep_track(particles[0])
            temp = exp.adw.adc(exp.temp,2)
            position = particles[0].get_center()
            dd,ii = exp.adw.get_timetrace_static([exp.counter],duration=1,acc=1)
            t = time.time()
            new_data2 = [t,position[0],position[1],position[2],np.sum(dd),temp]
            data2 = np.vstack([data2,new_data2])
            try:
                for item in new_data2:
                    fll.write("%s, " % (item)) ## Appends the most recent data to the temporary file
                fll.write("\n")
                fll.flush()
            except:
                print('Failed saving data at time %s seconds'%(t))

            print('Press q to exit and start acquiring spectra')
            t1 = time.time()
            while time.time()-t1 < 1:
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


    while exp.spec.remaining_data>0:
        fl.write(exp.spec.get_data())
        fl.write('\n')

    fl.flush()
    fl.close()
    fl = open(savedir+filename,'wb') # Erases any previous content
    pickle.dump(exp.spec,fl)
    fl.close()
    fll.flush()
    fll.close()
    np.savetxt(savedir+filename2,data2,delimiter=',',newline='\n',header=header2)
    print('Saving all the experiment information to %s'%(savedir+filename))
    print('Program finish')
