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
    cwd = os.getcwd()
    savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
    print('For quiting press q')
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    i=1
    filename = name    
    while os.path.exists(savedir+filename):
        filename = '%s_%s' %(name,i)
        i += 1
    logger.info('%s\\%s.log' %(savedir,filename))
    print('Data will be saved in %s'%(savedir+filename))
    #init the Adwin programm and also loading the configuration file for the devices
    adw = adq('adwin.T99') 
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    counter = device('APD 1')
    aom = device('AOM')
    adw.load()
    adw.go_to_position([aom],[1.25])
    #making a 2d scan of the sample and trying to find particles
    xcenter = 50 #In um
    ycenter = 50
    zcenter = 50
    xdim = 30    #In um
    ydim = 30
    xacc = 0.2   #In um
    yacc = 0.2
    devs = [xpiezo,ypiezo,zpiezo]
    #parameters for the refocusing on the particles
    dims = [0.3,0.3,1]
    accuracy = [0.1,0.1,0.2]
    adw.go_to_position(devs[:3],[xcenter,ycenter,zcenter])
    
    pressing = input('First let\'s do a scan with the 532. Enter when ready\n')
    
    image = np.array(adw.scan_static(counter,[xpiezo,ypiezo],[xcenter,ycenter],[xdim,ydim],[xacc,yacc]))
    image = np.squeeze(image)
    
    start_scan = np.array([adw.scan_settings[xpiezo.properties['Name']+'_start'] ,adw.scan_settings[ypiezo.properties['Name']+'_start']])
    accuracy_scan = np.array([adw.scan_settings[xpiezo.properties['Name']+'_accuracy'],adw.scan_settings[ypiezo.properties['Name']+'_accuracy']])
   
    #plotting the scan and letting the user select/delete particles
    #also the user has to select a background
    #this is for subtracting its spectra from the spectra of a particle 
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    header = 'center = [%s,%s,%s], dim = [%s,%s], acc = [%s,%s]' %(xcenter,ycenter,zcenter,xdim,ydim,xacc,yacc)
    np.savetxt(savedir + "%s_raw_image.txt" %(filename),image,fmt='%s',delimiter=',',header=header)
    imshow=ax.imshow(image, interpolation='none', cmap='gnuplot')
    plt.colorbar(imshow)
#    plt.savefig(savedir + "%s_scan" %(filename))

    plot_backg, = ax.plot([], [],markeredgecolor = 'w' ,marker='$\circ$',markersize=10,markeredgewidth=2.0,linestyle="")      
    try:
        particles=adw.find(adw.scan_image,3)  
        plot_parti, = ax.plot(particles[0,:], particles[1,:],markeredgecolor = 'g' ,marker='$\circ$',markersize=10,markeredgewidth=2.0,linestyle="")
        print('%i particles found automatically'%(len(particles)))
        logger.info('%i particles found automatically'%(len(particles)))
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
    
    for i in range(len(particles[0,:])):
        center = np.append(particles[:2,i],zcenter)
        adw.go_to_position(devs[:2],center[:2])
        data[i,1:4] =  adw.focus_full(counter,devs,center,dims,accuracy,rate=1,speed=10)
        adw.set_digout(0)
        data[i,4]=str(datetime.now().time())
        time.sleep(0.5)
        adw.clear_digout(0)
        while adw.get_digin(1):
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if ord(key) == 113: #113 is ascii for letter q
                     abort(filename+'_init')
            time.sleep(0.1)
        print('Done with particle %i of %i'%(i,len(particles[0,:])))
        
    print('Initial particle spectra taken')
    
    #make a spectra of the selected background
    for i in range(len(background[0,:])):
        center = np.append(background[:2,i],np.mean(data[:len(particles[0,:]),3].astype('float')))
        print(center)
        adw.go_to_position(devs,center)
        adw.set_digout(0)
        data[i-len(background[0,:]),3]=str(np.mean(data[:len(particles[0,:]),3].astype('float')))
        data[i-len(background[0,:]),4]=str(datetime.now().time())
        time.sleep(0.5)
        adw.clear_digout(0)
        while adw.get_digin(1):
            if msvcrt.kbhit(): # <--------
                key = msvcrt.getch()
                if ord(key) == 113:
                     abort(filename+'_init')
            time.sleep(0.1)
    logger.info('Initial spectra of particles and background is taken')
            
    print('Background spectra are taken')
    
    header = "type,x-pos,y-pos,z-pos,first scan time" + ",time_%s"*(len(data[0,:])-5) %tuple(range((len(data[0,:])-5)))
    np.savetxt("%s%s_init.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)   
    logger.info('Initial file saved as %s%s_init.txt' %(savedir,filename))
    
    
    
    data = np.loadtxt('%s%s_init.txt' %(savedir, filename),dtype='bytes',delimiter =',').astype('str')#strange b in front of strings 
    num_particles = sum(data[:,0]=='particle')
    num_background = sum(data[:,0]=='background')
    
    print('Now is time to do a scan and take spectra with the 633nm laser\n')
    pressing = input('Change filters and press Enter: \n')
    if not os.path.exists(savedir):
        os.makedirs(savedir)

    i=1  
    while os.path.exists(savedir+filename):
        filename = '%s_%s' %(name,i)
        i += 1
    
    logger.info('%s\\%s.log' %(savedir,filename))
        
    for m in range(20):
        power_aom = 2.5-m*2.5/20
        adw.go_to_position([aom],[power_aom])
        print('For quiting press q')
    
        num_particles = sum(data[:,0]=='particle')
        num_background = sum(data[:,0]=='background')
   
        j = 0
        for i in range(num_particles):
            center = data[i,1:4].astype('float')
            adw.go_to_position(devs,center)
            if m==0: # If it's the first time that is running
                data[i,1:4] = adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
            adw.set_digout(0)
            power = adw.adc(5)
            
            try:
                data[i,j+5]=str(power)
            except:
                data = np.append(data,np.zeros([len(data),1]).astype('str'),1)
                data[i,j+5]=str(power)
                
            time.sleep(0.5)    
            adw.clear_digout(0)
            while adw.get_digin(1):
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if ord(key) == 113:
                        abort(filename + '_inter')
                time.sleep(0.1)
            print('Done with %s of %s particles' %(i, num_particles))
        #make a spectra of the selected backgrounds
        
        for i in range(num_background):
            center = data[i-num_background,1:4].astype('float')
            adw.go_to_position(devs,center)
            adw.set_digout(0)
            time.sleep(0.5)
            adw.clear_digout(0)
            while adw.get_digin(1):
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if ord(key) == 113:
                         abort(filename + '_inter')
                time.sleep(0.1)
            
            data[i-num_background,j+5]=str(power)
                
            print('Done with %s of %s backgrounds'%(i,num_background))
            
        print('Final background spectra are taken')
        
        j += 1    
        print('Go to the next power cycle')
        
    header = "type,x-pos,y-pos,z-pos,laser power"
    np.savetxt("%s%s_final.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    logger.info('Final file saved as %s%s_final.txt' %(savedir,filename))
    logger.info('Program completed')
    print('Program completed')
    

    
    