# Script for acquiring spectra vs intensity of the selected particle

from __future__ import division
import numpy as np
import time
import matplotlib.pyplot as plt
from lib.adq_mod import *
from lib.xml2dict import device,variables
from datetime import datetime
import msvcrt
import sys
import os
from lib.logger import get_all_caller,logger
from devices.powermeter1830c import powermeter1830c as pp

logger=logger(filelevel=20)

cwd = os.getcwd()
savedir = cwd + '\\' + str(datetime.now().date()) + '\\'
#names of the parameters
par=variables('Par')
fpar=variables('FPar')
data=variables('Data')
fifo=variables('Fifo')

def abort(filename):
    logger = logging.getLogger(get_all_caller())
    logger.critical('You quit!')
    header = "type,x-pos,y-pos,z-pos,first scan time" + ",time_%s"*(len(data[0,:])-5) %tuple(range((len(data[0,:])-5)))
    np.savetxt("%s%s_abort.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    logger.info('Aborted file saved as %s%s_abort.txt' %(savedir,filename))
    sys.exit(0)
        
if __name__ == '__main__': 
    #initialize the adwin and the devices   
    name = 'spectra_power'
    savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    
    i=1
    filename = '%s_%s.dat'%(name,i)
    while os.path.exists(savedir+filename):
        i += 1
        filename = '%s_%s.dat' %(name,i)
        
    logger.info('%s\\%s.log' %(savedir,filename))
    print('Data will be saved in %s'%(savedir+filename))
    #init the Adwin programm and also loading the configuration file for the devices
    adw = adq('lib/adbasic/adwin.T99') 
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    counter = device('APD 1')
    aom = device('AOM')
    xcenter = 50.31 #In um
    ycenter = 44.53
    zcenter = 49.45
    devs = [xpiezo,ypiezo,zpiezo]
    #parameters for the refocusing on the particles
    dims = [0.4,0.4,0.8]
    accuracy = [0.05,0.05,0.1]
    center = [xcenter, ycenter, zcenter]
    number_of_spectra = 20
 #   adw.clear_digout(0)
 #   adw.go_to_position([aom],[1])
    
    #Newport Power Meter
    pmeter = pp(0)
    pmeter.initialize()
    pmeter.wavelength = 633
    pmeter.attenuator = True
    pmeter.filter = 'Medium' 
    pmeter.go = True
    pmeter.units = 'Watts' 
    data = np.zeros([number_of_spectra*2,1])
    #print('Spectra taken with long pass filter')
    #pressing = input('Press enter when ready')
    #data = np.zeros([number_of_spectra+1,1])
    #
    # 
    #power_aom = 1.5
    #adw.go_to_position([aom],[power_aom])   
    #adw.set_digout(0)           
    #time.sleep(0.5)    
    #adw.clear_digout(0)
    #time.sleep(1)
    #try:
    #    power = pmeter.data*1000000
    #except:
    #    power = 0
    #while adw.get_digin(1):
    #    if msvcrt.kbhit():
    #        key = msvcrt.getch()
    #        if ord(key) == 113:
    #            abort(filename + '_inter')
    #    time.sleep(0.1)    
    #print('Acquired spectra of particle with %i uW'%(power))
    #data[0]=str(power)
    #
    #pressing = input('Done with particle. Move to shortpass filter and press enter.')
    
    #make spectra with the shortpass
    #for m in range(number_of_spectra):
    #    # Focus on the particle with an average power
    #    power_aom = 1
    #    adw.go_to_position([aom],[power_aom])
    #    center = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
    #    print(center)
    #    center = center.astype('float')
    #    print(center)
    #    # Now take spectra with a variable power
    #    power_aom = 2-m*2/number_of_spectra
    #    adw.go_to_position([aom],[power_aom])   
    #    adw.set_digout(0)           
    #    time.sleep(0.5)    
    #    adw.clear_digout(0)
    #    
    #    while adw.get_digin(1):
    #        if msvcrt.kbhit():
    #            key = msvcrt.getch()
    #            if ord(key) == 113:
    #                 abort(filename + '_inter')
    #        time.sleep(0.1)
    #    try:
    #        power = pmeter.data*1000000 # Power in uW
    #    except:
    #        power = 0
    #    print('Acquired spectra of particle %i with %i uW'%(i,power))
    #    data[m] = (str(power))
    #
    #print('Done with particle. Move to background (1um away from particle).')
    #center[1] = center[1]+1
    #adw.go_to_position(devs,center)
    
    for m in range(number_of_spectra):
        power_aom = 2-m*2/number_of_spectra
        adw.go_to_position([aom],[power_aom])   
        adw.set_digout(0)           
        time.sleep(0.5)    
        adw.clear_digout(0)
        
        while adw.get_digin(1):
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if ord(key) == 113:
                     abort(filename + '_inter')
            time.sleep(0.1)
        try:
            power = pmeter.data*1000000
        except:
            power = 0
        print('Acquired background %i with %i uW'%(i,power))
        data[number_of_spectra+m] = (str(power))
    
    print('Done with Shortpass background.')
    #
    #for m in range(number_of_spectra):
    #    power_aom = 1.5-m*1.5/number_of_spectra
    #    adw.go_to_position([aom],[power_aom])   
    #    adw.set_digout(0)           
    #    time.sleep(0.5)    
    #    adw.clear_digout(0)
    #    
    #    while adw.get_digin(1):
    #        if msvcrt.kbhit():
    #            key = msvcrt.getch()
    #            if ord(key) == 113:
    #                 abort(filename + '_inter')
    #        time.sleep(0.1)
    #    try:
    #        power = pmeter.data*1000000
    #    except:
    #        power = 0
    #    print('Acquired background %i with %i uW'%(i,power))
    #    data[number_of_spectra*3+m] = (str(power))
        
    header = "Power in uW"
    np.savetxt("%s%s" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    logger.info('Final file saved as %s%s' %(savedir,filename))
    logger.info('Finished acquiring several sepctra completed')
    
    print('Program finish')
