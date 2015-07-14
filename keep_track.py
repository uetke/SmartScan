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

from devices.powermeter1830c import powermeter1830c as pp
from devices.arduino import arduino as ard

        
if __name__ == '__main__': 
    #initialize the adwin and the devices   
    xcenter = 52.45
    ycenter = 48.49
    zcenter = 50.40
    total_time = 360000    # In seconds
    wavelength = 532 # For the power meter
    
    name = 'tracking_'
    
    #parameters for the refocusing on the particles
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    center = [xcenter,ycenter,zcenter]
    devs = [xpiezo,ypiezo,zpiezo]
    dims = [0.4,0.4,0.8]
    accuracy = [0.05,0.05,0.1]
    
    #Initialize the Arduino
    arduino = ard('COM9')
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
    
    data = np.zeros(9)
    
    header = 'Time [s], X [uM], Y [uM], Z [uM], Power [mW], Counts, Inside Temp, Room Temp [C], Humidity [%]' 
    
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
        position = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
        center = position.astype('float')
        adw.go_to_position(devs,center)
        # Take power
        try:
            power = pmeter.data*1000000
        except:
            power = 0
        # Take intensity
        dd,ii = adw.get_timetrace_static([counter],duration=1,acc=1)
        
        # Humidity
        humidity = arduino.get_room_humidity()
        
        # Room Temp
        room_temp = arduino.get_room_temp()
        
        # Flowcell Temp
        flowcell_temp = arduino.get_flowcell_temp()
            
        t = time.time()-t_0

        new_data = [t,position[0],position[1],position[2],power,np.sum(dd),flowcell_temp,room_temp,humidity]
        data = np.vstack([data,new_data])
        try:
            for item in new_data:
                file.write("%s, " % (item))
            file.write("\n")
            file.flush()
        except:
            print('Failed saving data at time %s seconds'%(t))
       
        print('Press q to exit')
        t1 = time.time()
        while time.time()-t1 < 5:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if ord(key) == 113: #113 is ascii for letter q
                    keep_track = False
    
    file.close()
    try:
        np.savetxt("%s%s" %(savedir,filename),data, fmt='%s', delimiter=",",header=header)
    except:
        print('Problem saving local data')
    arduino.close() 