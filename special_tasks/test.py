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
    number_of_spectra = 10
 #   adw.clear_digout(0)
 #   adw.go_to_position([aom],[1])

    
    while True:
    #    if msvcrt.kbhit():
    #        key = msvcrt.getch()
    #        if ord(key) == 113:
    #             abort(filename + '_inter')
        time.sleep(0.05)
        print('%i  |  %i' %(adw.get_digin(1),adw.get_digin(2)))
    

