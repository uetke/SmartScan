"""
    test_flipper.py
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

if __name__ == "__main__":
    exp = experiment()

    repeat = True
    while repeat:
        exp.adw.set_digout(3)
        time.sleep(0.1)
        exp.adw.clear_digout(3)
        key = input('Continue?[y/n]')
        if key == 'n':
            repeat = False
