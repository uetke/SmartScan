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
    pcle1 = [41.38, 44.32, 52.40]
    pcle2 = [58.13, 41.74, 52.10]
    pcle3 = [41.90, 48.76, 52.20]
    #pcle4 = [45.85, 53.86, 49.00]
    #pcle5 = [52.97, 55.28, 49.00]
    #pcle6 = [53.80, 49.32, 49.00]
    #pcle7 = [55.88, 51.63, 49.00]

    # Coordinates of the background
    bkg = [48.91, 49.15, 52.40]

    # Create array of particles
    particles = []
    particles.append(particle(pcle1,pcle,1))
    particles.append(particle(pcle2,pcle,2))
    particles.append(particle(pcle3,pcle,3))
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
    background = particle(bkg,'bkg',1)
    exp.number_of_accumulations = 3 # Accumulations of each spectra (for reducing noise in long-exposure images)
    # Wavelengths for the acquisition at different central positions.
    spec_wl = [600, 610] # Minimum and maximum of the central wavelength
    #parameters for the refocusing on the particles
    exp.dims = [1,1,1.5]
    exp.accuracy = [0.1,0.1,0.1]

    # How much time between refocusing
    exp.time_for_refocusing = 5*60 # In seconds

    # Saving the files
    name = 'spectra_temperature'

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

    header = 'Time(s),\t Wavelength(nm),\t Central_wavelength(nm),\t Temperature(V),\t Description,\t \
        Pcle,\t Power(uW),\t Counts,\t X(um),\t Y(um),\t Z(um)'

    ## Making header.
    fl = open(savedir+filename+'.temp','a') # Appends to previous files
    fl.write(header)
    fl.write('\n')
    fl.flush()
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
        bkg_center = background.get_center()
        bkg_center[2] = particles[-1].get_center()[2] # Gets the Z position of the last particle
        background.set_center(bkg_center)
        exp.acquire_spectra(background,how,spec_wl)
        while exp.spec.remaining_data>0:
            fl.write(exp.spec.get_data())
            fl.write('\n')
            fl.flush()
        print('Done with temperature %s.'%temp)

        print('--->Press q to exit and start acquiring spectra<---')
        t1 = time.time()
        while time.time()-t1 < 2:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if ord(key) == 113: #113 is ascii for letter q
                    acquire_spectra = False
                    break

    while exp.spec.remaining_data>0:
        fl.write(exp.spec.get_data())
        fl.write('\n')

    fl.flush()
    fl.close()
    fl = open(savedir+filename,'w') # Erases any previous content
    pickle.dumps(exp.spec.data,fl)
    fl.close()
    print('Program finish')
