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
from devices.powermeter1830c import PowerMeter1830c as pp
from devices.arduino import arduino as ard

class experiment():
    """ Defines a general class where all the variables for a possible experiment
        are defined.
    """
    def __init__(self):
        self.adw = adq()
        self.adw.proc_num = 9
        self.devices = []
        self.variables = []
        self.client_spec = client_spectrometer()
        self.number_of_accumulations = 1 # Number of identical spectra to be acquired
        self.number_of_spectra = 1  # Number of spectra at different intensities to be acquired. (May be depecrated)
        self.counter = device('APD 1')
        self.aom = device('AOM')
        self.laser_min = 500 # In uW
        self.laser_max = 3900 # In uW
        self.laser_powers = np.linspace(self.laser_min,self.laser_max,self.number_of_spectra)
        self.temp = device('Temperature')
        self.wavelength = 0 # Wavelength being used
        self.spec = spectra() # Class for storing the spectra information

        ############################
        # Parameter for refocusing #
        ############################
        self.time_for_refocusing = 5*60 # In seconds
        self.dims = [1,1,1.5]
        self.accuracy = [0.1,0.1,0.1]
        self.xpiezo = device('x piezo')
        self.ypiezo = device('y piezo')
        self.zpiezo = device('z piezo')
        self.devs = [self.xpiezo,self.ypiezo,self.zpiezo]
        self.focusing_power = 1800 # In uW (The power used to refocus on the particles and to keep track during temperature changes)

        ##################################
        # Initialize some other devices  #
        ##################################
        #Newport Power Meter
        try:
            pmeter = pp.via_serial(0)
            pmeter.initialize()
            pmeter.wavelength = 532
            pmeter.attenuator = True
            pmeter.filter = 'Medium'
            pmeter.go = True
            pmeter.units = 'Watts'
            self.pmeter = pmeter
        except:
            self.pmeter = 0
            print('Problem with PMeter')
        # Initialize the Arduino Class
        try:
            arduino = ard('COM9')
        except:
            print('Problem with arduino')




    def acquire_spectra(self,particle,how,spec_wl):
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
        """
        self.center = particle.get_center()
        self.num_pcle = particle.get_id()
        self.descr = particle.get_type()
        if particle.get_type() == 'pcle':
            # Refocus on the particle
            print('\tFocusing')
            position = self.focus_full()
            self.time_last_refocus = time.time()
            self.center = position.astype('float')
            particle.set_center(self.center)
        elif particle.get_type() == 'bkg':
            pass
        else:
            raise Exception('Type of particle not recognized')

        self.adw.go_to_position(self.devs,self.center)
        wavelengths = np.linspace(spec_wl[0],spec_wl[-1],self.number_of_accumulations)
        if how['type'] == 'fixed':
            self.accumulate_spectrometer(particle,wavelengths)

        elif how['type'] == 'variable':
            for m in range(self.number_of_spectra):
                dev = how['device']
                values = how['values']
                self.adw.go_to_position([dev],[values[m]])
                self.accumulate_spectrometer(particle,wavelengths)
        return particle

    def focus_full(self):
        return self.adw.focus_full(self.counter,self.devs,self.center,self.dims,self.accuracy).astype('str')

    def accumulate_spectrometer(self,pcle,wl):
        num_accumulations = len(wl)
        if num_accumulations >= 1:
            for wlength in wl:
                if (time.time()-self.time_last_refocus>=self.time_for_refocusing) and (pcle.get_type() == 'pcle'):
                    position = self.focus_full()
                    self.time_last_refocus = time.time()
                    self.center = position.astype('float')
                    pcle.set_center(self.center)
                    self.adw.go_to_position(self.devs,self.center)

                self.client_spec.goto(wlength)
                trigger_spectrometer(self.adw)

                #####################################
                # Saves the data of each triggering #
                #####################################
                dd,ii = self.adw.get_timetrace_static([self.counter],duration=1,acc=1)
                dd = np.sum(dd)
                t = time.time()
                try:
                    power = self.pmeter.data*1000000
                except:
                    power = 0
                temp = self.adw.adc(self.temp,2)
                values = {'Time': t,
                    'Central_wavelength': wlength,
                    'Temperature': temp,
                    'Description': self.descr,
                    'Pcle': self.num_pcle,
                    'Power': power,
                    'Counts': dd,
                    'X': self.center[0],
                    'Y': self.center[1],
                    'Z': self.center[2]}
                self.spec.update(values)
        else:
            raise Exception('The length of the accumulations is wrong')

    def keep_track(self,particle):
        # Take position
        self.center = particle.get_center() # Use the first particle for refocusing
        position = self.focus_full().astype('str')
        center = position.astype('float')
        self.adw.go_to_position(self.devs,center)
        particle.set_center(center)

        return particle

class particle():
    def __init__(self,coords,tpe,num):
        """ TPE: Means the type. If pcle or bkg. Has to be string.
        """
        self.xcenter = []
        self.ycenter = []
        self.zcenter = []
        self.tcenter = [] # The time at which the center was updated
        self.xcenter.append(coords[0])
        self.ycenter.append(coords[1])
        self.zcenter.append(coords[2])
        self.tcenter.append(time.time())
        self.set_type(tpe)
        self.set_id(num) # Identificator for the particle.



    def get_center(self):
        center = [self.xcenter[-1],self.ycenter[-1],self.zcenter[-1]]
        return center

    def set_center(self,coords):
        self.tcenter.append(time.time())
        self.xcenter.append(coords[0])
        self.ycenter.append(coords[1])
        self.zcenter.append(coords[2])

    def get_type(self):
        return self.tpe

    def set_type(self,tpe):
        self.tpe = tpe
        return self.tpe

    def set_id(self,num):
        self.num = num
        return self.num

    def get_id(self):
        return self.num

class spectra():
    """ Class for storing the information of every spectra taken.
    """
    def __init__(self):
        self.data = {'Time': [], # Time for logbook/spectra taken
            'Wavelength': [], # Of the laser used. 0 for White Light
            'Central_wavelength': [], # The central wavelength set to the spectr.
            'Temperature': [],
            'Description': [],
            'Pcle': [], # Number of the particle observed
            'Power': [], # The power measured by the Power Meter
            'Counts': [], # The counts per second measured by the APD
            'X': [],
            'Y': [],
            'Z': []}
        self.last_index = -1 # Last accessed index
        self.remaining_data = 0 # How many spectra were not downloaded yet

    def update(self,values):
        """ Appends the new values to the Dictionary.
        """
        for k in self.data:
            if k in values:
                self.data[k].append(values[k])
            else:
                try:
                    self.data[k].append(0)
                except:
                    self.data[k].append(None)
        self.remaining_data = len(self.data['Time'])-self.last_index-1

    def get_data(self):
        """ Returns a string of values ready to be stored in file.
        """
        indexes = ['Time','Wavelength','Central_wavelength','Temperature','Description', \
            'Pcle','Power','Counts','X','Y','Z']

        out = ''
        if self.remaining_data > 0:
            self.last_index += 1
            self.remaining_data = len(self.data['Time'])-self.last_index-1
            for i in indexes:
                out = "%s\t%s"%(out,self.data[i][self.last_index])
        else:
            out = ''
        return out
