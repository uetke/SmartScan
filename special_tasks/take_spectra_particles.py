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
    logger.info('Aborted file saved as %s%s_abort.txt' %(savedir,filename))
    sys.exit(0)
    
def trigger_spectrometer(adq,in_port=0,out_port=1):
    """Triggers the spectrometer by sending a TTL signal and waits until it finishes. 
    
    Arguments:
    adq -- an acquisition class. Usually the ADwin box.
    in_port -- (integer) the digital port where the spectrometer is connected
    out_port -- (integer) the digital port where the spectrometer output is connected
    """
    
    in_port = int(in_port)
    out_port = int(out_port)
    
    time.sleep(0.5) 
    adw.set_digout(0)           
    time.sleep(0.5)    
    adw.clear_digout(0)
    while adw.get_digin(1):
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if ord(key) == 113: #113 is ascii for letter q
                 abort(filename+'_init')
        time.sleep(0.1)
    return True
    
        
if __name__ == '__main__': 
    #Initialize the logger:
    logger = logging.getLogger(get_all_caller())
    header = "type,x-pos,y-pos,z-pos, intensity"
    
    #initialize the adwin and the devices   
    name = input('Give the name of the File to process without extension: ')
    wavelength = int(input('What wavelength are you using? (in nm): '))
    cwd = os.getcwd()
    savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    
    filename = name
    
    i=1
    while os.path.exists(savedir+filename+"_data.txt"):
        filename = '%s_%s' %(name,i)
        i += 1
        
    logger.info('%s\\%s.log' %(savedir,filename))
    print('Data will be saved in %s%s_data.txt'%(savedir,filename))
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
    pmeter.wavelength = wavelength
    pmeter.attenuator = True
    pmeter.filter = 'Medium' 
    pmeter.go = True
    pmeter.units = 'Watts' 
    
    #making a 2d scan of the sample and trying to find particles
    xcenter = 50.0 #In um
    ycenter = 50.0
    zcenter = float(input('Enter Z value for the scan provided: \n'))
    xdim = 30    #In um
    ydim = 30
    xacc = 0.15   #In um
    yacc = 0.15
    devs = [xpiezo,ypiezo,zpiezo]
    #parameters for the refocusing on the particles
    dims = [0.3,0.3,0.3]
    accuracy = [0.05,0.05,0.1]
    adw.go_to_position(devs[:3],[xcenter,ycenter,zcenter])

    
    global data 
    print('Now is time to acquire spectra with the %i nm laser\n'%(wavelength))
    pressing = input('Please set up the spectrometer and press enter when ready')

    data = np.loadtxt('%s%s_good.txt' %(savedir, name),dtype='bytes',delimiter =',').astype('str')#strange b in front of strings 
    num_particles = sum(data[:,0]=='particle')
    num_background = sum(data[:,0]=='background')    
    
    start_time = time.time()
    for i in range(num_particles):
        center = data[i,1:4].astype('float')
        center[2] = zcenter
        adw.go_to_position(devs,center)
        print('Focusing on particle %i ...'%(i+1))
        data[i,1:4] = adw.focus_full(counter,devs,center,dims,accuracy,rate=1,speed=50,steps=3)
        np.savetxt("%s%s_data.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header) # Saves for checking while running
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
            
        try:
            power = pmeter.data*1000000
        except:
            power = 0
        try:
            data[i,4]=str(power)
        except:
            data = np.append(data,np.zeros([len(data),1]).astype('str'),1)
            data[i,4]=str(power)
        print('Acquired spectra of particle %i with %i uW'%(i+1,power))
        print('Ellapsed time: %i minutes'%(int((time.time()-start_time)/60)))
        logger.info('Particle %i finished with intensity: %i uW'%(i+1,power))
        
    logger.info('Particles Finished')  
    print('532nm particle spectra taken')
    print('Now is time to acquire the backgrpunds')
    
    #make a spectra of the selected background
    for i in range(num_background):
        center = np.append(data[i-num_background,1:3].astype('float'),np.mean(data[:num_particles,3].astype('float')))
        adw.go_to_position(devs,center)
        adw.set_digout(0)
        time.sleep(0.5)    
        adw.clear_digout(0)
        time.sleep(0.5)
        while adw.get_digin(1):
            if msvcrt.kbhit(): # <--------
                key = msvcrt.getch()
                if ord(key) == 113:
                     abort(filename+'_init')
            time.sleep(0.1)
        print('Done with background %i of %i'%(i+1,num_background))
        
    
    header = "type,x-pos,y-pos,z-pos, intensity"
    np.savetxt("%s%s_data.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)   
    logger.info('532 spectra file saved as %s%s_532.txt' %(savedir,filename))
    logger.info('Program finished')  
    print('Program finished')
