# Script for acquiring timetraces vs intensity manually
#
######################### M. Caldarola - April 2016
from __future__ import division
import time
from lib.adq_mod import *
from lib.xml2dict import device,variables
from datetime import datetime
import msvcrt
from winsound import Beep


# inizialize adwin
adw = adq(model='goldII')

n=0
print('Waiting for signal...')
while n <10:
    if adw.get_digin(0):
        print('measuring')
        Beep(840,200)
        time.sleep(0.1)
        n=n+1
        print('Waiting for signal...')

print('end')
