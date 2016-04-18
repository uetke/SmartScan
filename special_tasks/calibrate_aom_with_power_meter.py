#
#
#
#
######################### M. Caldarola - April 2016
import numpy as np
from devices.powermeter1830c import PowerMeter1830c as pp
import time
import matplotlib.pyplot as plt
from lib.adq_mod import *
from lib.xml2dict import device,variables

# save folder 
savedir = 'E:\\Martin\\Measurements\\Perylene\\2016-04-15-AOM_cal\\'
print('Save directory: ' + savedir)


# inizialize the pmeter
pmeter = pp.via_serial(1)
pmeter.initialize()
time.sleep(0.5)

# set the configuration of power meter.
pmeter.attenuator = False
time.sleep(0.5)
pmeter.wavelength = 671
print('Wavelength = '+str(pmeter.wavelength)+' nm')
time.sleep(0.5)
print('Units = '+str(pmeter.units))
pmeter.range = 0
print('Range = '+str(pmeter.range))
time.sleep(0.5)

# inizialize adwin
adw = adq()
aom = device('AOM')
adw.go_to_position([aom],[0])
time.sleep(1)
v_aom = np.linspace(0,3,50)

# for to get the data
data = [];

print('Runnin the for...')

for a in v_aom:
    adw.go_to_position([aom],[a])
    time.sleep(2)
    data.append(pmeter.data*1000000) # the data is now in uW
    print(a)
    
print('For done!')

# save
np.savetxt("%s\\aom_calibration2.txt" %(savedir), (v_aom,data),fmt='%s', delimiter=',')

# finalize
pmeter.finalize()    

# plot 
plt.plot(np.array(v_aom),np.array(data))
plt.xlabel('AOM voltage [V]')
plt.ylabel('Measured Power [uW]')
plt.show()

print('Finished')


