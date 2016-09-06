# Script for acquiring several spectra on top of different particles.
# On each partcile we take a spectra. We define also a BKG for 
# each partile, close to it and we measure the same. So the input file must have the positions
# for all the particles to measure and bakground (same number)
# the file with the positions is the output of the program intermediate_scan_mod.py
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


########################################################## Here is the info to be filled in before starting
sample = 'S1607_02_NR_PMMA_film'
experiment_label = 'Spectra_automatic_1_'+sample
print('sample='+sample)


# particle positions
pcle_filename = 'D:\\Data\\2016-07-04\\S1607_03_NR_PMMA_film_positions.txt' # filename with the pcle positions and global bkg.
Zplane = '52.68' # z position of the focus [um]
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
Laser_wavelength = 532 # laser wavelength nm
experiment_label+=str(Laser_wavelength)+'nm_'
print('Experiment Label = ' + experiment_label)
N=1            # number of spectra to be taken in each particle

###########################################################
# starting

# inizialize hardware
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

# inizialize the vectors needed

pw =np.zeros((num_particles,N)) # power at bfp
xp = np.zeros((num_particles,N+1)) # position for each parricle after refocus
yp = np.zeros((num_particles,N+1)) # position
zp = np.zeros((num_particles,N+1)) # position
for n in range(num_particles):
    xp[n,0] = np.array(Pos[n][0])
    yp[n,0] = np.array(Pos[n][1])
    zp[n,0] = np.array(Pos[n][2])

## start measuring
input('############### Do not forget to set up the spectrometer and shut off the flipper program before continuing.')
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
    
# while in the measurement
n=0
input('Set the power for the measurements and then press enter to continue')

while n <N:
    sleep(0.1)
    for nn in range(len(Pos)):
        print('################ New positon started.')
        # measure power
        pw_now=(pmeter.data*1000000)
        print('Measured Power =%s uW'%(str(pw_now)))
        
        # go to the particle 
        print('going to Position Number ' + str(nn))
        adw.go_to_position(devs,Pos[nn])
        time.sleep(0.1)
        if (nn % 2 ==0):
                # go pacbk to apd (pos 1) with flipper
            if flip:
                if flipper_apd != flipper.getPos():
                    flipper.goto(flipper_apd)
                    sleep(0.5)
            print('PCLE position = '+str(Pos[nn])+'um')
            print('Refocusing...')
            aux = adw.focus_full(counter1,devs,Pos[nn],dims,accuracy).astype('str')
            xp[nn/2,n]=aux[0]
            yp[nn/2,n]=aux[1]
            zp[nn/2,n]=aux[2]
            pw[nn/2,n]=pw_now/9 # power at bfp
            print('Final position = '+str(aux))
            time.sleep(0.2)
        else:
            print('BKG position = '+str(Pos[nn])+'um')
        

        # To take spectra
        # change flipprer to spec position
        if flip:
            if flipper_spec != flipper.getPos():
                flipper.goto(flipper_spec)
                sleep(0.5)
        # take spectra
        print('Started spectra at position '+str(nn))
        trigger_spectrometer(adw,digin=2,digout=16,digcheck=3)
        print('Ended spectra at position '+str(nn))

        
        print('##################### done with position '+str(nn))
    n+=1
    print('Done with this run, go to next')
        



# save the positions 
filename = experiment_label+'Particle_x_output.txt'
header = '# Particle x position evolution (um)'
np.savetxt("%s%s" %(savedir,filename), xp,fmt='%s', delimiter=",")

filename = experiment_label+'Particle_y_output.txt'
header = '# Particle  position evolution (um)'
np.savetxt("%s%s" %(savedir,filename), yp,fmt='%s', delimiter=",")

filename = experiment_label+'Particle_z_output.txt'
header = '# Particle y position evolution (um)'
np.savetxt("%s%s" %(savedir,filename), zp,fmt='%s', delimiter=",")

filename = experiment_label+'power_at_bfp.txt'
header = '# Power at BFP [uW]'
np.savetxt("%s%s" %(savedir,filename), pw,fmt='%s', delimiter=",")

##plot the xposition evolution
legend = [];
for n in range(num_particles):
    legend.append( 'Pcle ' + str(n+1))
    plt.figure(1)
    p1=plt.plot(xp[n,:])
    plt.hold

plt.xlabel('Number of measurement')
plt.ylabel('X Position')
plt.legend(legend)
plt.show()

# finalize hardware
pmeter.finalize()   
flipper.close()

print('Program finished')



