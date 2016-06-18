# Script for acquiring power dependece.
# The power is changed manually and the measurements are triggered by the pulser.
# On each partcile we take a time trace and a spectra. We define also a BKG for 
# each partile, close to it and we measure the same.
# 
#
######################### M. Caldarola - May 2016
# import 
from __future__ import division
import numpy as np
from time import sleep
import matplotlib.pyplot as plt
from math import floor
from lib.adq_mod import *
from lib.xml2dict import device,variables
from datetime import datetime
import msvcrt
import sys
import os
from lib.logger import get_all_caller,logger
from devices.powermeter1830c import PowerMeter1830c as pp
from winsound import Beep
from special_tasks.spectrometer import abort, trigger_spectrometer
from devices.flipper import Flipper


########

plt.ion() # enables interactive plot to show big numbers.

########################################################## Here is the info to be filled in before starting
experiment_label = 'NR_complex_PMMA_1mM_739nm_power_dependence'
# define parameters for the time trace
timetrace_time = 3# In seconds
integration_time = .05 # In seconds
number_elements = int(timetrace_time/integration_time)

# particle positions
pcle_filename = 'D:\\Data\\2016-06-15\\NR_complex_PMMA_1mM_good.txt' # filename with the pcle positions and global bkg.
Zplane = '52.10' # z position of the focus [um]
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
    
# refocus parameters
dims = [0.5,0.5,0.8]
accuracy = [0.05,0.05,0.1]

## power dependence definitions.
Laser_wavelength = 739 # nm
N=2             # number of measurements to be done
# min and max power to use in the sample (make sure it is lower than the threshold)
# it is transformed to the power to be measured automatically.
Pmin = 100
Pmax = 200 # uw at BFP
pw_to_set= np.logspace(np.log10(Pmin*9),np.log10(Pmax*9),N)

# for testing
test = False
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

# Initialize the motorized flipper mirror
try:
    flipper = Flipper(SerialNum=b'37863346')
    flipper_apd = 1 # Position going to the APD
    flipper_spec = 2 # Position going to the spectrometer
    flip = True
except:
    print('Problem initializing the flipper mirror')
    flip = False
    
    
    
# inizialize adwin
adw = adq(model='goldII')
xpiezo = device('x piezo')
ypiezo = device('y piezo')
zpiezo = device('z piezo')
devs = [xpiezo,ypiezo,zpiezo]
counter1 = device('APD 1')
counter2 = device('APD 2')

# inizialize the vectors needed
pw =np.zeros((1,N)) # power at bfp

xp = np.zeros((num_particles,N)) # position for each parricle after refocus
yp = np.zeros((num_particles,N)) # position
zp = np.zeros((num_particles,N)) # position

## start measuring
input('############### Do not forget to set up the spectrometer before continuing.')
input('close the shutter for the laser and press enter to take an initial time trace of dark counts')
if flip:
    if flipper_apd != flipper.getPos():
        flipper.goto(flipper_apd)
        sleep(0.5)
# measure dark time trace and save 
print('taking dark time trace')
dd,ii = adw.get_timetrace_static([counter1,counter2],duration=timetrace_time,acc=integration_time)
filename = experiment_label +'_Meas_at_'+t+'_TimeTrace_dark.dat'
if test==False: # save timetrace plce
    header = "(Row1: TimeTrace1 (counts), Row2: TimeTrace1 (counts)) integration time: %f seconds"%(integration_time)
    np.savetxt("%s%s" %(savedir,filename), dd,fmt='%s', delimiter=",", header=header)

# put the flipper to the spectrometer
if flip:
    if flipper_spec != flipper.getPos():
        flipper.goto(flipper_spec)
        sleep(0.5)

print('taking spectra')
trigger_spectrometer(adw,digin=2,digout=16,digcheck=3)
# go pack to apd
if flip:
    if flipper_apd != flipper.getPos():
        flipper.goto(flipper_apd)
        sleep(0.5)

input('dark counts and spectra measured. turn on the laser and press enter to continue.')
    
# while in the measurement
n=0
print('First Measurement. Power to be set= %s uW'%(pw_to_set[n]))
print('Waiting for triggger...')

# shows a plot with the number to be set in big fontsize
fig = plt.figure()
ax = fig.add_subplot(111)
ax.text(0,0.5,'P =%.2e'%(pw_to_set[n])+' uW',fontsize=55)
plt.show()
plt.pause(0.0001)
print('Waiting for signal...')

while n <N:
    sleep(0.1)
    if adw.get_digin(0):
        plt.close()
        print('Measurement started.')
        Beep(440,200)
        for nn in range(len(Pos)):
            print('################ New positon started.')
            # go to the particle 
            if test==False:
                print('going to Position Number ' + str(nn))
                adw.go_to_position(devs,Pos[nn])
                time.sleep(0.1)
                if (nn % 2 ==0):
                    print('PCLE position = '+str(Pos[nn])+'um')
                    print('Refocusing...')
                    aux = adw.focus_full(counter1,devs,Pos[nn],dims,accuracy).astype('str')
                    xp[nn/2,n]=aux[0]
                    yp[nn/2,n]=aux[1]
                    zp[nn/2,n]=aux[2]
                    print('Final position = '+str(aux))
                    time.sleep(0.2)
                    
                else:
                    print('BKG position = '+str(Pos[nn])+'um')
                    
                    
            pw_now=(pmeter.data*1000000)
            pw[0,n]=pw_now/9 # power at bfp
            print('Measured Power =%s uW'%(str(pw_now)))
            print('Measured Power at BFP =%s uW'%(str(pw[0,n])))
            
            filename = experiment_label +'_Meas_at_'+t+'_TimeTrace_PosNumber'+str(nn)+'_Measured_Power='+str(pw_now)+'uW.dat'
            
            # # time trace and save on the particle
            print('Started time trace at position '+str(nn))
            dd,ii = adw.get_timetrace_static([counter1,counter2],duration=timetrace_time,acc=integration_time)
            print('Ended time trace at position '+str(nn))
           
            if test==False: # save timetrace 
                header = "(Row1: TimeTrace1 (counts), Row2: TimeTrace1 (counts)) integration time: %f seconds"%(integration_time)
                np.savetxt("%s%s" %(savedir,filename), dd,fmt='%s', delimiter=",", header=header)
                
                # To take spectra
                
                # change flipprer to spec position, 2
                if flip:
                    if flipper_spec != flipper.getPos():
                        flipper.goto(flipper_spec)
                        sleep(0.5)
                # spectra
                print('Started spectra at position '+str(nn))
                trigger_spectrometer(adw,digin=2,digout=16,digcheck=3)
                print('Ended spectra at position '+str(nn))
                # go pacbk to apd (pos 1) with flipper
                if flip:
                    if flipper_apd != flipper.getPos():
                        flipper.goto(flipper_apd)
                        sleep(0.5)
            
            print('##################### done with position '+str(nn))
                
        Beep(440,250)
        Beep(560,250)
        Beep(440,250)
        Beep(440,350)
        print('Done with this power, go to next')
        
        n=n+1
        if n < N:
            print('Measurement number =%s out of %s. Power to be set= %s uW'%(n+2,N,np.logspace(np.log10(Pmin*9),np.log10(Pmax*9),N)[n]))
            print('Waiting for trigger...') 
            # show a new plot with the next value to be set
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.text(0,0.5,'P =%.2e'%(pw_to_set[n])+' uW',fontsize=55)
            plt.show()
            plt.pause(0.0001)
        
#TODO: save the positions of the particles


# finalize power meter
pmeter.finalize()   
flipper.close()

print('End')




