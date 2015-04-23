"""
    keep_track.py
    -------------
    Keeps track of the laser intensity, position of the particle, and brightness
    over a defined period of time. 
    AUTHOR: Aquiles Carattino
    EMAIL: carattino@physics.leidenuniv.nl

"""


import os
import numpy as np
import time
from lib.adq_mod import *
from lib.xml2dict import device,variables
from datetime import datetime

from devices.powermeter1830c import powermeter1830c as pp


        
if __name__ == '__main__': 
    #initialize the adwin and the devices   
    xcenter = 56.55
    ycenter = 46.00
    zcenter = 50.00
    total_time = 36000    # In seconds
    wavelength = 633 # For the power meter
    
    name = 'tracking_'
    
    #parameters for the refocusing on the particles
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    center = [xcenter,ycenter,zcenter]
    devs = [xpiezo,ypiezo,zpiezo]
    dims = [1,1,2]
    accuracy = [0.05,0.05,0.1]
    
    ##names of the parameters
    #par=variables('Par')
    #fpar=variables('FPar')
    #data=variables('Data')
    #fifo=variables('Fifo')
    
    # Prepare the folder in local drive
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
    print('Data will be saved in %s'%(savedir+filename))
    
    # Prepare the folder in network drive
    cwd = os.getcwd()
    savedir2 = 'R:\\monos\\Aquiles\\Data' + str(datetime.now().date()) + '\\'
    if not os.path.exists(savedir2):
        os.makedirs(savedir2)
    filename = name
    while os.path.exists(savedir2+filename+".dat"):
        filename = '%s_%s' %(name,i)
        i += 1
    filename = filename+".dat"
    print('Data will also be saved in %s'%(savedir2+filename))
    
    #init the Adwin programm and also loading the configuration file for the devices
    adw = adq() 
    adw.proc_num = 9
    counter = device('APD 1')
    
    #Newport Power Meter
    pmeter = pp(0)
    pmeter.initialize()
    pmeter.wavelength = wavelength
    pmeter.attenuator = True
    pmeter.filter = 'Medium' 
    pmeter.go = True
    pmeter.units = 'Watts' 
    time.sleep(1)
    
    data = np.zeros(6)
    
    header = 'Time [s], X [uM], Y [uM], Z [uM], Power [muW], Counts ' 
    
    i = 0
    t_0 = time.time() # Initial time
    while time.time()-t_0 < total_time:
        print('Entering iteration %s...'%i)
        i+=1
        # Take position
        position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
        center = position.astype('float')
        # Take power
        try:
            power = pmeter.data*1000000
        except:
            power = 0
        # Take intensity
        dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
        
        t = time.time()-t_0
        new_data = [t,position[0],position[1],position[2],power,np.sum(dd)]
        data = np.vstack([data,new_data])
        np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
        np.savetxt("%s%s" %(savedir2,filename),data, fmt='%s', delimiter=",",header=header)
        
     