from time import sleep
import matplotlib.pyplot as plt
import numpy as np
from devices.powermeter1830c import PowerMeter1830c as PP
from devices.cobolt import rumba
from devices.DriverFuncGen import funcgen

from lantz import Q_

kilohertz = Q_(1000,'Hz')
volt = Q_(1,'V')

with PP.via_serial(1) as pmeter,\
    funcgen.via_usb() as fgen:

    pmeter.wavelength = 633
    pmeter.attenuator = True
    pmeter.units = 'Watts'
    pmeter.go = True

    fgen.func = 'DC'
    fgen.freq = 550 * kilohertz
    fgen.volt = 0 * volt
    fgen.output(True)
    data = []
    offsets = np.linspace(0,5,20)
    for offset in offsets:
        fgen.offset = offset * volt
        sleep(1)
        try:
            power = pmeter.data*1000000
        except:
            power = 0

        data.append(power)
        print(power)

plt.plot(offsets,data,'o')
plt.show()
