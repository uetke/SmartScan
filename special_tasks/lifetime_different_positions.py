# Script for taking lifetime on  top of plces without refocusing.
#
# 
#
######################### M. Caldarola - May 2016
# import 
from __future__ import division
import numpy as np
from time import sleep
#import matplotlib.pyplot as plt
from math import floor
from lib.adq_mod import *
from lib.xml2dict import device,variables
from datetime import datetime
import msvcrt
import sys
import os
from lib.logger import get_all_caller,logger
from devices.powermeter1830c import PowerMeter1830c as pp


######## 'Debug this program befor using.'

plt.ion() # enables interactive plot to show big numbers.

########################################################## Here is the info to be filled in before starting
experiment_label = 'Lifetime_PMMA_film_EuComplex_1mM_740nm'


# particle positions
pcle_filename = 'D:\\Data\\2016-06-21\\S1606_18_PMMA_fim_EuComplex_1mM_positions.txt' # filename with the pcle positions and global bkg.
Zplane = '48.47' # z position of the focus [um]
pcle_data = np.loadtxt(pcle_filename,dtype='bytes',delimiter =',').astype('str')#strange b in front of strings 
num_particles = sum(pcle_data[:,0]=='particle')
num_background = sum(pcle_data[:,0]=='background')    
# we biuld a list of positions, even number for pcles and odd number for bkg positions (zero based) 
# and we call this structure Pos.
# It has all the x,y,z positions were the program has to go and take timetraces and spectra
Pos = [0]*num_particles*2
for i in range(num_particles):
    Pos[2*i] = pcle_data[i][1:3]
    Pos[2*i] = list(map(float,[Pos[2*i][0],Pos[2*i][1],Zplane]))
    Pos[2*i+1] = pcle_data[num_particles+i][1:3]
    Pos[2*i+1] = list(map(float,[Pos[2*i+1][0],Pos[2*i+1][1],Zplane]))

## power dependence definitions.
Laser_wavelength = 740 # nm


## define parameters for lifetime measurement
integration_time = 10E-6+10E-6*2*n # secs
detection_time=2E-3                 # detection time [sec]
on_time=1E-3                        # sec
duration = detection_time+on_time   # One run experiment time length [sec]
times=500             # number of times 

###########################################################

# starting

# inizialize
# generate saving path
savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
t = datetime.now().strftime('%Hhs%Mm')

if not os.path.exists(savedir):
    os.makedirs(savedir)
print('Save directory: ' + savedir)

# inizialize the pmeter
try:
    pmeter = pp.via_serial(1)
    pmeter.initialize()
    time.sleep(0.5)

    # set the configuration of power meter.
    pmeter.attenuator = True
    time.sleep(0.5)
    pmeter.wavelength = Laser_wavelength
    print('Wavelength = '+str(pmeter.wavelength)+' nm')
    time.sleep(0.5)
    print('Units = '+str(pmeter.units))
    pmeter.range = 0 # set auto scale
    print('Range = '+str(pmeter.range))
    time.sleep(0.5)
except:
    self.pmeter = 0
    print('Problem with Power Meter')


# inizialize adwin
adw = adq(model='goldII')
xpiezo = device('x piezo')
ypiezo = device('y piezo')
zpiezo = device('z piezo')
devs = [xpiezo,ypiezo,zpiezo]
apd1 = device('APD 1')
apd2 = device('APD 2')
aom = device('AOM Ti:Sa')
adw.load('lib/adbasic/lifetime.TB1')

# inizialize the vectors needed
pw =np.zeros((2*num_particles,N)) # power at bfp

## start measuring
input('############### Do not forget to stopp porcesses in the adwin...')
input('close the shutter for the laser and press enter to take an initial time trace of dark counts')

print('taking dark time trace')
print("integration_time= %e sec. duration= %f sec. on_time= %f sec. times= %i."%(integration_time,duration,on_time,times))
print('Expected ticks = '+str(int(times*duration / (np.floor(integration_time/adw.time_high) * adw.time_high))))
a1,a2 = adw.lifetime(apd1,apd2,aom,duration=duration,acc=integration_time,on_time=on_time,times=times)
print('obtained size apd1 ' + str(len(a1)))
print('obtained size apd2 ' + str(len(a2)))

filename = experiment_label+'_dark_'+t+'.dat'
print(filename)
header = "(Row1: TimeTrace1 (counts),Row2: TimeTrace2 (counts)) integration_time= %e sec. duration= %f sec. on_time= %f sec. times= %f ."%(integration_time,duration,on_time,N)
np.savetxt("%s%s" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)

input('OPEN the shutter for the laser and press enter to take continue...')

print('start')
for nn in range(len(Pos)):
    print('################ New positon started.')
    print('going to Position Number ' + str(nn))
    adw.go_to_position(devs,Pos[nn])
    time.sleep(0.1)
    if (nn % 2 ==0):
        print('PCLE position = '+str(Pos[nn])+'um')
        filename = experiment_label+'_PCLE_position_'+str(int(nn/2))+'_at_'+t+'.dat'
    else:
        print('BKG position = '+str(Pos[nn])+'um')
        filename = experiment_label+'_BKG_position_'+str(int((nn-1)/2))+'_at_'+t+'.dat'

 
    print('taking lifetime')
    a1,a2 = adw.lifetime(apd1,apd2,aom,duration=duration,acc=integration_time,on_time=on_time,times=N)        
    print('ended lifetime')
    print(len(a1))
    print(len(a2))
    data = np.vstack((a1,a2))
    
    print(filename)
    header = "(Row1: TimeTrace1 (counts),Row2: TimeTrace2 (counts)) integration_time= %e sec. duration= %f sec. on_time= %f sec. times= %f ."%(integration_time,duration,on_time,N)
    np.savetxt("%s%s" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    
    # measure power
    # power_aom = 10
    # adw.go_to_position([aom],[power_aom])
    # pw_now=(pmeter.data*1000000)
    # pw[nn,n]=pw_now/9 # power at bfp
    # print('Measured Power =%s uW'%(str(pw_now)))
    # print('Measured Power at BFP =%s uW'%(str(pw[0,n])))

    print('################### done with this position')
#np.savetxt("%s%s" %(savedir,filename[:-4]+'measured_power.dat'), pw,fmt='%s', delimiter=",", header=header)
# finalize power meter
pmeter.finalize()   
print('Program finished')




