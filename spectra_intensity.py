# Script for acquiring spectra vs intensity of the selected particle

from __future__ import division
import numpy as np
import time
import msvcrt
import sys
import os
from datetime import datetime
from spectrometer import abort, trigger_spectrometer

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


        
if __name__ == '__main__': 
    # Names of the parameters
#    config_variables = '../config/config_variables.xml'
#    par=variables('Par',filename=config_variables)
#    fpar=variables('FPar',filename=config_variables)
#    data=variables('Data',filename=config_variables)
#    fifo=variables('Fifo',filename=config_variables)
    
    # Name that the files will have
    name = 'spectra_intensity' 
    
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

    print('Data will be saved in %s'%(savedir+filename))
    #init the Adwin program and also load the configuration file for the devices
    adw = adq() 
    counter = device('APD 1')
    aom = device('AOM')

    number_of_spectra = 10
    
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    
    xcenter = 52.09 #In um
    ycenter = 53.24
    zcenter = 48.20
    devs = [xpiezo,ypiezo,zpiezo]
    center = [xcenter, ycenter, zcenter]
    #parameters for the refocusing on the particles
    dims = [0.3,0.3,0.3]
    accuracy = [0.05,0.05,0.1]
    #Newport Power Meter
    pmeter = pp(0)
    pmeter.initialize()
    pmeter.wavelength = 532
    pmeter.attenuator = True
    pmeter.filter = 'Medium' 
    pmeter.go = True
    pmeter.units = 'Watts' 
    data = np.zeros([number_of_spectra,1])
    
    for m in range(number_of_spectra):
    
        adw.go_to_position([aom],[1]) # Go to a reasonable intensity
        
        center = adw.focus_full(counter,devs,center,dims,accuracy).astype('float')
        
        power_aom = m*1.5/number_of_spectra
        adw.go_to_position([aom],[power_aom])
        # Triggers the spectrometer
        trigger_spectrometer(adw)

        try:
            power = pmeter.data*1000000
        except:
            power = 0

        print('Acquired spectra %i with %i uW'%(m+1,power))

        data[m] = (str(power))
        time.sleep(1)
    
    print('Done acquiring spectra.')

    header = "Power in uW"
    np.savetxt("%s%s" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    
    print('Program finish')
