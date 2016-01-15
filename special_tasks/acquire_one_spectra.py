"""
    acquire_one_spectra.py
    -------------
    Acquires one spectra, moving the grating if needed, but without changing the
    piezo position.

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
    exp.number_of_accumulations = 5 # Accumulations of each spectra (for reducing noise in long-exposure images)
    # Wavelengths for the acquisition at different central positions.
    spec_wl = [670, 690] # Minimum and maximum of the central wavelength
    how = {'type':'fixed',
            'device':None,
            'values': 0,
            'description': 'White light'}
    exp.fixed_spectra(how,spec_wl)
    print('Finished with the spectra')
