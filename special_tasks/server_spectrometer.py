# server.py
import socket
import time
import pickle
# from .devices.acton import a500i as spectrometer
#from .devices import acton as spect

# create a socket object
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get local machine name
# It will bind to any incoming connection. It may be a good idea to think about authentication?

host = ''# socket.gethostname()
#TODO: Allow only connections from a certain IP on the network.
#TODO: It is not as versatile as username/password, but guarantees non unwanted
#TODO: interference.

port = 12345

# bind to the port
serversocket.bind((host, port))

# queue up to 1 requests
serversocket.listen(1)

while True:
    # establish a connection
    conn,addr = serversocket.accept()
    print("Got a connection from %s" % str(addr))
    data = conn.recv(8192)
    if not data:
        print('No data received')
        conn.close()
    else:
        data = pickle.loads(data) # This transforms data into a dictionary sent from the client
                                  # This is a risky operation since there is no validation of the connection, and pickle
                                  # Allows for arbitrary data execution.
        if data['type'] == 'move':
            wl = data['value']
            print('Going to %s'%data['value'])
            #spectrometer.goto(wl)
            msg = wl
        elif data['type'] == 'query':
            wl = spectrometer.getwl()
            msg = wl
        elif data['type'] == 'stop':
            # break
            msg = 'Stopped'
        else:
            msg = 'Unrecognized command'
        msg = pickle.dumps(msg)
        conn.sendall(msg)

conn.close()
