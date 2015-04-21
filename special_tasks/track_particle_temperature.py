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
    header = "Time,X,Y,Z,Counts"
    np.savetxt("%s%s" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    sys.exit(0)
        
if __name__ == '__main__': 
    #initialize the adwin and the devices   
    name = 'track_particle_temperature'
    savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    
    i=1
    filename = '%s_%s.dat'%(name,i)
    while os.path.exists(savedir+filename):
        i += 1
        filename = '%s_%s.dat' %(name,i)
        
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
    
    # Initial position of the particle
    xcenter = 74.30 #In um
    ycenter = 46.46
    zcenter = 51.00
	
    timetrace_time = .1 # In seconds
    integration_time = .1 # In seconds

    devs = [xpiezo,ypiezo,zpiezo]
    #parameters for the refocusing on the particles
    dims = [0.2,0.2,0.4]
    accuracy = [0.05,0.05,0.1]
    adw.go_to_position(devs[:3],[xcenter,ycenter,zcenter])
    
    start_time = datetime.now()
    
    data = np.zeros([5,1])
    i = 0
    data[0,0] = 0 # Initial time
    data[1,0] = xcenter
    data[2,0] = ycenter
    data[3,0] = zcenter
    adw.go_to_position(devs,[xcenter,ycenter,zcenter])
    dd,ii = adw.get_timetrace_static([counter],duration=timetrace_time,acc=integration_time)
    data[4,0] = np.sum(dd)
    print('Press q to quit')
    while True:
        center = data[1:4,i]
        data = np.append(data,np.zeros([5,1]),1)
        adw.go_to_position(devs,center)
        i += 1
        data[1:4,i] = adw.focus_full(counter,devs,center,dims,accuracy,rate=1,speed=50,steps=1)
        time_elaps = (datetime.now()-start_time).total_seconds()
        data[0,i] = time_elaps
        dd,ii = adw.get_timetrace_static([counter],duration=timetrace_time,acc=integration_time)
        data[4,i] = np.sum(dd)
        
        while (datetime.now()-start_time).total_seconds()-time_elaps<2:
            print('Press q to quit')
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if ord(key) == 113: #113 is ascii for letter q
                     abort(filename)
    
    header = "Time,X,Y,Z,Counts"
    np.savetxt("%s%s" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)

    
    print('Program finish')
