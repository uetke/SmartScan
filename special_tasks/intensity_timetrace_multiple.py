# Script for acquiring timetraces of different particles at varying intensities 

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
from start import adding_to_path

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
    adw = adq('lib/adbasic/adwin.T99') 
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    counter = device('APD 1')
    aom = device('AOM')
    adw.go_to_position([aom],[1.25])
    
    
    #Newport Power Meter
    pmeter = pp(0)
    pmeter.initialize()
    pmeter.wavelength = 633
    pmeter.attenuator = True
    pmeter.filter = 'Medium' 
    pmeter.go = True
    pmeter.units = 'Watts' 
    
    print('The file to read will be name+_data.txt. Please verify that it exists\n')
    name = input('Give the name of the File to process without extension: ')
    cwd = os.getcwd()
    savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    filename = name    
    i=1
    while os.path.exists(savedir+filename+"%_timetraces.txt"):
        filename = '%s_%s' %(name,i)
        i += 1
    logger.info('%s\\%s.log' %(savedir,filename))
    print('Data will be saved in %s_timetraces.txt'%(savedir+filename))
    
    xcenter = 50.0 #In um
    ycenter = 50.0
    zcenter = 50.0
    xdim = 30    #In um
    ydim = 30
    xacc = 0.15   #In um
    yacc = 0.15
    devs = [xpiezo,ypiezo,zpiezo]
    #parameters for the refocusing on the particles
    dims = [0.3,0.3,0.3]
    accuracy = [0.05,0.05,0.1]
    
    adw.go_to_position(devs[:3],[xcenter,ycenter,zcenter])
    header = "type,x-pos,y-pos,z-pos,laser power..."
    
    #Number of spectra to take on each particle
    number_of_timetraces = 20
    timetrace_time = 2 # In seconds
    integration_time = .01 # In seconds
    
    number_elements = int(timetrace_time/integration_time)
    global data 
    print('Now is time to acquire timetraces changing the 633nm intensity\n')

    data = np.loadtxt('%s%s_data.txt' %(savedir, name),dtype='bytes',delimiter =',').astype('str')#strange b in front of strings 
    num_particles = sum(data[:,0]=='particle')
    num_background = sum(data[:,0]=='background')    
    
    powers = np.zeros([num_particles+num_background,number_of_timetraces])
    
    for i in range(num_particles):
        center = data[i,1:4].astype('float')
        #center[2] = zcenter # Now the center is provided by the data file
        adw.go_to_position(devs,center)
        for m in range(number_of_timetraces):
            if m==0: # If it's the first time that is running
                print('Focusing on particle %i'%(i+1))
                adw.go_to_position([aom],[1]) # Go to a reasonable intensity
                data[i,1:4] = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
                
            power_aom = 1.5-m*1./number_of_timetraces
            adw.go_to_position([aom],[power_aom])   
            dd,ii = adw.get_timetrace_static([counter],duration=timetrace_time,acc=integration_time)
            if m==0:
                time.sleep(1)
            try:
                power = pmeter.data*1000000
            except:
                power = 0
           
            print('Power %s uW'%(str(power)))

            try:
                data[i,m+4]=np.sum(dd)
            except:
                data = np.append(data,np.zeros([len(data),1]).astype('str'),1)
                data[i,m+4]=np.sum(dd)
            powers[i,m] = power
            
        print('Done with %s of %s particles' %(i+1, num_particles))
    
    # Make a spectra of the selected backgrounds
    
    print('Going to Bakgrounds')
    for i in range(num_background):
        center = np.append(data[i-num_background,1:3].astype('float'),np.mean(data[:num_particles,3].astype('float')))
        adw.go_to_position(devs,center)
        for m in range(number_of_timetraces):
            power_aom = 1.25-m*1.25/number_of_timetraces
            adw.go_to_position([aom],[power_aom])   
            
            dd,ii = adw.get_timetrace_static([counter],duration=timetrace_time,acc=integration_time)
            try:
                power = pmeter.data*1000000
            except:
                power = 0
            print('Acquired background %i with %i uW'%(i,power))
            data[i-num_background,m+4]=np.sum(dd) 
            powers[i-num_background,m] = power

        print('Done with %s of %s backgrounds'%(i+1,num_background))
    

    np.savetxt("%s%s_timetraces.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    np.savetxt("%s%s_powers.txt" %(savedir,filename), power,fmt='%s', delimiter=",", header=header)
    
    print('Done')