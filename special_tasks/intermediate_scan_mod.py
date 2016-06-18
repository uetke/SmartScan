from __future__ import division
import numpy as np
import time
import matplotlib.pyplot as plt
from lib.adq_mod import *
from lib.xml2dict import device,variables
import os
import re # For extracting the coordinates of the scan
from lib.logger import get_all_caller,logger
from datetime import datetime
from start import adding_to_path
import tkinter

        
if __name__ == '__main__': 
    logger=logger(filelevel=20)
    adding_to_path('lib')
    #names of the parameters
    par=variables('Par')
    fpar=variables('FPar')
    data=variables('Data')
    fifo=variables('Fifo')

    #filename = tkinter.filedialog.askopenfilename(initialdir="D:\\Data",title='Please select a directory')
    filename= 'D:\\Data\\2016-06-15\\NR_complex_PMMA_1mM_739nm_100uW_20x20_image_01.dat'
    image = np.loadtxt('%s' %(filename),dtype='bytes',delimiter =',').astype('float')
    
    f = open('%s'%(filename),'r')
    for line in f:
        if line.startswith('#center'):
            information = line
            break
    print(information)
    a = re.findall('\d+.\d+',information) # Finds only the positive integers
    xcenter = float(a[0])
    ycenter = float(a[1])
    xdim = float(a[2])
    ydim = float(a[3])
    xacc = float(a[4])
    yacc = float(a[5])
    
   
    #plotting the scan and letting the user select/delete particles
    #also the user has to select a background
    #this is for subtracting its spectra from the spectra of a particle 
    fig = plt.figure()
    ax = fig.add_subplot(111)       

    imshow=ax.imshow(image, interpolation='none', cmap='gnuplot')
    plt.colorbar(imshow)

    plot_backg, = ax.plot([], [],markeredgecolor = 'w' ,marker='$\circ$',markersize=10,markeredgewidth=2.0,linestyle="")      
    try:
        particles=adw.find(image,3)  
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
    
    accuracy = np.array([xacc,yacc])
    start = np.array([xcenter,ycenter])-np.array([xdim,ydim])/2
    
    particles = (inter.particles.T*accuracy+start).T
    background = (inter.background.T*accuracy+start).T
    
    global data 
    data = (np.hstack((particles,background)).T).astype('str')
    data = np.append(np.zeros([len(data),1]).astype('str'),data,1)
    data[:,0] = 'background'
    data[:len(particles[0,:]),0] = 'particle'
    data = np.append(data,np.zeros([len(data),2]).astype('str'),1)    
    
    name = input('Give the name of the sample: ')
    savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    i=1
    filename = name    
    while os.path.exists(savedir+filename+"_good1.txt"):
        filename = '%s_%s' %(name,i)
        i += 1
        
    header = "type,x-pos,y-pos,z-pos,first scan time" + ",time_%s"*(len(data[0,:])-5) %tuple(range((len(data[0,:])-5)))
    np.savetxt("%s%s_good.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)   
    logger.info('Coordinates file saved as %s%s_good.txt' %(savedir,filename))
    print('Coordinates file saved as %s%s_good.txt\n' %(savedir,filename))
    print('Now is time to continue with continue_scan_mod.py\n')
    print('Program finished')
