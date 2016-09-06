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
import msvcrt
import serial
from lib.adq_mod import *
from lib.xml2dict import device,variables
from datetime import datetime

from devices.powermeter1830c import PowerMeter1830c as pp


        
if __name__ == '__main__': 
    #initialize the adwin and the devices   
    xcenter = 53.61
    ycenter = 38.92
    zcenter = 50.85
    total_time = 26*3600 # In seconds
    interval = 30
    wavelength = 532 # For the power meter
    
    name = 'stability_test1_26hs_light_on_OD6'
    
    #parameters for the refocusing on the particles
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    center = [xcenter,ycenter,zcenter]
    devs = [xpiezo,ypiezo,zpiezo]
    dims = [0.4,0.4,0.8]
    accuracy = [0.01,0.01,0.05]
    
       
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
    
#    # Prepare the folder in network drive
#    cwd = os.getcwd()
#    savedir2 = 'R:\\monos\\Aquiles\\Data\\' + str(datetime.now().date()) + '\\'
#    if not os.path.exists(savedir2):
#        os.makedirs(savedir2)
#    filename = name
#    while os.path.exists(savedir2+filename+".dat"):
#        filename = '%s_%s' %(name,i)
#        i += 1
#    filename = filename+".dat"
#    print('Data will also be saved in %s'%(savedir2+filename))
    
    #init the Adwin program and also loading the configuration file for the devices
    adw = adq(model='goldII') 
    #adw.proc_num = 9
    counter1 = device('APD 1')
    counter2 = device('APD 2')
    power_meter_analog = device('Power Meter')
    
   
    # inizialize the pmeter
    try:
        pmeter = pp.via_serial(1)
        pmeter.initialize()
        time.sleep(0.5)

        # set the configuration of power meter.
        pmeter.attenuator = True
        time.sleep(0.5)
        pmeter.wavelength = wavelength
        print('Wavelength = '+str(pmeter.wavelength)+' nm')
        time.sleep(0.5)
        print('Units = '+str(pmeter.units))
        pmeter.range = 0 # set auto scale
        print('Range = '+str(pmeter.range))
        time.sleep(0.5)
    except:
        pmeter = 0
        print('Problem with Power Meter')
    
    time.sleep(5)
    try:
        power = pmeter.data*1000000
    except:
        power = 0
            
    data = np.zeros(8)
    header = 'Time [s], X [uM], Y [uM], Z [uM], Power [uW], Counts1[cnt/ms], Counts2[cnt/ms],InstPower[V]' 
    t_ini = time.time()
    print(t_ini)
    new_data = [t_ini,xcenter,ycenter,zcenter,power,0,0,0]
    data[:]=new_data
    
    try:
        for item in new_data:
            file.write("%s, " % (item))
        file.write("\n")
        file.flush()
    except:
        print('Failed saving data at initial time')
    
    i = 0
    t_0 = time.time() # Initial time
    
    keep_track = True
    
    file = open(savedir+filename+'.temp','a') # Erases any previous file
    file.write(header)
    file.write('\n')
    file.flush()
    while (time.time()-t_0 < total_time) and (keep_track):
        print('Entering iteration %s...'%i)
        i+=1
        # Take position
        print('Re-focusing...')
        position = adw.focus_full(counter1,devs,center,dims,accuracy).astype('str')
        center = position.astype('float')
        adw.go_to_position(devs,center)
        # Take power
        try:
            power = pmeter.data*1000000
        except:
            power = 0
        # Take intensity
        print('Taking time trace for intenstiy measurement')
        dd,ii = adw.get_timetrace_static([counter1,counter2,power_meter_analog],duration=1,acc=1)

        t = time.time()-t_0
        print('t='+str(t))
        new_data = [t,position[0],position[1],position[2],power,np.sum(dd[0]),np.sum(dd[1]),np.sum(dd[2])]
        print('New data = '+ str(new_data))
        data = np.vstack([data,new_data])
        try:
            for item in new_data:
                file.write("%s, " % (item))
            file.write("\n")
            file.flush()
        except:
            print('Failed saving data at time %s seconds'%(t))
       
        print('Press q to exit (you have 5 sec)')
        t1 = time.time()
        while time.time()-t1 < 5:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if ord(key) == 113: #113 is ascii for letter q
                    keep_track = False
                    print('Quiting!')
        
        if keep_track:
            print('Waiting for next measurement')
            time.sleep(interval)
        
    file.close()
    try:
        np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
    except:
        print('Problem saving local data')
    
    
    # finalize power meter
    pmeter.finalize()   
    
    