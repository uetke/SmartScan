# -*- coding: utf-8 -*-
"""
    Acquires spectra of the defined coordinates after refocusing on them.
    It is wise to run intermediate_scan_mod before running this script.
"""

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
from devices.flipper import Flipper
from start import adding_to_path
from spectrometer import abort, trigger_spectrometer

adding_to_path('lib')
logger=logger(filelevel=30)

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
    logger.critical('Aborted file saved as %s%s_abort.txt' %(savedir,filename))
    sys.exit(0)

if __name__ == '__main__':

    #init the Adwin programm and also loading the configuration file for the devices
    adw = adq()
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    counter = device('APD 1')


    #print('The file to read will be name+_data.txt. Please verify that it exists\n')
    name = 'S190917_good'
    cwd = os.getcwd()
    savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    filename = name
    i=1
    while os.path.exists(savedir+filename+"_532.txt"):
        filename = '%s_%s' %(name,i)
        i += 1
    logger.info('%s\\%s.log' %(savedir,filename))
    print('Data will be saved in %s_532.txt'%(savedir+filename))

    xcenter = 50.0 #In um
    ycenter = 50.0
    zcenter = 48.65
    xdim = 30    #In um
    ydim = 30
    xacc = 0.15   #In um
    yacc = 0.15
    devs = [xpiezo,ypiezo,zpiezo]
    #parameters for the refocusing on the particles
    dims = [1,1,1]
    accuracy = [0.05,0.05,0.1]

    adw.go_to_position(devs[:3],[xcenter,ycenter,zcenter])
    header = "type,x-pos,y-pos,z-pos"
    try:
        flipper = Flipper(b'37863355')
        flipper_apd = 1 # Position going to the APD
        flipper_spec = 2 # Position going to the spectrometer
        flip = True
    except:
        print('Problem initializing the flipper mirror')
        flip = False

    global data
    print('Now is time to acquire 532nm Spectra\n')
    pressing = input('Please set up the spectrometer and press enter when ready')

    data = np.loadtxt('%s%s.txt' %(savedir, name),dtype='bytes',delimiter =',').astype('str')#strange b in front of strings
    num_particles = sum(data[:,0]=='particle')
    num_background = sum(data[:,0]=='background')

    for i in range(num_particles):
        center = data[i,1:4].astype('float')
        center[2] = zcenter # Now the center is provided by the data file
        adw.go_to_position(devs,center)

        if flip:
            if flipper_apd != flipper.getPos():
                flipper.goto(flipper_apd)
        position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
        center = position.astype('float')
        adw.go_to_position(devs,center)
        data[i,1:4] = center

        if flip:
            if flipper_spec != flipper.getPos():
                flipper.goto(flipper_spec)
                time.sleep(0.5)
        trigger_spectrometer(adw)

        np.savetxt("%s%s_532.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)

        print('Done with %s of %s particles' %(i+1, num_particles))

    # Make a spectra of the selected backgrounds

    print('Taking Spectra of Bakgrounds')
    for i in range(num_background):
        center = np.append(data[i-num_background,1:3].astype('float'),np.mean(data[:num_particles,3].astype('float')))
        data[i-num_background,1:4] = center
        adw.go_to_position(devs,center)
        if flip:
            if flipper_spec != flipper.getPos():
                flipper.goto(flipper_spec)
                time.sleep(0.5)
        trigger_spectrometer(adw)

        np.savetxt("%s%s_532.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
        print('Done with %s of %s backgrounds'%(i,num_background))


    np.savetxt("%s%s_532.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    logger.info('532 file saved as %s%s_532.txt' %(savedir,filename))
    logger.info('532 completed')

    print('Done with the White Light\n')
    print('Program finished')
