from time import time, sleep
from lib.adq_mod import adq

adw = adq()
num_ticks = 1
tot_time = num_ticks*25*85/1000/1000/1000 # In seconds

num_iterations = 10

cycles = 0
for i in range(num_iterations):
    adw.boot()
    adw.load('lib/ADwinsrc/fast_timetrace.T98')
    adw.set_par(74,1)
    adw.set_par(78,num_ticks)
    adw.adw.Set_Processdelay(8, 50)
    adw.start(8)
    sleep(tot_time+.25)
    print('Iteration %s'%i)
    print('\t Cycles: %s'%adw.get_par(1))
    cycles+=adw.get_par(1)

    
print('Total cycles counted on avg: %s'%(cycles/num_iterations))