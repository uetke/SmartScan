"""
    white_light_spectra.py
    -------------
    Acquires spectra of a particle while varying the temperature in the surrounding medium.

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
    pcle1 = [43.97, 64.81, 43.50]

    #pcle6 = [53.80, 49.32, 47.00]
    #pcle7 = [55.88, 51.63, 47.00]

    # Coordinates of the background
    bkg = [53.44, 47.94, 43.50]

    # Create array of particles
    particles = []
    particles.append(particle(pcle1,pcle,1))

    background = particle(bkg,'bkg',1)
    exp.number_of_accumulations = 1 # Accumulations of each spectra (for reducing noise in long-exposure images)
    # Wavelengths for the acquisition at different central positions.
    spec_wl = [680, 680] # Minimum and maximum of the central wavelength
    #parameters for the refocusing on the particles
    exp.dims = [1,1,1.5]
    exp.accuracy = [0.1,0.1,0.1]

    # How much time between refocusing
    exp.time_for_refocusing = 5*60 # In seconds

    # Saving the files
    name = 'Continuos_spectra_temperature'

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

        for k in range(len(particles)):
            print('-> Particle %s out of %s'%(k+1,len(particles)))
            how = {'type':'fixed',
                    'device':None,
                    'values': 0,
                    'description': 'White light'}

            particles[k] = exp.acquire_spectra(particles[k],how,spec_wl)
            # Update background position
            dx = particles[0].xcenter[-1]-particles[0].xcenter[0]
            dy = particles[0].ycenter[-1]-particles[0].ycenter[0]
            dz = particles[0].zcenter[-1]-particles[0].zcenter[0]
            center = [background.xcenter[0],background.ycenter[0],background.zcenter[0]]
            center[0] += dx
            center[1] += dy
            center[2] += dz
            background.set_center(center)
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

        print('--->Press q to exit and stop acquiring spectra<---')
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
    fl = open(savedir+filename,'wb') # Erases any previous content
    pickle.dump(exp.spec,fl)
    fl.close()
    print('Saving all the experiment information to %s'%(savedir+filename))
    print('Program finish')
