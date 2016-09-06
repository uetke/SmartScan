import matplotlib.pyplot as plt
from time import time, sleep
from lib.adq_mod import adq
from lib.xml2dict import device
from datetime import datetime
import msvcrt
import sys
import os
import numpy as np
## stop all other processes in the adwin before running this. Done in line 28
experiment_label = 'S1607_04_2a_770nm_278uW_Single_Lifetime_pcle_6'

print('###################################### started lifetime measurement...')
print('###################################### ')
# generate saving path
savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
now = datetime.now().strftime('%Hhs%Mm')

if not os.path.exists(savedir):
    os.makedirs(savedir)
print('Save directory: ' + savedir)

adw = adq(model='goldII')
apd1 = device('APD 1')
apd2 = device('APD 2')
aom = device('AOM Ti:Sa')
#adw.boot()
adw.load('lib/adbasic/lifetime.TB1')
adw.stop(10)

filename = experiment_label+'_'+now+'.dat'
print('Filename to save: '+ filename)

# define parameters for lifetime measurement
integration_time = 25E-6            # bin time or integration time [sec]
detection_time=3E-3                 # detection time [sec]
on_time=3E-3                        # Laser on time [sec]
duration = detection_time+on_time   # One run experiment time length [sec]
times=3000                          # number of times to repeat the single cycle.
# show
print("integration_time= %e sec. duration= %f sec. on_time= %f sec. times= %i."%(integration_time,duration,on_time,times))
print('Expected ticks = '+str(int(times*duration / (np.floor(integration_time/adw.time_high) * adw.time_high))))
# measure
a1,a2 = adw.lifetime(apd1,apd2,aom,duration=duration,acc=integration_time,on_time=on_time,times=times)
print('obtained size apd1 ' + str(len(a1)))
print('obtained size apd2 ' + str(len(a2)))
data = np.vstack((a1,a2)) # stack data obtained to save.
# save
header = "(Row1: TimeTrace1 (counts),Row2: TimeTrace2 (counts)) integration_time= %e sec. duration= %f sec. on_time= %f sec. times= %f ."%(integration_time,duration,on_time,times)
np.savetxt("%s%s" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)

# plot the results
plt.plot(a1)
plt.show()

print('############### finished lifetime measurement.')