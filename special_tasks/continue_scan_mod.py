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
    while os.path.exists(savedir+filename+"_SP.txt"):
        filename = '%s_%s' %(name,i)
        i += 1
    logger.info('%s\\%s.log' %(savedir,filename))
    print('Data will be saved in %s_SP.txt'%(savedir+filename))
    
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
    number_of_spectra = 15
    
    global data 
    print('Now is time to acquire spectra changing the 633nm intensity\n')
    pressing = input('Please set up the spectrometer and press enter when ready')

    data = np.loadtxt('%s%s_data.txt' %(savedir, name),dtype='bytes',delimiter =',').astype('str')#strange b in front of strings 
    num_particles = sum(data[:,0]=='particle')
    num_background = sum(data[:,0]=='background')    
    
    for i in range(num_particles):
        center = data[i,1:4].astype('float')
        #center[2] = zcenter # Now the center is provided by the data file
        adw.go_to_position(devs,center)
        for m in range(number_of_spectra):
            if m==0: # If it's the first time that is running
                print('Focusing on particle %i'%(i+1))
                adw.go_to_position([aom],[1]) # Go to a reasonable intensity
                data[i,1:4] = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
                
            power_aom = 1.5-m*1./number_of_spectra
            adw.go_to_position([aom],[power_aom])   
            adw.set_digout(0)           
            time.sleep(0.5)    
            adw.clear_digout(0)
            while adw.get_digin(1):
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if ord(key) == 113:
                        abort(filename + '_inter')
                time.sleep(0.1)
            try:
                power = pmeter.data*1000000
            except:
                power = 0
       
            print('Acquired spectra of particle %i with %i uW'%(i,power))
            try:
                data[i,m+4]=str(power)
            except:
                data = np.append(data,np.zeros([len(data),1]).astype('str'),1)
                data[i,m+4]=str(power)
                
            np.savetxt("%s%s_SP.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
            
        print('Done with %s of %s particles' %(i+1, num_particles))
    
    # Make a spectra of the selected backgrounds
    
    print('Taking Spectra of Bakgrounds')
    for i in range(num_background):
        center = np.append(data[i-num_background,1:3].astype('float'),np.mean(data[:num_particles,3].astype('float')))
        adw.go_to_position(devs,center)
        for m in range(number_of_spectra):
            power_aom = 1.25-m*1.25/number_of_spectra
            adw.go_to_position([aom],[power_aom])   
            adw.set_digout(0)           
            time.sleep(0.5)    
            adw.clear_digout(0)
            
            while adw.get_digin(1):
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if ord(key) == 113:
                         abort(filename + '_inter')
                time.sleep(0.1)
            try:
                power = pmeter.data*1000000
            except:
                power = 0
            print('Acquired background %i with %i uW'%(i,power))
            data[i-num_background,m+4]=str(power)  
            
            np.savetxt("%s%s_SP.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
        print('Done with %s of %s backgrounds'%(i,num_background))
    

    np.savetxt("%s%s_SP.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    logger.info('SP file saved as %s%s_SP.txt' %(savedir,filename))
    logger.info('633 SP completed')
    
    print('Done with the SP\n')
    print('Now is time to repeat with the LP filter')
    
    pressing = input('Please set up the spectrometer and press enter when ready')
    print('Data will be saved in %s_LP.txt'%(savedir+filename))
    
    data = np.loadtxt('%s%s_SP.txt' %(savedir, filename),dtype='bytes',delimiter =',').astype('str')#strange b in front of strings 
    num_particles = sum(data[:,0]=='particle')
    num_background = sum(data[:,0]=='background')    
    
    for i in range(num_particles):
        center = data[i,1:4].astype('float')
        adw.go_to_position(devs,center)
        for m in range(number_of_spectra):
            if m==0: # If it's the first time that is running
                print('Focusing on particle %i'%(i+1))
                adw.go_to_position([aom],[1]) # Go to a reasonable intensity
                data[i,1:4] = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
                
            power_aom = 1.25-m*1.25/number_of_spectra
            adw.go_to_position([aom],[power_aom])   
            adw.set_digout(0)           
            time.sleep(0.5)    
            adw.clear_digout(0)
            time.sleep(0.5)
            while adw.get_digin(1):
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if ord(key) == 113:
                        abort(filename + '_inter')
                time.sleep(0.1)
            try:
                power = pmeter.data*1000000
            except:
                power = 0
                
            print('Acquired spectra of particle %i with %i uW'%(i,power))
            try:
                data[i,m+4]=str(power)
            except:
                data = np.append(data,np.zeros([len(data),1]).astype('str'),1)
                data[i,m+4]=str(power)
                
            np.savetxt("%s%s_LP.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
        print('Done with %s of %s particles' %(i+1, num_particles))
    
    # Make a spectra of the selected backgrounds
    
    for i in range(num_background):
        center = np.append(data[i-num_background,1:3].astype('float'),np.mean(data[:num_particles,3].astype('float')))
        adw.go_to_position(devs,center)
        for m in range(number_of_spectra):
            power_aom = 1.25-m*1.25/number_of_spectra
            adw.go_to_position([aom],[power_aom])   
            adw.set_digout(0)           
            time.sleep(0.5)    
            adw.clear_digout(0)
            time.sleep(0.5)
            while adw.get_digin(1):
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if ord(key) == 113:
                         abort(filename + '_inter')
                time.sleep(0.1)
            try:
                power = pmeter.data*1000000
            except:
                power = 0
            print('Acquired background %i with %i uW'%(i,power))
            data[i-num_background,m+4]=str(power)  
            np.savetxt("%s%s_LP.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
        print('Done with %s of %s backgrounds'%(i,num_background))
    

    np.savetxt("%s%s_LP.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    logger.info('LP file saved as %s%s_LP.txt' %(savedir,filename))
    logger.info('633 LP completed')
    
    print('Done with the LP\n')
    print('Now is time to repeat with the 532nm laser')
    pressing = input('Set the spectrometer and filters and press enter when ready')
    
    print('Data will be saved in %s_532.txt'%(savedir+filename))
    data = np.loadtxt('%s%s_LP.txt' %(savedir, filename),dtype='bytes',delimiter =',').astype('str')#strange b in front of strings 
    num_particles = sum(data[:,0]=='particle')
    num_background = sum(data[:,0]=='background')    
    
    for i in range(num_particles):
        center = data[i,1:4].astype('float')
        center[2] = zcenter
        adw.go_to_position(devs,center)
        #data[i,1:4] = adw.focus_full(counter,devs,center,dims,accuracy,rate=1,speed=50)
        time.sleep(0.5) 
        adw.set_digout(0)           
        time.sleep(0.5)    
        adw.clear_digout(0)
        time.sleep(0.5)
        while adw.get_digin(1):
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if ord(key) == 113: #113 is ascii for letter q
                     abort(filename+'_init')
            time.sleep(0.1)
        print('Done with particle %i of %i'%(i+1,num_particles))
        
        np.savetxt("%s%s_532.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    print('532nm particle spectra taken')
    
    #make a spectra of the selected background
    for i in range(num_background):
        center = np.append(data[i-num_background,1:3].astype('float'),np.mean(data[:num_particles,3].astype('float')))
        adw.go_to_position(devs,center)
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
        np.savetxt("%s%s_532.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    
    np.savetxt("%s%s_532.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)   
    logger.info('532 spectra file saved as %s%s_532.txt' %(savedir,filename))
    logger.info('Program finished')  
    print('Program finished')
