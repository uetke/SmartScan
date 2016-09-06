# Simple script for analyzing the polarization dependence of the emission of a single-rod

import numpy as np
import time
import msvcrt
import sys
import os
from lib.adq_mod import *
from datetime import datetime
from lib.logger import get_all_caller,logger
from devices.powermeter1830c import PowerMeter1830c as pp
from winsound import Beep


logger=logger(filelevel=20)

def abort(filename):
    logger = logging.getLogger(get_all_caller())
    logger.critical('You quit!')
    header = "type,x-pos,y-pos,z-pos,first scan time" + ",time_%s"*(len(data[0,:])-5) %tuple(range((len(data[0,:])-5)))
    np.savetxt("%s%s_abort.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    logger.info('Aborted file saved as %s%s_abort.txt' %(savedir,filename))
    sys.exit(0)
        
if __name__ == '__main__': 
    #initialize the adwin and the devices   
    cwd = os.getcwd()
    savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    name = 'PolHeNe'
    i=1
    filename = '%s_%s.dat'%(name,i)
    while os.path.exists(savedir+filename):
        i += 1
        filename = '%s_%s.dat' %(name,i)
        
    logger.info('%s\\%s.log' %(savedir,filename))
    print('Data will be saved in %s'%(savedir+filename))
   
    adw = adq()
    #Newport Power Meter
    pmeter = pp.via_serial(16)
    pmeter.initialize()
    pmeter.wavelength = 633
    pmeter.attenuator = True
    pmeter.filter = 'Medium'
    pmeter.go = True
    pmeter.units = 'Watts'

    print('Trigger to start')
    print('Press q to quit')
    
    powers = []
    while True:       
        if not adw.get_digin(0):
            print('Acquiring Timetrace')
            Beep(840,200)
            
            try:
                power = pmeter.data*1000000
            except:
                power = 0
            print('Measured power %s uW'%power)
            powers.append(power)
            Beep(440,200)
            
        if msvcrt.kbhit(): # <--------
            key = msvcrt.getch()
            if ord(key) == 113:
                break
   
    header = "633 Power as polarization changes in uW"
    np.savetxt("%s%s" %(savedir,filename), powers,fmt='%s', delimiter=",", header=header)   
    print('Data saved in %s%s'%(savedir,filename))