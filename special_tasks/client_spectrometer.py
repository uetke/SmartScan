import socket
import pickle
import numpy as np


host = socket.gethostname()
port = 1234                   # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
msg = {'type': 'move','value':532}
#msg = b'Hello World'
msg = pickle.dumps(msg)
s.sendall(msg)
data = s.recv(8192)
s.close()
data = pickle.loads(data)
print('Received', repr(data))
print(type(data))
