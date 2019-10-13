import time
import serial
import math
import decimal

class DataManager:
    #constructor
    def __init__(self):
        self.gps_port = "/dev/ttyACM3"
        self.ser_gps = serial.Serial(self.gps_port, baudrate=9600, timeout=0.5)
        self.dictionary = dict()

    def start(self):
        while True:
            self.read_gps()
            time.sleep(3)

    def read_gps(self):
            while True:
                data = self.ser_gps.readline()
                print(data)
                s = b' '
                if data[0:6] == b'$GNGGA':
                    s = data.decode().split(",")
                    print(s)
                    if s[12] != '0':
                        #print("no satellite data available")
                    	#time = s[1]
                    	#lat = s[2]
                    	#dirLat = s[3]
                    	#lon = s[4]
                    	#dirLon = s[5]
                    	numsat = s[6]
                        #print(s[6])
                    	#alt = s[9]
                    	#checksum = s[12]
                    	lat = float(s[2])
                        if s[3] == 'S':
                            lat = -lat
                        lon = float(s[4])
                        if s[5] == 'W':
                            lon = -lon
                        self.dictionary['time_gps'] = s[1]
                        self.dictionary['gps_y'] = self.dmm_to_dd(lat)
                        self.dictionary['gps_x'] = self.dmm_to_dd(lon)
                        print('gps_y = {}'.format(self.dictionary['gps_y']))
                        print('gps_x = {}'.format(self.dictionary['gps_x']))
                        alt = float(s[9])
                        self.dictionary['altitude_gps'] = alt
                    else:
                        print('NON SAT') 
    
    def dmm_to_dd(self,x):
        s1 = math.floor(x/100)
        s11 = (x-s1*100)/60
        x = s1 + s11
        print(x)
        return x
	
if __name__ == '__main__':
    data_obj = DataManager()
    data_obj.start()
