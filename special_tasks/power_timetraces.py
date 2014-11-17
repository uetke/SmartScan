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
    name = 'power_intensity'
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

    devs = [xpiezo,ypiezo,zpiezo]
    number_of_spectra = 10
    
    #Newport Power Meter
    pmeter = pp(0)
    pmeter.initialize()
    pmeter.wavelength = 633
    pmeter.attenuator = True
    pmeter.filter = 'Medium' 
    pmeter.go = True
    pmeter.units = 'Watts' 
    
    timetrace_time = 2 # In seconds
    integration_time = .01 # In seconds
    number_elements = int(timetrace_time/integration_time)
    
    data = np.zeros([number_of_spectra,number_elements+1]) # The first element will be the power

    for m in range(number_of_spectra):
        power_aom = 1.5-m*1.5/number_of_spectra
        adw.go_to_position([aom],[power_aom])   
        dd,ii = adw.get_timetrace_static([counter],duration=timetrace_time,acc=integration_time)
        if m==0:
            time.sleep(1)
        try:
            power = pmeter.data*1000000
        except:
            power = 0
        data[m,0] = (str(power))
        data[m,1:] = np.array(dd)
        print('Power %s uW'%(str(power)))
        print('Done with %i'%(m))
        

        
    header = "(Power in uW,timetrace) integration time: %f seconds"%(integration_time)
    np.savetxt("%s%s" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    logger.info('Final file saved as %s%s' %(savedir,filename))
    logger.info('Finished acquiring several sepctra completed')
    
    print('Program finish')
