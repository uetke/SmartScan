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
from time import sleep
logger=logger(filelevel=20)

cwd = os.getcwd()
savedir = cwd + '\\' + str(datetime.now().date()) + '\\'



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
    print('For quiting press q')
    if not os.path.exists(savedir):
        os.makedirs(savedir)

    print('Data will be saved in %s'%(savedir))
    #init the Adwin programm and also loading the configuration file for the devices
    adw = adq() 
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    counter = device('APD 1')
    aom = device('AOM')
    pmeter = pp(0)
    pmeter.initialize()
    pmeter.wavelength = 532
    pmeter.attenuator = True
    
    data = []
    aom_data = []
    adw.go_to_position([aom],[1.25])
    plt.ion()
    for i in range(20):
        power_aom = 2.5-i*2.5/20
        adw.go_to_position([aom],[power_aom])
        sleep(2)
        data.append(pmeter.data*1000000)
        print('Power meter: %i uW'%(pmeter.data*1000000))
        print('AOM: %f'%(power_aom))
        aom_data.append(power_aom)
        
        plt.plot(np.array(aom_data),np.array(data))

        sleep(.1)
        
    np.savetxt("%s\\aom_calibration.txt" %(savedir), data,fmt='%s', delimiter=",")
    np.savetxt("%s\\aom_calibration2.txt" %(savedir), aom_data,fmt='%s', delimiter=",")
    pmeter.finalize()
    plt.show()