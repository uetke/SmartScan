"""
    calibrate_spectrometer.py
    -------------
    Acquires spectra of the ArHg lamp at different central wavelengths.
    It should be used to calibrate the spectrometer according to the needs of the
    experiment.

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

    # Coordinates of the background
    bkg = [50.,50., 50.]

    background = particle(bkg,'bkg',1)
    exp.number_of_accumulations = 5 # Accumulations of each spectra (for reducing noise in long-exposure images)
    # Wavelengths for the acquisition at different central positions.
    spec_wl = [575, 595] # Minimum and maximum of the central wavelength

    # Saving the files
    name = 'calibration_spectrometer'

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

    input('Press enter when Calibration Light is on and everything is ready')

    print('Aquiring calibration data...')
    how = {'type':'fixed',
            'device':None,
            'values': 0,
            'description': 'White light'}
    exp.acquire_spectra(background,how,spec_wl)
    while exp.spec.remaining_data>0:
        fl.write(exp.spec.get_data())
        fl.write('\n')
        fl.flush()

    fl.flush()
    fl.close()
    fl = open(savedir+filename,'wb') # Erases any previous content
    pickle.dump(exp.spec,fl)
    fl.close()
    print('Saving all the calibration information to %s'%(savedir+filename))
    print('Program finish')
