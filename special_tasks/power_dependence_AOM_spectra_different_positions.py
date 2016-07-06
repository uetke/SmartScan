# Script for acquiring spectra at different powers in a set of particles and bk given by a file
#
######################### M. Caldarola - July 2016
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
from special_tasks.spectrometer import abort, trigger_spectrometer
from devices.flipper import Flipper

########################################################## Here is the info to be filled in before starting
Laser_wavelength = 770 # laser wavelength nm
sample = 'S1607_04_2a_'
print('sample='+sample)
experiment_label = sample+'_'+str(Laser_wavelength)+'nm_power_dependence_spectra_automatic_1'
print(experiment_label)

# particle positions
pcle_filename = 'D:\\Data\\2016-07-06\\te.txt' # filename with the pcle positions and global bkg.
Zplane = '58.4' # z position of the focus [um]

# read particle positions
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
# finished generating the particle positions vectors
    
# refocus parameters
dims = [0.5,0.5,0.8]
accuracy = [0.05,0.05,0.1]

## power dependence definitions.
# min and max power seted with the filters. 
# Use the aom from 0 to 10V to controll the power. We measure each point the power with the PowerMeter
Vrefocus = [5.1]        # voltage value to use for refocusing
N =3 # number of powers to use
V= np.logspace(np.log10(0.5),np.log10(10),N)  # voltages for the power dependence
print('Voltage='+str(V))
########################################################## up to Here is the info to be filled in before starting





############################################################ starting
input('############### Do not forget to set up the spectrometer and shut off the flipper program before continuing. Press enter to start measuring')
# for testing
test = False


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
    pmeter = 0
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
aom = device('AOM Ti:Sa')

# inizialize the vectors needed
pw =np.zeros((len(Pos),N)) # power at bfp

############################## start measuring

## dark spectra
input('close the shutter for the laser and press enter to take an initial time trace of dark counts')

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

input('dark spectra measured. turn on the laser and press enter to continue.')

# while for the measurement
n=0

print('Start the while')

while n <N:
    sleep(0.1)
    print('###############################  Start power '+str(n+1)+' out of ' +str(N))
    for nn in range(len(Pos)):
        print('###### Position '+str(nn+1)+' out of ' +str(len(Pos)))
        
        
        # go to the particle 
        print('going to Position Number ' + str(nn+1))
        adw.go_to_position(devs,Pos[nn])
        time.sleep(0.5)
        if (nn % 2 ==0):
                # go pacbk to apd (pos 1) with flipper
            if flip:
                if flipper_apd != flipper.getPos():
                    flipper.goto(flipper_apd)
                    sleep(0.5)
            print('PCLE position = '+str(Pos[nn])+'um')
            adw.go_to_position([aom],Vrefocus)
            sleep(0.5)
            pw_now=(pmeter.data*1000000)
            print('Measured refocusing power =%s uW'%(str(pw_now)))
            print('Refocusing...')
            aux = adw.focus_full(counter1,devs,Pos[nn],dims,accuracy).astype('str')
            print('Final position = '+str(aux))
            
            time.sleep(0.2)
        else:
            print('BKG position = '+str(Pos[nn])+'um')
        
        # got to power value
        print(V[n])
        adw.go_to_position([aom],[V[n]])
        sleep(0.5)
        # measure power
        pw_now=(pmeter.data*1000000)
        pw[nn,n]=pw_now/9 # power at bfp
        print('Measured Power =%s uW'%(str(pw_now)))
        # To take spectra
        # change flipprer to spec position
        if flip:
            if flipper_spec != flipper.getPos():
                flipper.goto(flipper_spec)
                sleep(0.5)
        # take spectra
        print('Started spectra at position '+str(nn+1))
        trigger_spectrometer(adw,digin=2,digout=16,digcheck=3)
        print('Ended spectra at position '+str(nn+1))

        
        print('###### done with position '+str(nn+1))
    n+=1
    print('###############################  Done with power '+str(n+1)+' out of ' +str(N))

print(pw)
# save powers
filename = experiment_label+'power_at_bfp.dat'
header = "# power in uw"
np.savetxt("%s%s" %(savedir,filename), pw,fmt='%s', delimiter=",", header=header)

       

# finalize hardware
pmeter.finalize()   
flipper.close()

print('End')




