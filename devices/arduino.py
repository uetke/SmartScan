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
            ans = self.ser.readline().decode("utf-8").split('\t')
            flowcell_volts = float(ans[0])
            flowcell_int = int(ans[1])
        except:
            print("Problem flowcell temp")
            flowcell_volts = 0
            flowcell_int = 0
        return flowcell_volts,flowcell_int

    def close(self):
        self.ser.close()

if __name__ == "__main__":
    import time
    inst = arduino('COM7')
    for i in range(10):
        volts,fint = inst.get_flowcell_temp()
        print('%s\t%s '%(volts,fint))
        time.sleep(1)
    inst.close()
