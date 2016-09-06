# Script for acquiring timetraces vs intensity manually
#
######################### M. Caldarola - April 2016
import time
from lib.adq_mod import *
from lib.xml2dict import device,variables
from winsound import Beep
from math import floor
import matplotlib.pyplot as plt
plt.ion()  # enable interactive ploting

# inizialize adwin
adw = adq(model='goldII')


Pmin = 10   # uW
Pmax = 100  # uW
N=3
pw_to_set= np.logspace(np.log10(Pmin*9),np.log10(Pmax*9),N)



n=0

fig = plt.figure()
ax = fig.add_subplot(111)
ax.text(0,0.5,'P =%.2e'%(pw_to_set[n])+' uW',fontsize=55)
plt.show()
plt.pause(0.01)
print('Waiting for signal...')
time.sleep(2)

# for n in range(4):
    # plt.close()
    # print('measuring')
    # print('Measurement number =%s'%(n+1))
    # Beep(840,200)
        
    # n=n+1
    # print('Waiting for signal...')
    # if n < N:
        # fig = plt.figure()
        # ax = fig.add_subplot(111)
        # ax.text(0,0.5,'P =%.2e'%(pw_to_set[n])+' uW',fontsize=55)
        # plt.show()
        # plt.pause(0.01)
    # time.sleep(1.5)


while n <N:
    time.sleep(0.1)
    if adw.get_digin(0):
        plt.close()
        print('measuring')
        print('Measurement number =%s'%(n+1))
        Beep(840,200)
        
        n=n+1
        print('Waiting for signal...')
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.text(0,0.5,'P ='+str(floor(pw_to_set[n]))+'uW',fontsize=55)
        plt.show()
        plt.pause(0.01)
        
print('end')
