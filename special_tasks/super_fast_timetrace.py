# Acquire a timetrace with an APD with the shortest possible acquisition time.

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

        
if __name__ == '__main__': 
    #initialize the adwin and the devices   
    name = 'super_fast_timetrace'
    cwd = os.getcwd()
    savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    i=1
    filename = name
    while os.path.exists(savedir+filename+".dat"):
        filename = '%s_%s' %(name,i)
        i += 1
    filename = filename+".dat"
    logger.info('%s\\%s.log' %(savedir,filename))
    print('Data will be saved in %s'%(savedir+filename))
    #init the Adwin programm and also loading the configuration file for the devices
    adw = adq() 
    adw.load('lib/adbasic/fast_timetrace.T98')
    counter = device('APD 1')
    
    timetrace_time = 3    # In seconds
    integration_time = .001 # In seconds
    number_elements = int(timetrace_time/integration_time)
    data = np.zeros([1,number_elements+1])
   
    print('Acquiring Timetrace')
    dd = adw.get_fast_timetrace(counter,duration=timetrace_time,acc=integration_time)
    dd = np.array(dd)
    data = dd
   
    header = "Fast Timetrace of APD"
    np.savetxt("%s%s" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)   
    logger.info('Initial file saved as %s%s_init.txt' %(savedir,filename))
    print('Data saved in %s%s'%(savedir,filename))