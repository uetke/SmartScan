# Simple script for analyzing the polarization dependence of the emission of a single-rod

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
from winsound import Beep

logger=logger(filelevel=20)

        
if __name__ == '__main__': 
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
    #init the Adwin programm and also loading the configuration file for the devices
    adw = adq() 
    counter = device('APD 1')
    counter2 = device('APD 2')
       
    timetrace_time = 0.5 # In seconds
    integration_time = .01 # In seconds
    number_elements = int(timetrace_time/integration_time)
    
    data = np.zeros([38,number_elements])
    print('Click to start')
    print('Press q to quit')
    i=0
    while True:       
        if not adw.get_digin(0):
            print('Acquiring Timetrace')
            Beep(840,200)
            dd,ii = adw.get_timetrace_static([counter],duration=timetrace_time,acc=integration_time)
            dd = np.array(dd)
            ddd,ii = adw.get_timetrace_static([counter2],duration=timetrace_time,acc=integration_time)
            ddd = np.array(ddd)
            data[2*i,:] = dd
            data[2*i+1,:] = ddd
            i+=1
            Beep(440,200)
            
        if msvcrt.kbhit(): # <--------
            key = msvcrt.getch()
            if ord(key) == 113:
                break
   
    header = "Counts as polarization changes"
    np.savetxt("%s%s" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)   
    logger.info('Initial file saved as %s%s_init.txt' %(savedir,filename))
    print('Data saved in %s%s'%(savedir,filename))