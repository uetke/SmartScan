from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg

from lib.adq_mod import adq
from lib.xml2dict import variables

par=variables('Par','config/config_variables.xml')
fpar=variables('FPar','config/config_variables.xml')
data=variables('Data','config/config_variables.xml')
fifo=variables('Fifo','config/config_variables.xml')
adw = adq('lib/adbasic/qpd.T98') 
adw.load()

time = .5 # 1 Second acquisition
accuracy = .00005 # Accuracy in seconds
num_points = int(time/accuracy)
freqs = np.fft.rfftfreq(num_points, accuracy)

initial_data = np.random.normal(size=(num_points))
initial_ps = np.abs(np.fft.rfft(initial_data))**2

win = pg.GraphicsWindow(title="QPD Power Spectrum")
win.resize(900,900)
win.setWindowTitle('QPD Power Spectrum')
win.move(330,10)

win3 = pg.GraphicsWindow(title="QPD Traces")
win3.resize(900,900)
win3.setWindowTitle('QPD Traces')
win3.move(330,10)

px3 = win3.addPlot(title="QPD x")
curvex3 = px3.plot(freqs,initial_ps,pen='y')
px3.setLabel('left', "Power Spectrum", units='U.A.')
px3.setLabel('bottom', "Frequency", units='Hz')



py3 = win3.addPlot(title="QPD y")
curvey3 = py3.plot(freqs,initial_ps,pen='y')
py3.setLabel('left', "Power Spectrum", units='U.A.')
py3.setLabel('bottom', "Frequency", units='Hz')


win.nextRow()

pz3 = win3.addPlot(title="QPD z")
curvez3 = pz3.plot(freqs,initial_ps,pen='y')
pz3.setLabel('left', "Power Spectrum", units='U.A.')
pz3.setLabel('bottom', "Frequency", units='Hz')


px3.enableAutoRange('xy', True)  ## stop auto-scaling after the first data set is plotted
py3.enableAutoRange('xy', True)  ## stop auto-scaling after the first data set is plotted
pz3.enableAutoRange('xy', True)  ## stop auto-scaling after the first data set is plotted

win2 = QtGui.QMainWindow()
win2.resize(300,800)
win2.move(10,10)
win2.setWindowTitle('QPD Values')
qpdx = QtGui.QLCDNumber(win2)
qpdx.display(123.5)
qpdx.resize(250,250)
qpdx.move(10,10)
qpdy = QtGui.QLCDNumber(win2)
qpdy.display('124.5')
qpdy.resize(250,250)
qpdy.move(10,260)
qpdz = QtGui.QLCDNumber(win2)
qpdz.display(125.6)
qpdz.resize(250,250)
qpdz.move(10,510)

pg.setConfigOptions(antialias=True)

px = win.addPlot(title="QPD x")
curvex = px.plot(freqs,initial_ps,pen='y')
px.setLabel('left', "Power Spectrum", units='U.A.')
px.setLabel('bottom', "Frequency", units='Hz')
px.setLogMode(x=True, y=True)


py = win.addPlot(title="QPD y")
curvey = py.plot(freqs,initial_ps,pen='y')
py.setLabel('left', "Power Spectrum", units='U.A.')
py.setLabel('bottom', "Frequency", units='Hz')
py.setLogMode(x=True, y=True)

win.nextRow()

pz = win.addPlot(title="QPD z")
curvez = pz.plot(freqs,initial_ps,pen='y')
pz.setLabel('left', "Power Spectrum", units='U.A.')
pz.setLabel('bottom', "Frequency", units='Hz')
pz.setLogMode(x=True, y=True)

px.enableAutoRange('xy', True)  ## stop auto-scaling after the first data set is plotted
py.enableAutoRange('xy', True)  ## stop auto-scaling after the first data set is plotted
pz.enableAutoRange('xy', True)  ## stop auto-scaling after the first data set is plotted

def update():
    global curvex, curvey, curvez, qpdz, qpdy, qpdx
    datax, datay, dataz = adw.get_QPD(time,accuracy)
    print(dataz)
    datax = np.float64((datax-32768)/6553.6)
    datay = np.float64((datay-32768)/6553.6)
    dataz = np.float64((dataz-32768)/6553.6)
   
    curvex3.setData(datax)
    curvey3.setData(datay)
    curvez3.setData(dataz)
    
    pwrx = np.abs(np.fft.rfft(datax))**2
    pwry = np.abs(np.fft.rfft(datay))**2
    pwrz = np.abs(np.fft.rfft(dataz))**2
    
    datax = np.float32(np.mean(datax))
    datay = np.float32(np.mean(datay))
    dataz = np.float32(np.mean(dataz))
    
    curvex.setData(freqs[1:],pwrx[1:])
    curvey.setData(freqs[1:],pwry[1:])
    curvez.setData(freqs[1:],pwrz[1:])
    

    qpdz.display('%5.1f'%(dataz) )
    qpdx.display('%5.1f'%(datax) )
    qpdy.display('%5.1f'%(datay) )
    print('%5.1f'%(dataz) )
    print('%5.1f'%(datax) )
    print('%5.1f'%(datay) )
    
#timer = QtCore.QTimer()
#timer.timeout.connect(update)
#timer.start(60)
update()

win2.show()
## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()