# Test of writing myself

import os

import numpy as np
import time
import msvcrt
import sys
import os
from datetime import datetime
from spectrometer import abort, trigger_spectrometer
import copy

print('This is a test')

myself = os.path.basename(__file__)
savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'

i=1
name = myself
filename = '%s_%s.dat'%(name,i)
while os.path.exists(savedir+filename):
    i += 1
    filename = '%s_%s.dat' %(name,i)
    print('Data will be saved in %s'%(savedir+filename))
    
f = open(myself,'r')
g = open(savedir+filename,'w')
for line in f:
    g.write(line)
    print(line)
f.close()
g.close()
print('Finish')
