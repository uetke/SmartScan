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
    xcenter = 47.33
    ycenter = 44.39
    zcenter = 56.31
    total_time = 2*3600 # In seconds
    rhythm = 60
    #wavelength = 532 # For the power meter
    
    name = 'stability_test3'
    
    #parameters for the refocusing on the particles
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    center = center2 = [xcenter,ycenter,zcenter]
    devs = [xpiezo,ypiezo,zpiezo]
    dims = [0.4,0.4,0.8]
    accuracy = [0.02,0.02,0.04]
    
       
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
    adw = adq() 
    #adw.proc_num = 9
    counter1 = device('APD 1')
    lockin = device('Lock-in X')
    # counter2 = device('APD 2')
    # power_meter_analog = device('Power Meter')
    
   
    # # inizialize the pmeter
    # try:
    #     pmeter = pp.via_serial(1)
    #     pmeter.initialize()
    #     time.sleep(0.5)

    #     # set the configuration of power meter.
    #     pmeter.attenuator = True
    #     time.sleep(0.5)
    #     pmeter.wavelength = wavelength
    #     print('Wavelength = '+str(pmeter.wavelength)+' nm')
    #     time.sleep(0.5)
    #     print('Units = '+str(pmeter.units))
    #     pmeter.range = 0 # set auto scale
    #     print('Range = '+str(pmeter.range))
    #     time.sleep(0.5)
    # except:
    #     pmeter = 0
    #     print('Problem with Power Meter')
    
    # time.sleep(5)
    # try:
    #     power = pmeter.data*1000000
    # except:
    #     power = 0
            
    data = np.zeros(9)
    header = 'Time [s], X1 [um], Y1 [um], Z1 [um], X2 [um], Y2 [um], Z2 [um], Counts [cnt/s], Photothermal [V]' 
    # data = np.zeros(5)
    # header = 'Time [s], X [um], Y [um], Z [um], Pump-Probe Signal [V]' 
    t_ini = time.time()
    print(t_ini)
    # new_data = [t_ini,xcenter,ycenter,zcenter, 0]
    new_data = [t_ini,xcenter,ycenter,zcenter, xcenter,ycenter,zcenter, 0, 0]
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
        this_timestamp = time.time()
        print('Entering iteration %s...'%i)
        i+=1
        # Take position
        print('Re-focusing... (1)')
        position = adw.focus_full(counter1,devs,center,dims,accuracy).astype('str')
        center = position.astype('float')
        position2 = adw.focus_full(lockin,devs,center,dims,accuracy).astype('str')
        center2 = position.astype('float')
        adw.go_to_position(devs,center)
        # # Take power
        # try:
        #     power = pmeter.data*1000000
        # except:
        #     power = 0
        # Take intensity
        print('Taking time trace for intenstiy measurement')
        dd,ii = adw.get_timetrace_static([counter1,lockin],duration=1,acc=1)
        sinal_counts_per_s = np.sum(dd[0])
        signal_volts = ((np.average(dd[1]) / 2.**15) - 1.0) * 10

        t = time.time()-t_0
        print('t='+str(t))
        new_data = [t,*position, *position2, sinal_counts_per_s, signal_volts]
        print('New data = '+ str(new_data))
        data = np.vstack([data,new_data])
        try:
            for item in new_data:
                file.write("%s, " % (item))
            file.write("\n")
            file.flush()
        except:
            print('Failed saving data at time %s seconds'%(t))

        # wait until the next point in time
        next_timestamp = this_timestamp + rhythm
       
        print('Press q to exit.')
        while time.time() < next_timestamp:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if ord(key) == 113: #113 is ascii for letter q
                    keep_track = False
                    print('Quitting!')
                    break
            else:
                time.sleep(0.05)
        
    file.close()
    try:
        np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
    except:
        print('Problem saving local data')
    
    
    # finalize power meter
    #pmeter.finalize()   
    
    