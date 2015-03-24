from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg

from lib.adq_mod import adq
from lib.xml2dict import device,variables

par=variables('Par')
fpar=variables('FPar')
data=variables('Data')
fifo=variables('Fifo')
adw = adq('lib/adbasic/qpd.T98') 
adw.load()

QPDx = device('QPDx')
QPDy = device('QPDy')
QPDz = device('QPDz')

time = 1. # 1 Second acquisition
accuracy = .00005 # Accuracy in seconds
num_points = int(time/accuracy)
freqs = np.fft.fftfreq(num_points, accuracy)

initial_data = np.random.normal(size=(1,num_points))
initial_ps = np.abs(np.fft.fft(initial_data))**2

win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: Plotting')

pg.setConfigOptions(antialias=True)

px = win.addPlot(title="Updating plot")
curvex = px.plot(freqs,initial_ps,pen='y')
px.setLabel('left', "Power Spectrum", units='U.A.')
px.setLabel('bottom', "Frequency", units='Hz')
px.setLogMode(x=True, y=True)

py = win.addPlot(title="Updating plot")
curvey = py.plot(freqs,initial_ps,pen='y')
py.setLabel('left', "Power Spectrum", units='U.A.')
py.setLabel('bottom', "Frequency", units='Hz')
py.setLogMode(x=True, y=True)

win.nextRow()

pz = win.addPlot(title="Updating plot")
curvez = pz.plot(freqs,initial_ps,pen='y')
pz.setLabel('left', "Power Spectrum", units='U.A.')
pz.setLabel('bottom', "Frequency", units='Hz')
pz.setLogMode(x=True, y=True)

px.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
py.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
pz.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted

def update():
    global curvex, curvey, curvez
    datax, datay, dataz = adw.get_QPD(time,accuracy)
    
    pwrx = np.abs(np.fft.fft(datax))**2
    pwry = np.abs(np.fft.fft(datay))**2
    pwrz = np.abs(np.fft.fft(dataz))**2
    
    curvex.setData(freqs,pwrx)
    curvey.setData(freqs,pwry)
    curvez.setData(freqs,pwrz)
    
    
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(time*1000*2)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()