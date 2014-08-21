from __future__ import division
import numpy as np
import time
import matplotlib.pyplot as plt
from adq_functions import *
from xml2dict import device,variables
from datetime import datetime
import msvcrt
import sys
import os
from logger import get_all_caller,logger

logger=logger(filelevel=20)

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
        
if __name__ == '__main__': 
    #initialize the adwin and the devices   
    name = input('Give the name of the sample: ')
    print('For quiting press q')
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    i=1
    filename = name    
    while os.path.exists(savedir+filename):
        filename = '%s_%s' %(name,i)
        i += 1
    logger.info('%s\\%s.log' %(savedir,filename))
    
    #init the Adwin programm and also loading the configuration file for the devices
    adw = adq('lib/adbasic/adwin.T99') 
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    counter = device('APD 1')
    adw.load()
    
    #making a 2d scan of the sample and trying to find particles
    xcenter = 50
    ycenter = 50
    zcenter = 54.25
    xdim = 40
    ydim = 40
    xacc = 0.1
    yacc = 0.1
    
    adw.scan_static(counter,[xpiezo,ypiezo],[xcenter,ycenter],[xdim,ydim],[xacc,yacc])
    particles=adw.find(adw.scan_image,3)
    start_scan = np.array([adw.scan_settings[xpiezo.properties['Name']+'_start'] ,adw.scan_settings[ypiezo.properties['Name']+'_start']])
    accuracy_scan = np.array([adw.scan_settings[xpiezo.properties['Name']+'_accuracy'],adw.scan_settings[ypiezo.properties['Name']+'_accuracy']])
    print(particles)
    
    #plotting the scan and letting the uses select/delete particles
    #also the user has to select a background
    #this is for subtracting its spectra from the spectra of a particle 
    fig = plt.figure()
    ax = fig.add_subplot(111)
    image = adw.scan_image
    imshow=ax.imshow(image, interpolation='none', cmap='gnuplot')
    plt.colorbar(imshow)
    plt.savefig(savedir + "%s_scan" %(filename))
    plot_backg, = ax.plot([], [],markeredgecolor = 'w' ,marker='$\circ$',markersize=10,markeredgewidth=2.0,linestyle="")      
    try:
        plot_parti, = ax.plot(particles[0,:], particles[1,:],markeredgecolor = 'g' ,marker='$\circ$',markersize=10,markeredgewidth=2.0,linestyle="")
        print(len(particles[0,:]))
        inter=inter_add_remove(plot_parti,plot_backg,particles[:2,:])
    except:
        logger.warning('no patrticles found')
        plot_parti, = ax.plot([], [],markeredgecolor = 'g' ,marker='$\circ$',markersize=10,markeredgewidth=2.0,linestyle="")
        inter=inter_add_remove(plot_parti,plot_backg)
        
    ax.set_xlim(0,len(image[0,:]))
    ax.set_ylim(0,len(image[:,0]))
    plt.show()
    
    particles = (inter.particles.T*accuracy_scan+start_scan).T
    background = (inter.background.T*accuracy_scan+start_scan).T
    
    #first make an initial spectra of all the particles
    global data 
    data = (np.hstack((particles,background)).T).astype('str')
    data = np.append(np.zeros([len(data),1]).astype('str'),data,1)
    data[:,0] = 'background'
    data[:len(particles[0,:]),0] = 'particle'
    data = np.append(data,np.zeros([len(data),2]).astype('str'),1)
    devs = [xpiezo,ypiezo,zpiezo]
    #parameters for the refocusing on the particles
    dims = [1,1,2]
    accuracy = [0.05,0.05,0.1]
    
    
    for i in range(len(particles[0,:])):
        center = np.append(particles[:2,i],zcenter)
        adw.go_to_position(devs[:2],center[:2])
        data[i,1:4] =  adw.focus_full(counter,devs,center,dims,accuracy,rate=1)
        adw.set_digout(0)
        data[i,4]=str(datetime.now().time())
        adw.clear_digout(0)
        time.sleep(0.5)
        while adw.get_digin(1):
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if ord(key) == 113: #113 is ascii for letter q
                     abort(filename+'_init')
            time.sleep(0.1)
        print('Done go to next')
    print('initial particle spectra are taken')
    
    #make a spectra of the selected background
    for i in range(len(background[0,:])):
        center = np.append(background[:2,i],np.mean(data[:len(particles[0,:]),3].astype('float')))
        print(center)
        adw.go_to_position(devs,center)
        adw.set_digout(0)
        data[i-len(background[0,:]),3]=str(np.mean(data[:len(particles[0,:]),3].astype('float')))
        data[i-len(background[0,:]),4]=str(datetime.now().time())
        adw.clear_digout(0)
        time.sleep(0.5)
        while adw.get_digin(1):
            if msvcrt.kbhit(): # <--------
                key = msvcrt.getch()
                if ord(key) == 113:
                     abort(filename+'_init')
            time.sleep(0.1)
    print('background spectra are taken')
    
    header = "type,x-pos,y-pos,z-pos,first scan time" + ",time_%s"*(len(data[0,:])-5) %tuple(range((len(data[0,:])-5)))
    np.savetxt("%s%s_init.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)   
    logger.info('Initial file saved as %s%s_init.txt' %(savedir,filename))
    logger.info('Initial spectra of particles and background is taken')
    
    print('Give now the particles and backgrounds \nthat have a good spectrum')
    print('Save the file in same map under same %s_good.txt' %filename)
    input('Press enter to continue')
    duration = float(input('Give the duration of the experiment in minutes'))
    data = np.loadtxt('%s%s_good.txt' %(savedir, filename),dtype='bytes',delimiter =',').astype('str')#strange b in front of strings 
    num_particles = sum(data[:,0]=='particle')
    num_background = sum(data[:,0]=='background')
    
    #focus on all particles and making spectra 
    start_time = datetime.now()
    time_elaps = (datetime.now()-start_time).total_seconds()
    focus = True
    focus_time = time_elaps
    refocus_time = 300
    first = True
    j = 0
    while time_elaps<duration*60:
        if time_elaps - focus_time > refocus_time or first:
            focus = True
            first = False
            focus_time = time_elaps
        else:
            focus = False
        for i in range(num_particles):
            center = data[i,1:4].astype('float')
            adw.go_to_position(devs,center)
            if focus:
                data[i,1:4] = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
            adw.set_digout(0)
            try:
                data[i,j+5]=str(datetime.now().time())
            except:
                data = np.append(data,np.zeros([len(data),1]).astype('str'),1)
                data[i,j+5]=str(datetime.now().time())
            adw.clear_digout(0)
            print('wait')
            while adw.get_digin(1):
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if ord(key) == 113:
                        abort(filename + '_inter')
                time.sleep(0.1)
            print('Done go to next')
        print('Go to the next cicle')
        header = "type,x-pos,y-pos,z-pos,first scan time" + ",time_%s"*(len(data[0,:])-5) %tuple(range((len(data[0,:])-5)))
        np.savetxt("%s%s_inter.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
        time_elaps = (datetime.now()-start_time).total_seconds()
        j+=1
    print('particles spectra are taken')
    
    #make a spectra of the selected background
    for i in range(num_background):
        center = data[i-num_background,1:4].astype('float')
        adw.go_to_position(devs,center)
        adw.set_digout(0)
        data[i-num_background,-1]=str(datetime.now().time())
        adw.clear_digout(0)
        while adw.get_digin(1):
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if ord(key) == 113:
                     abort(filename + '_inter')
            time.sleep(0.1)
        print('Done go to next')
    print('final background spectra are taken')
    header = "type,x-pos,y-pos,z-pos,first scan time" + ",time_%s"*(len(data[0,:])-5) %tuple(range((len(data[0,:])-5)))
    np.savetxt("%s%s_final.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    logger.info('Final file saved as %s%s_final.txt' %(savedir,filename))
    logger.info('Program completed')
    
    