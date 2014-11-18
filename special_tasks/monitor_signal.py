# Program for monitoring a signal

from __future__ import division
import numpy as np
import time
import matplotlib.pyplot as plt
from lib.adq_mod import *
from lib.xml2dict import device,variables
from datetime import datetime
from tkinter.filedialog import askopenfilename
import msvcrt
import sys
import os
from lib.logger import get_all_caller,logger
from devices.powermeter1830c import powermeter1830c as pp
from winsound import Beep
import subprocess

#names of the parameters
par=variables('Par')
fpar=variables('FPar')
data=variables('Data')
fifo=variables('Fifo')

		
if __name__ == '__main__': 
	#initialize the adwin and the devices   
	#init the Adwin programm and also loading the configuration file for the devices
	adw = adq('lib/adbasic/adwin.T99')  
	counter = device('APD 1')
	threshold = 4000 # Threshold for triggering the fast_timetrace
	j = 1
	
	print('Start monitoring the signal on the APD')
	print('If the value gets higher than %s it will trigger a series of timetraces'%(threshold))
	print('Control+C to stop this monitor')
	last_clear = datetime.now()
	while True:
		adw.clear_digout(2) # Opens the shutter of 1064
		# For monitoring the signal
		timetrace_time = 1	# In seconds
		integration_time = 1 # In seconds
		number_elements = int(timetrace_time/integration_time)
		dd,ii = adw.get_timetrace_static([counter],duration=timetrace_time,acc=integration_time)
		dd = np.array(dd)
		ss = np.sum(dd)
		# Threshold for triggering the data acquisition
		if ss>threshold:
			if ss>5000000:
				print('BURNING APDDDDDDD!!!!')
				adw.set_digout(2)
				for i in range(10):
					Beep(840,200)
					Beep(440,200)
					Beep(240,200)
					Beep(1040,200)
			else:
				print('Acquiring timetraces for particle %s'%(j))
				j+=1
				for i in range(5):
					subprocess.call("super_fast_timetrace.py", shell=True)
				adw.set_digout(2)
				last_clear = datetime.now()
				print('Releasing the particle')
				time.sleep(2) # Waits some seconds before switching on again
				print('Waiting for next particle...')
		if (datetime.now()-last_clear).total_seconds() > 30*60:
			print('Releasing just in case')
			print('Control+C to stop this monitor')
			adw.set_digout(2) # Releases just in case
			last_clear = datetime.now()
			time.sleep(2)
		