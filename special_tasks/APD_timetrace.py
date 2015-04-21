# Simple script for analyzing the polarization dependence of the emission of a single-rod

from __future__ import division
import numpy as np
import time
import matplotlib.pyplot as plt
from lib.adq_mod import *
from lib.xml2dict import device,variables
from datetime import datetime
from tkinter.filedialog import askopenfilename
import msvcrt
import sys
import os
from lib.logger import get_all_caller,logger
from devices.powermeter1830c import powermeter1830c as pp
from winsound import Beep

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
    name = input('Give the name of the sample: ')
    cwd = os.getcwd()
    savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    i=1
    filename = name
    while os.path.exists(savedir+filename+"APD.txt"):
        filename = '%s_%s' %(name,i)
        i += 1
    filename = filename+"APD.txt"
    logger.info('%s\\%s.log' %(savedir,filename))
    print('Data will be saved in %s'%(savedir+filename))
    #init the Adwin programm and also loading the configuration file for the devices
    adw = adq('lib/adbasic/adwin.T99') 
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    counter = device('APD 1')
    aom = device('AOM')
    adw.go_to_position([aom],[1.5])
    
    #Newport Power Meter
    pmeter = pp(0)
    pmeter.initialize()
    pmeter.wavelength = 633
    pmeter.attenuator = True
    pmeter.filter = 'Medium' 
    pmeter.go = True
    pmeter.units = 'Watts' 
    
    timetrace_time = 1    # In seconds
    integration_time = .00005 # In seconds
    number_elements = int(timetrace_time/integration_time)
    
    data = np.zeros([120,number_elements+1])
    print('Click to start')
    print('Press q to quit')
    i=0
    while True:       
        if not adw.get_digin(0):
            print('Acquiring Timetrace')
            Beep(840,200)
            dd,ii = adw.get_timetrace_static([counter],duration=timetrace_time,acc=integration_time)
            dd = np.array(dd)
            try:
                power = pmeter.data*1000000
            except:
                power = 0
            data[i,0] = power
            data[i,1:] = dd
            i+=1
            Beep(440,200)
            
        if msvcrt.kbhit(): # <--------
            key = msvcrt.getch()
            if ord(key) == 113:
                break
   
    header = "Timetrace of APD"
    np.savetxt("%s%s" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)   
    logger.info('Initial file saved as %s%s_init.txt' %(savedir,filename))
    print('Data saved in %s%s'%(savedir,filename))