from __future__ import division
import numpy as np
from ADwin import ADwin
import time
import scipy.ndimage
import matplotlib.pyplot as plt
import math as m
from sys import stdout
import ctypes
import psutil
from xml2dict import device,variables
import logging
from logger import get_all_caller
import copy
	
	
class adq(ADwin):
	def __init__(self, process):
		DEVICENUMBER = 1 # By default this is the number
		RAISE_EXCEPTIONS = 1
		self.adw = ADwin(DEVICENUMBER, RAISE_EXCEPTIONS)
		self.proc = process
		self.proc_num = int(process[-1])
		if self.proc_num == 0:
			self.proc_num = 10
		self.scan_settings = dict()
		self.dev_value = dict()
		self.running = False
		self.logger = logging.getLogger(get_all_caller())
		self.logger.info('Init the class with process %s' %process)
		
	def boot(self): 
		""" Boots the ADwin. """
		self.logger = logging.getLogger(get_all_caller())
		self.logger.info('Booted the Adwin')
		self.adw.Boot('c:\\adwin\\ADwin9.btl')
		
	def load(self,process=None): 
		""" Loads the processes. """
		if process==None:
			process=self.proc_num
		self.adw.Load_Process(self.proc)
		self.logger = logging.getLogger(get_all_caller())
		self.logger.info("Loaded process %s" %process)
		
	def start(self,process=None):
		""" Starts the process"""
		if process==None:
			process=self.proc_num
		self.logger = logging.getLogger(get_all_caller())
		self.adw.Start_Process(process)
		self.logger.info("Started process %s" %process)
		
	def stop(self,process=None):
		""" Stops the process"""
		if process==None:
			process=self.proc_num
		self.adw.Stop_Process(process)
		self.logger = logging.getLogger(get_all_caller())
		self.logger.info("Stopped process %s" %process)
	
	def wait(self,ref_time=0.1):
		""" Waits until the process is finished"""
		self.logger = logging.getLogger(get_all_caller())
		self.logger.info("Waiting")
		while self.adw.Process_Status(self.proc_num):
			time.sleep(ref_time)  
			   
	def set_par(self,index,value):
		"""sets a parameter value"""
		if 0<index<=80:
			self.logger = logging.getLogger(get_all_caller())
			self.logger.debug("Setting Par %s to %s" %(int(index),int(value)))
			self.adw.Set_Par(int(index),int(value))
		else:
			self.logger.error('The Parameter number %s is out of range(0,81)' %index)
		
	def set_datalong(self,array,arr_num,start_index=1):
		"""sets a data array"""
		if 0<arr_num<=200:
			c_array=(ctypes.c_long * len(array))(0)
			array=array.astype('int')
			for i in range(len(array)):
				c_array[i]=array[i]
			self.logger = logging.getLogger(get_all_caller())
			self.logger.debug("Set data array %s with length %s" %(arr_num,len(array)))
			self.logger.debug("Set data array %s to %s" %(arr_num,array))
			self.adw.SetData_Long(c_array, int(arr_num), int(start_index), len(array))
		else:
			self.logger.error('The array number %s is out of range(0,201)' %(arr_num))
		
	def get_par_all(self):
		"""gets all the parameter from adwin"""
		self.logger = logging.getLogger(get_all_caller())
		self.logger.debug("Getting all Pars")
		return self.adw.Get_Par_All()
		
	def get_par(self,index):
		"""gets a parameter from adwin"""
		if 0<index<=80:
			self.logger = logging.getLogger(get_all_caller())
			self.logger.debug("Getting Par %s" %int(index))
			return self.adw.Get_Par(int(index))
		else:
			self.logger.error('The Parameter number %s is out of range(0,81)' %index)
			return -1
		
	def get_data(self,number,length,start=1):
		"""gets a array from adwin"""
		if 0<number<=200:
			self.logger = logging.getLogger(get_all_caller())
			self.logger.debug("Getting Data %s from index %s to %s" %(number,start,start+length))
			return self.adw.GetData_Long(number,start,length)
		else:
			self.logger.error('The array number %s is out of range(0,201)' %(number))

	def get_fifo(self,number,length='all'):
		"""gets a fifo array from adwin"""
		self.logger = logging.getLogger(get_all_caller())
		if 0<number<=200:
			if length=='all':
				length = self.adw.Fifo_Full(number)
			if 0<self.adw.Fifo_Full(number) >= length:
				cdata = self.adw.GetFifo_Long(number,int(length))
				data=[]
				for i in range(len(cdata)):
					data.append(cdata[i])
				self.logger.debug("Getting FIFO %s with length %s" %(number,length))
				return np.array(data)
			else:
				self.logger.warning('not enough elements in the fifo array')
				return np.array([])
		else:
			self.logger.error('The fifo number %s is out of range(0,201)' %(number))

	def get_timetrace_static(self,detect,duration=1,acc=None):
		"""gets the timetrace data from the adwin with the duration in seconds
			and the accuracy in seconds"""
		if not type(detect)== type([]):
			detect = list(detect)
		self.logger = logging.getLogger(get_all_caller())
		if acc!=None:
			self.adw.Set_Processdelay(self.proc_num, m.floor(acc/25e-9))
		delay = self.adw.Get_Processdelay(self.proc_num) 
		self.logger.info('Making static timetrace with %s for %ss and precision of %ss' %(', '.join([ i.properties['Name'] for i in detect ]),duration,acc))
		num_ticks = int(duration / (delay * 25e-9))
		#self.set_par(par.properties['Dev_type'],int(detect.properties['Type'][:5],36))
		#self.set_par(par.properties['Port'],detect.properties['Input']['Hardware']['PortID'])
		dev_params = np.array([])
		for i in detect:
			dev_params = np.append(dev_params,[int(i.properties['Type'][:5],36),i.properties['Input']['Hardware']['PortID']])
		self.set_datalong(dev_params,data.properties['dev_params'])
		self.set_par(par.properties['Num_devs'],len(detect))
		self.set_par(par.properties['Num_ticks'],num_ticks)
		self.set_par(par.properties['Case'],3)
		self.start()
		self.wait()
		array = np.array(list(self.get_fifo(fifo.properties['Scan_data'])))
		split_data = []
		for i in range(len(detect)):
			split_data.append(array[i::len(detect)])
		index = np.arange(num_ticks)*(delay*25e-9)
		return split_data,index
	
	def get_timetrace_dynamic(self,detect,duration=1,acc=0.01):
		"""gets the timetrace data from the adwin with the duration in seconds
			and the accuracy in seconds"""
		if not type(detect) == type([]):
			detect = list(detect)
		self.logger = logging.getLogger(get_all_caller())
		if not self.running:
			self.logger.info('Making dynamic timetrace with %s' %', '.join([ i.properties['Name'] for i in detect ])) 
			self.logger.info('for %ss and precision of %ss' %(duration,acc))
			self.adw.Set_Processdelay(self.proc_num, m.floor(acc/25e-9))
			num_ticks = int(duration / (acc))
			#self.set_par(par.properties['Dev_type'],int(detect.properties['Type'][:5],36))
			#self.set_par(par.properties['Port'],detect.properties['Input']['Hardware']['PortID'])
			dev_params = np.array([])
			for i in detect:
				dev_params = np.append(dev_params,[int(i.properties['Type'][:5],36),i.properties['Input']['Hardware']['PortID']])
			self.set_datalong(dev_params,data.properties['dev_params'])
			self.set_par(par.properties['Num_devs'],len(detect))
			self.set_par(par.properties['Num_ticks'],num_ticks)
			self.set_par(par.properties['Case'],3)
			self.start()
			self.running = bool(self.adw.Process_Status(self.proc_num))
			self.array = np.array(list(self.get_fifo(fifo.properties['Scan_data'])))
			split_data = []
			for i in range(len(detect)):
				length = np.floor(len(self.array)/len(detect))*len(detect)
				split_data.append(self.array[i:length:len(detect)])
			self.excess_data = self.array[length:] or np.array([])
			return split_data
		
		elif self.running:
			self.logger.debug('Getting data from danamic timetrace')
			split_data = []
			self.array = np.array(list(self.get_fifo(fifo.properties['Scan_data'])))
			try:
				image = np.append(self.excess_data,image)
			except:
				pass
			for i in range(len(detect)):
				length = np.floor(len(self.array)/len(detect))*len(detect)
				split_data.append(self.array[i:length:len(detect)])
			self.excess_data = self.array[length:] or np.array([])
			return split_data
		
	def dac(self,channel,value,unit=None):
		"""uses dac to convert the value into a voltage 
		0 = -10V, 32768= 0V	 and 65536 = 9.999695V"""
		self.logger = logging.getLogger(get_all_caller())
		if not unit==None:
			value = int((value-3278)/6553.6)
		if 0<=value<=65536 and 0<=channel<=15:
			self.logger.debug('Dac of %s to %sV' %(value,(value-3278)/6553.6))
			self.set_par(par.properties['Port'],channel)
			self.set_par(par.properties['Input_value'],value)
			self.set_par(par.properties['Case'],1)
			self.start()
			self.wait()
		elif 0<=channel<=15:
			self.logger.error('The value %s is out of range(0,65537)'%value)
		else:
			self.logger.error('The channel %s us out of range(0,16)'%channel)
			
	def adc(self,channel,gain=1):
		"""uses adc to convert a voltage into a value
		   0  = -10V/gain, 32768= 0V  and 65536 = 9.999695V/gain """
		self.logger = logging.getLogger(get_all_caller())
		if 0<=channel<=15:
			self.logger.debug('Converting analog signal from channel %s'%channel)
			self.set_par(par.properties['Port'],channel)
			self.set_par(par.properties['Input_value'],gain)
			self.set_par(par.properties['Case'],2)
			self.start()
			self.wait()
			return self.get_par(par.properties['Output_value'])
		else:
			self.logger.error('The channel %s is out of range(0,16)' %channel)
	
	def set_device_value(self,dev,value):
		"""sets a value to the device"""
		self.logger = logging.getLogger(get_all_caller())
		self.dev_value[dev.properties['Name']] = value
		calibration=dev.properties['Output']['Calibration']
		port = dev.properties['Output']['Hardware']['PortID']
		value = int((value-calibration['Offset'])/calibration['Slope'])
		max = dev.properties['Output']['Limits']['Max']
		min = dev.properties['Output']['Limits']['Min']
		if (min < value < max):
			self.logger.debug('Setting value to device %s' %dev.properties['Name'])
			self.dac(port,value)
		else:
			self.logger.error('Value exceeded boundaries of device %s' %dev.properties['Name'])
			self.logger.error('Value %s is out of range(%s,%s)' %(value,min,max))
		
	def get_digin(self,port):
		""" Gets the value of the digin port"""
		self.logger = logging.getLogger(get_all_caller())
		if 0<=port<16:
			self.logger.info('Getting data from digital port %s' %port)
			self.set_par(par.properties['Case'],5)
			self.start()
			self.wait()
			digin_data = self.get_par(par.properties['Output_value'])
			digin_data = bin(digin_data)[2:]
			digin_data = '0'*(16-len(digin_data)) + digin_data
			return int(digin_data[-port-1])
		else:
			self.logger.error('The port %s is out of range(0,16)' %port)

	def set_digout(self,port):
		""" Sets the digout port to 1"""
		self.logger = logging.getLogger(get_all_caller())
		if 0<=port<16:
			self.logger.debug('Setting digital port %s to 1' %port)
			self.set_par(par.properties['Case'],6)
			self.set_par(par.properties['Port'],port)
			self.start()
			self.wait()
		else:
			self.logger.error('The port %s is out of range(0,16)' %port)
			
		
	def clear_digout(self,port):
		""" Sets the digout port to 0"""
		self.logger = logging.getLogger(get_all_caller())
		if 0<=port<16:
			self.logger.debug('Setting digital port %s to 0' %port)
			self.set_par(par.properties['Case'],7)
			self.set_par(par.properties['Port'],port)
			self.start()
			self.wait()
		else:
			self.logger.error('The port %s is out of range(0,16)' %port)

	def scan_static(self,detect,devs,center,dims,accuracy,speed=10):
		""" A function that does a scan. The number of axes you can choose yourself.
		detect: a device that does the detection of your signal
		devs: array devices which you are using, 
		center: array of starting piont of the center (unit of the device),
		dims: array of the dimensions (unit of the device),
		accuracy: array of accuracy value (unit of the device),
		speed: the duration of one pixel (ms)
        """
		self.logger = logging.getLogger(get_all_caller())
		devs = np.array(devs)
		center = np.array(center)
		dims = np.array(dims)
		accuracy = np.array(accuracy)
		if not type(detect) == type([]):
			detect = [detect]
		if len(devs)==len(center)==len(dims)==len(accuracy)<=3:
			port=np.zeros(3)
			pix=(np.array(dims)/np.array(accuracy)).astype('int')
			increment=np.zeros(3)
			start=-np.ones(3)
			self.logger.info('Making a static scan')
			for i in range(len(devs)):
				port[i]=devs[i].properties['Output']['Hardware']['PortID']
				calibration=devs[i].properties['Output']['Calibration'] 
				start[i]=(center[i]-calibration['Offset']-dims[i]/2)/calibration['Slope']
				increment[i]=accuracy[i]/calibration['Slope']
				min = devs[i].properties['Output']['Limits']['Min'] 
				max = devs[i].properties['Output']['Limits']['Max'] 
				if (start[i]<min or max<start[i]+pix[i]*increment[i]):
					self.logger.error('Error boundaries of device %s exceeded' %devs[i].properties['Name'])
					self.logger.error('Value %s is out of range(%s,%s)' %(start[i],min,max))
					raise ValueError('Boundaries exceded')
				self.logger.info('Range(%s,%s) for device %s' %(center[i]-dims[i]/2,center[i]+dims[i]/2,devs[i]))
				self.scan_settings[devs[i].properties['Name']+'_start']=center[i]-dims[i]/2
				self.scan_settings[devs[i].properties['Name']+'_accuracy']=accuracy[i]
			#self.set_par(par.properties['Port'],detect.properties['Input']['Hardware']['PortID'])
			#self.set_par(par.properties['Dev_type'],int(detect.properties['Type'][:5],36))
			dev_params = np.array([])
			for i in detect:
				dev_params = np.append(dev_params,[int(i.properties['Type'][:5],36),i.properties['Input']['Hardware']['PortID']])
			self.set_datalong(dev_params,data.properties['dev_params'])
			self.set_par(par.properties['Num_devs'],len(detect))
			pix=np.append(pix,np.ones(3-len(pix)))		  
			self.set_datalong(np.append((port,start,pix),increment),data.properties['Scan_params'])
			total=int(np.prod(pix))
			self.set_par(par.properties['Case'],4)
			self.adw.Set_Processdelay(self.proc_num, int(speed*1e-3/25e-9))
			self.start()
			while self.adw.Process_Status(self.proc_num):
				number = self.get_par(par.properties['Pix_done'])
				perc = int(number/total*100)
				stdout.write("\r{0:d}%".format(perc))
				stdout.flush()
				time.sleep(0.5)
			print("")
			temp = np.array(list(self.get_fifo(fifo.properties['Scan_data'], total)))
			self.scan_image = []
			for i in range(len(detect)):
				self.scan_image.append(np.squeeze(temp[i::len(detect)].reshape((pix[::-1]))/(speed*1e-3)))
			return self.scan_image
		else:
			self.logger.error("Not all input arrays have the same length or are longer the 3")
			raise InputError("Not all input arrays have the same length or are longer the 3")
			return False

	def scan_dynamic(self,detect,devs,center,dims,accuracy,speed=10):
		"""a function that does a scan. The number of axes you can choose yourself.
		detect: a device(s) that does the detection of your signal
		devs: array devices which you are using, 
		center: array of starting piont of the center (unit of the device),
		dims: array of the dimensions (unit of the device),
		accuracy: array of accuracy value (unit of the device),
		speed: the duration of one pixel (ms)"""
		self.logger = logging.getLogger(get_all_caller())
		if not self.running:
			devs = np.array(devs)
			center = np.array(center)
			dims = np.array(dims)
			accuracy = np.array(accuracy)
			if not type(detect) == type([]):
				detect = [detect]
			if len(devs)==len(center)==len(dims)==len(accuracy)<=3:
				self.logger.info('Making a dynamic scan')
				port=np.zeros(3)
				pix=(np.array(dims)/np.array(accuracy)).astype('int')
				increment=np.zeros(3)
				start=-np.ones(3)
				for i in range(len(devs)):
					port[i]=devs[i].properties['Output']['Hardware']['PortID']
					calibration=devs[i].properties['Output']['Calibration'] 
					start[i]=(center[i]-calibration['Offset']-dims[i]/2)/calibration['Slope']
					increment[i]=int(accuracy[i]/calibration['Slope'])
					min = devs[i].properties['Output']['Limits']['Min'] 
					max = devs[i].properties['Output']['Limits']['Max'] 
					if (start[i]<min or max<start[i]+pix[i]*increment[i]):
						self.logger.error('Error boundaries of device %s exceeded' %devs[i].properties['Name'])
						self.logger.error('Value %s is out of range(%s,%s)' %(start[i],min,max))
						return False
					self.logger.info('Range(%s,%s) for device %s' %(center[i]-dims[i]/2,center[i]+dims[i]/2,devs[i].properties['Name']))
					self.scan_settings[devs[i].properties['Name']+'_start']=center[i]-dims[i]/2
					self.scan_settings[devs[i].properties['Name']+'_accuracy']=accuracy[i]
				#self.set_par(par.properties['Port'],detect.properties['Input']['Hardware']['PortID'])
				#self.set_par(par.properties['Dev_type'],int(detect.properties['Type'][:5],36))
				dev_params = np.array([])
				for i in detect:
					dev_params = np.append(dev_params,[int(i.properties['Type'][:5],36),i.properties['Input']['Hardware']['PortID']])
				self.set_datalong(dev_params,data.properties['dev_params'])
				self.set_par(par.properties['Num_devs'],len(detect))
				self.pix=np.append(pix,np.ones(3-len(pix)))	   
				self.set_datalong(np.append((port,start,self.pix),increment),data.properties['Scan_params'])
				total=int(np.prod(self.pix))
				self.set_par(par.properties['Case'],4)
				self.adw.Set_Processdelay(self.proc_num, int(speed*1e-3/25e-9))
				self.start()
				time.sleep(0.1)
				self.running = bool(self.adw.Process_Status(self.proc_num))
				temp = np.zeros(total)
				temp[:] = np.nan
				image = self.get_fifo(fifo.properties['Scan_data'])
				self.scan_image = []
				for i in range(len(detect)):
					index = np.isnan(temp).argmax()
					length = np.min((len(temp[index:])*len(detect),np.floor(len(image)/len(detect))*len(detect)))
					temp[index:index+length/len(detect)] = image[i:length:len(detect)]
					self.scan_image.append(np.squeeze(temp.reshape((self.pix[::-1]))))
					temp = np.zeros(total)
					temp[:]=np.nan
				self.excess_data = image[length:] or np.array([])
				return self.scan_image
			
			else:
				self.logger.error("Not all input arrays have the same length or are longer the 3")
				return False
			
		elif self.running:
			self.logger.debug('Getting data from danamic scan')
			image = self.get_fifo(fifo.properties['Scan_data'])
			try:
				image = np.append(self.excess_data,image)
			except:
				pass
			for i in range(len(detect)):
				temp = self.scan_image[i].flatten()
				index = np.isnan(temp).argmax()
				length = np.min((len(temp[index:])*len(detect),np.floor(len(image)/len(detect))*len(detect)))
				temp[index:index+length/len(detect)] = image[i:length:len(detect)]
				self.scan_image[i] = np.squeeze(temp.reshape((self.pix[::-1])))
			self.excess_data = image[length:]
			return self.scan_image
			

				
	def find(self, image, fwhm, hmin=None, nsigma=1.5, roundlim=[-1.,1.], sharplim=[0.2,1.]):
		"""Identifies stars in an image

		ASTROLIB-routine
		
		Returns a list [x, y, flux, sharpness, roundness].

	 INPUTS:
	
		image -- 2D array containing the image
		hmin -- Minimum threshold for detection. Should be 3-4 sigma above background RMS.
		fwhm -- FWHM to be used for the convolution filter. Should be the same as the PSF FWHM.
		nsigma --: radius of the convolution kernel. (default: 1.5)
		roundlim -- Threshold for the roundness criterion. (default: [-1,1])
		sharplim -- Threshold for the sharpness criterion. (default: [0.2,1])

	 OUTPUT:

		x -- vector of x positions of maxima in image
		y -- vector of y positions of maxima in image
		flux -- vector of flux of maxima in image
		sharpness -- vector of sharpness of maxima in image
		roundness -- vector of roundness of maxima in image
	
	 EXAMPLE:	
		>>> import pyfits
		>>> import sp.find as find
		>>> image = pyfits.getdata('test.fits')
		>>> dim_y, dim_x = image.shape
		>>> [x, y, flux, sharpness, roundness] = find(image, 15, 5.)
		"""
		###
		# Setting the convolution kernel
		###
		self.logger = logging.getLogger(get_all_caller())
		
		if hmin==None:
			std = np.std(image)
			median = np.median(image)
			hmin = median + 3*std
		sigmatofwhm = 2*np.sqrt(2*np.log(2))
		radius = nsigma * fwhm / sigmatofwhm # Radius is 1.5 sigma
		if radius < 1.0:
			radius = 1.0
			fwhm = sigmatofwhm/nsigma
			self.logger.warning("Radius of convolution box smaller than one." )
			self.logger.warning("Setting the 'fwhm' to minimum value %f" %fwhm )
		sigsq = (fwhm/sigmatofwhm)**2 # sigma squared
		nhalf = int(radius) # Center of the kernel
		nbox = 2*nhalf+1 # Number of pixels inside of convolution box
		middle = nhalf # Index of central pixel
		self.logger.info('Attempt to find particles')
		self.logger.info('With fwhm = %s, hmin = %s, nsigma = %s,' %(fwhm,hmin,nsigma)) 
		self.logger.info('roundlim = %s, sharplim = %s' %(roundlim,sharplim))
		kern_y, kern_x = np.ix_(np.arange(nbox),np.arange(nbox)) # x,y coordinates of the kernel
		g = (kern_x-nhalf)**2+(kern_y-nhalf)**2 # Compute the square of the distance to the center
		mask = g <= radius**2 # We make a mask to select the inner circle of radius "radius"
		nmask = mask.sum() # The number of pixels in the mask within the inner circle.
		g = np.exp(-0.5*g/sigsq) # We make the 2D gaussian profile
	
		###
		# Convolving the image with a kernel representing a gaussian (which is assumed to be the psf)
		###
		c = g*mask # For the kernel, values further than "radius" are equal to zero
		c[mask] = (c[mask] - c[mask].mean())/(c[mask].var() * nmask) # We normalize the gaussian kernel
	
		c1 = g[nhalf] # c1 will be used to the test the roundness
		c1 = (c1-c1.mean())/((c1**2).sum() - c1.mean())
		h = scipy.ndimage.convolve(image,c,mode='constant',cval=0.0) # Convolve image with kernel "c"
		h[:nhalf,:] = 0 # Set the sides to zero in order to avoid border effects
		h[-nhalf:,:] = 0
		h[:,:nhalf] = 0
		h[:,-nhalf:] = 0
	
		mask[middle,middle] = False # From now on we exclude the central pixel
		nmask = mask.sum() # so the number of valid pixels is reduced by 1
		goody,goodx = mask.nonzero() # "good" identifies position of valid pixels
		
		###
		# Identifying the point source candidates that stand above the background
		###
		indy,indx = (h >= hmin).nonzero() # we identify point that are above the threshold, image coordinate
		nfound = indx.size # nfound is the number of candidates
		if nfound <= 0:
			self.logger.error("There is no source meeting the 'hmin' criterion." )
			self.logger.error("Aborting the 'find' function." )
			return None
		offsetsx = np.resize(goodx-middle,(nfound,nmask)) # a (nfound, nmask) array of good positions in the mask, mask coordinate
		offsetsx = indx + offsetsx.T # a (nmask, nfound) array of positions in the mask for each candidate, image coordinate
		offsetsy = np.resize(goody-middle,(nfound,nmask)) # a (nfound, nmask) array of good positions in the mask, mask coordinate
		offsetsy = indy + offsetsy.T # a (nmask, nfound) array of positions in the mask for each candidate, image coordinate
		offsets_vals = h[offsetsy,offsetsx] # a (nmask, nfound) array of mask values roundness each candidate
		vals = h[indy,indx] # a (nfound) array of the intensity of each candidate
	
		###
		# Identifying the candidates that are local maxima
		###
		ind_goodcandidates = ((vals - offsets_vals) > 0).all(axis=0) # a (nfound) array identifying the candidates whose values are above the mask (i.e. neighboring) pixels, candidate coordinate
		nfound = ind_goodcandidates.sum() # update the number of candidates
		if nfound <= 0:
			self.logger.error("There is no source meeting the 'hmin' criterion that is a local maximum." )
			self.logger.error("Aborting the 'find' function." )
			return None
		indx = indx[ind_goodcandidates] # a (nfound) array of x indices of good candidates, image coordinate
		indy = indy[ind_goodcandidates] # a (nfound) array of y indices of good candidates, image coordinate
	
		 ###
		# Identifying the candidates that meet the sharpness criterion
		###
		d = h[indy,indx] # a (nfound) array of the intensity of good candidates
		d_image = image[indy,indx] # a (nfound) array of the intensity of good candidates in the original image (before convolution)
		offsetsx = offsetsx[:,ind_goodcandidates] # a (nmask, nfound) array of positions in the mask for each candidate, image coordinate
		offsetsy = offsetsy[:,ind_goodcandidates] # a (nmask, nfound) array of positions in the mask for each candidate, image coordinate
		offsets_vals = image[offsetsy,offsetsx]
		sharpness = (d_image - offsets_vals.sum(0)/nmask) / d
		ind_goodcandidates = (sharpness > sharplim[0]) * (sharpness < sharplim[1]) # a (nfound) array of candidates that meet the sharpness criterion
		nfound = ind_goodcandidates.sum() # update the number of candidates
		if nfound <= 0:
			self.logger.error("There is no source meeting the 'sharpness' criterion." )
			self.logger.error("Aborting the 'find' function." )
			return None
		indx = indx[ind_goodcandidates] # a (nfound) array of x indices of good candidates, image coordinate
		indy = indy[ind_goodcandidates] # a (nfound) array of y indices of good candidates, image coordinate
		sharpness = sharpness[ind_goodcandidates] # update sharpness with the good candidates
	
		###
		# Identifying the candidates that meet the roundness criterion
		###
		temp = np.arange(nbox)-middle # make 1D indices of the kernel box
		temp = np.resize(temp, (nbox,nbox)) # make 2D indices of the kernel box (for x or y)
		offsetsx = np.resize(temp, (nfound,nbox,nbox)) # make 2D indices of the kernel box for x, repeated nfound times
		offsetsy = np.resize(temp.T, (nfound,nbox,nbox)) # make 2D indices of the kernel box for y, repeated nfound times
		offsetsx = (indx + offsetsx.swapaxes(0,-1)).swapaxes(0,-1) # make it relative to image coordinate
		offsetsy = (indy + offsetsy.swapaxes(0,-1)).swapaxes(0,-1) # make it relative to image coordinate
		offsets_vals = image[offsetsy,offsetsx] # a (nfound, nbox, nbox) array of values (i.e. the kernel box values for each nfound candidate)
		dx = (offsets_vals.sum(2)*c1).sum(1)
		dy = (offsets_vals.sum(1)*c1).sum(1)
		roundness = 2*(dx-dy)/(dx+dy)
		ind_goodcandidates = (roundness > roundlim[0]) * (roundness < roundlim[1]) * (dx >= 0.) * (dy >= 0.) # a (nfound) array of candidates that meet the roundness criterion
		nfound = ind_goodcandidates.sum() # update the number of candidates
		if nfound <= 0:
			self.logger.error("There is no source meeting the 'roundness' criterion." )
			self.logger.error("Aborting the 'find' function." )
			return None
		indx = indx[ind_goodcandidates] # a (nfound) array of x indices of good candidates, image coordinate
		indy = indy[ind_goodcandidates] # a (nfound) array of y indices of good candidates, image coordinate
		sharpness = sharpness[ind_goodcandidates] # update sharpness with the good candidates
		roundness = roundness[ind_goodcandidates] # update roundness with the good candidates
		offsets_vals = offsets_vals[ind_goodcandidates] # update offsets_vals with good candidates
		offsetsx = offsetsx[ind_goodcandidates]
		offsetsy = offsetsy[ind_goodcandidates]
	
		###
		# Recenter the source position and compute the approximate flux
		###
		c = np.empty((nfound,2), dtype=float)
		for i in range(nfound):
			c[i] = scipy.ndimage.center_of_mass(offsets_vals[i])
		x = c[:,1]+indx-middle
		y = c[:,0]+indy-middle
		flux = h[indy,indx]
 
		return np.array([x, y, flux, sharpness, roundness])
	
	def focus_full(self, detect, devs, center, dims_default, accuracy_default, rate=1, steps=3, speed=50):
		self.logger = logging.getLogger(get_all_caller())
		devs = np.array(devs)
		center = np.array(center)
		dims = copy.copy(dims_default)
		accuracy = copy.copy(accuracy_default)
		for i in range(len(devs)):
			self.set_device_value(devs[i],center[i])
		if len(devs)==len(center)==len(dims)==len(accuracy):
			self.logger.info('Focus on a particle with detector %s'%detect.properties['Name'])
			self.logger.info('At the position %s' %center)
			for i in range(steps):
				for j in range(len(devs)):
					self.scan_static(detect,[devs[j]],[center[j]],[dims[j]],[accuracy[j]],speed)
					center[j] = center[j] - dims[j]/2 + (self.scan_image[0][1:].argmax()+1)*accuracy[j]
					self.set_device_value(devs[j],center[j])
					dims[j] /= rate
					accuracy[j] /= rate
					self.logger.info('At the position %s' %center)
			values = []
			for i in range(len(devs)):
				values.append(self.dev_value[devs[i].properties['Name']])
			return np.array(values)
		else:
			self.logger.error('Dimensions of the arrays do not match')
			return np.array([])
			   
	def go_to_position(self, devs, center):
		self.logger = logging.getLogger(get_all_caller())
		devs = np.array(devs)
		center = np.array(center)
		if len(devs)==len(center):
			for i in range(len(devs)):
				self.logger.info('Go to the specified position')
				self.logger.info('Device %s to %s' %(devs[i].properties['Name'],center[i]))
				self.set_device_value(devs[i],center[i])
		else:
			self.logger.error('Dimensions of the arrays do not match')
			
class inter_add_remove():
	def __init__(self,plot_parti,plot_backg,particles=None):
		self.logger = logging.getLogger(get_all_caller())
		self.logger.info('Starting intecactive add/remove particles')
		self.plot_parti=plot_parti
		self.plot_backg=plot_backg
		try:
			self.particles_x=particles[0,:]
			self.particles_y=particles[1,:]
		except:
			if particles!=None:
				self.logger.warning("input incorrect no particles plotted")
			self.particles_x = np.array([])
			self.particles_y = np.array([])
		self.back_x = np.array([])
		self.back_y = np.array([])
		self.cid = plot_parti.figure.canvas.mpl_connect('button_press_event', self)
	
	def __call__(self, event):
		if event.button==2:
			self.particles = np.vstack((self.particles_x,self.particles_y))
			self.background = np.vstack((self.back_x,self.back_y))
			plt.close()
			return
		if event.inaxes!=self.plot_parti.axes:
			self.logger.info('Done intecactive add/remove particles')
			return
		if event.button==1 and event.key==None and event.dblclick==True:
			self.particles_x=np.append(self.particles_x,event.xdata)
			self.particles_y=np.append(self.particles_y,event.ydata)
			self.logger.debug('Added a particle')
		elif event.button==3 and event.key==None and event.dblclick==True:
			if (((self.particles_x-event.xdata)**2+(self.particles_y-event.ydata)**2)<25).any():
				index_min = ((self.particles_x-event.xdata)**2+(self.particles_y-event.ydata)**2).argmin()
				self.particles_x = np.delete(self.particles_x,index_min)
				self.particles_y = np.delete(self.particles_y,index_min)
				self.logger.debug('A particle was removed')
		elif event.button==1 and event.key=='alt+b' and event.dblclick==True:
			self.back_x = np.append(self.back_x,event.xdata)
			self.back_y = np.append(self.back_y,event.ydata)
			self.logger.debug('Added a background')
		elif event.button==3 and event.key=='alt+b' and event.dblclick==True:
			if (((self.back_x-event.xdata)**2+(self.back_y-event.ydata)**2)<25).any():
				index_min = ((self.back_x-event.xdata)**2+(self.back_y-event.ydata)**2).argmin()
				self.back_x = np.delete(self.back_x,index_min)
				self.back_y = np.delete(self.back_y,index_min)
				self.logger.debug('A background was removed')
		self.plot_backg.set_data(self.back_x, self.back_y)	
		self.plot_backg.figure.canvas.draw()	  
		self.plot_parti.set_data(self.particles_x, self.particles_y)
		self.plot_parti.figure.canvas.draw()


logger = logging.getLogger(get_all_caller())
"""initialize the variable names"""		
par=variables('Par')
fpar=variables('FPar')
data=variables('Data')
fifo=variables('Fifo')

"""This couple of lines are for checking if LabView (Uberscan) is running 
if not then we need to initialize port 7. Otherwise port 7 will change its output
to ~ -1.7V as soon as we set a other port."""
proc = psutil.process_iter()
name=None
for i in proc:
	try:
		if i.name == 'LabVIEW.exe':
			name = 'LabVIEW'
	except:
		pass
	
if name==None:
	init_port7=adq('init_port7.T99')
	init_port7.boot()
	init_port7.load()
	init_port7.start()
	init_port7.wait()
	logger.info('initialized port 7 to 0V')
	   

if __name__ == '__main__':
	adq=adq('adwin.T99') 
	print(par.properties)
	import matplotlib.image as mpimg
	img=mpimg.imread('find_test.png')
	img = np.array(img)[65:540,115:600,0]
	std = np.std(img)
	median = np.median(img)
	print(median+3* std)
	[x, y, flux, sharpness, roundness] = adq.find(img,40)
	print(x,y)
	print(sharpness,roundness)
	print(len(x))
	plt.set_cmap('gnuplot')
	plt.imshow(img,interpolation='none')
	plt.colorbar()
	plt.scatter(x, y, s=40**2, facecolor='none', edgecolor='r')
	plt.show()