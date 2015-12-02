import socket
import pickle
import numpy as np
import time

# host = '132.229.38.170'
# port = 12345                   # The same port as used by the server
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((host, port))
# msg = {'type': 'move','value':633}
# #msg = b'Hello World'
# msg = pickle.dumps(msg)
# s.sendall(msg)
# data = s.recv(8192)
# s.close()
# data = pickle.loads(data)
# print('Received', repr(data))
# print(type(data))

from special_tasks.spectrometer import client_spectrometer, trigger_spectrometer
from lib.adq_mod import *
print('Now trying with the client class')
client = client_spectrometer()
adw = adq()
client.goto(532)
trigger_spectrometer(adw)
client.goto(533)
trigger_spectrometer(adw)
client.goto(534)
trigger_spectrometer(adw)
client.goto(535)
trigger_spectrometer(adw)
