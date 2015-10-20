""" General class experiment.
    It will be used to make easier experiments programmed in steps.
    Like the refocusing, temperature change spectra.
"""

import numpy as np
import time

from devices import *
from lib.adq_mod import adq
from lib.xml2dict import device,variables
from special_tasks.spectrometer import abort, trigger_spectrometer, client_spectrometer

class experiment():
    """ Defines a general class where all the variables for a possible experiment
        are defined.
    """
    def __init__(self):
        self.adq = adq()
        self.devices = []
        self.variables = []
        self.spec = client_spectrometer()
        self.number_of_accumulations = 0 # Number of identical spectra to be acquired
        self.number_of_spectra = 0  # Number of spectra at different intensities to be acquired. (May be depecrated)

    def acquire_spectra(particle,how,spec_wl):
        """ Function for acquiring spectra of an array of particles. It will try to move the grating of the spectrometer.
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
            ..spec_wl: list with the min and max wavelengths to send to the spectrometer when
                        accumulating
        """"
        # Refocus on the particle
        center = particle.get_center()
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
