"""
    arduino.py
    -------------
    General class for interfacing with the Arduino. 
    It is thought to read temperature from a Pt100 and a DH11
    AUTHOR: Aquiles Carattino
    EMAIL: carattino@physics.leidenuniv.nl

"""

import serial

class arduino():
    def __init__(self,port):
        self.ser = serial.Serial(port,9600,timeout=2)
    
    # Room Temp
    def get_room_temp(self):
        try:
            self.ser.write(b'1')
            room_temp = float(self.ser.readline().decode("utf-8"))
        except:
            print("Problem Room Temperature")
            room_temp = 0   
        return room_temp
    
     # Humidity
    def get_room_humidity(self): 
        try:
            self.ser.write(b'0')
            humidity = float(self.ser.readline().decode("utf-8"))
        except:
            print("Problem Humidity")
            humidity = 0
        return humidity

            
    # Flowcell Temp
    def get_flowcell_temp(self):
        try:
            self.ser.write(b'2')
            flowcell_temp = int(self.ser.readline().decode("utf-8"))
        except:
            print("Problem flowcell temp")
            flowcell_temp = 0
        return flowcell_temp
        
    def close(self):
        self.ser.close()