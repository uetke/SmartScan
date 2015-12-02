import matplotlib.pyplot as plt
from time import time, sleep
from lib.adq_mod import adq
from lib.xml2dict import device

adw = adq()
num_ticks = 1000000
dur = 5
acc = 2.E-6
tot_time = num_ticks*25*100/1000/1000/1000 # In seconds
apd = device('APD 1')
adw.boot()
#adw.load('lib/ADwinsrc/fast_timetrace.T98')

t,cts = adw.get_fast_timetrace(apd, duration=dur, acc=acc)

plt.plot(t,cts,'o')
plt.show()

#print('Total photons counted: %s'%adw.get_par(79))