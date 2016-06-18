from special_tasks.spectrometer import abort, trigger_spectrometer
from lib.adq_mod import *
from lib.xml2dict import device,variables
from time import sleep

# inizialize adwin
adw = adq(model='goldII')
adw.clear_digout(16)
print('trigger test')
trigger_spectrometer(adw,digin=2,digout=16,digcheck=3)
