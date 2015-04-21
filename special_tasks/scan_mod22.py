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
    filename = input('Give the name of the sample: ')
    cwd = os.getcwd()
    savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
    
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
    
    #making a 2d scan of the sample and trying to find particles
    xcenter = 50.0 #In um
    ycenter = 50.0
    zcenter = 49.0
    xdim = 20    #In um
    ydim = 20
    xacc = 0.2   #In um
    yacc = 0.2
    devs = [xpiezo,ypiezo,zpiezo]
    #parameters for the refocusing on the particles
    dims = [0.4,0.4,0.8]
    accuracy = [0.05,0.05,0.1]
    adw.go_to_position(devs[:3],[xcenter,ycenter,zcenter])
    
    #Number of spectra to take on each particle
    number_of_spectra = 20
    

    data = np.loadtxt('%s%s_init.txt' %(savedir, filename),dtype='bytes',delimiter =',').astype('str')#strange b in front of strings 
    num_particles = sum(data[:,0]=='particle')
    num_background = sum(data[:,0]=='background')
    
   
    print('Now is time to take spectra with the 532')
    pressing = input('Enter when ready')
    
    pmeter.wavelength = 532

    for i in range(num_particles):
        center = data[i,1:4].astype('float')
        center[2] = zcenter
        adw.go_to_position(devs,center)
        data[i,1:4] = adw.focus_full(counter,devs,center,dims,accuracy,rate=1,speed=50)
        adw.set_digout(0)           
        time.sleep(0.5)    
        adw.clear_digout(0)
        while adw.get_digin(1):
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if ord(key) == 113: #113 is ascii for letter q
                     abort(filename+'_init')
            time.sleep(0.1)
        print('Done with particle %i of %i'%(i+1,num_particles))
    print('532nm spectra taken')
    
    #make a spectra of the selected background
    for i in range(num_background):
        center = np.append(data[i-num_background,1:4],np.mean(data[:num_particles,3].astype('float')))
        adw.go_to_position(devs,center)
        data[i-num_background,3]=str(np.mean(data[:num_particles,3].astype('float')))
        data[i-num_background,4]=str(datetime.now().time())
        adw.set_digout(0)
        time.sleep(0.5)    
        adw.clear_digout(0)
        while adw.get_digin(1):
            if msvcrt.kbhit(): # <--------
                key = msvcrt.getch()
                if ord(key) == 113:
                     abort(filename+'_init')
            time.sleep(0.1)
        print('Done with background %i of %i'%(i+1,num_background))
    print('Done with backgrounds with the 532')
    print('Done with the 532')

    
    
    print('Program finish')
