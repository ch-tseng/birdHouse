import sys
import Adafruit_DHT

class DHT:

    def __init__(self, type=11, pin=4):
        if (type==11):
            self.type = Adafruit_DHT.DHT11
        elif (type==22):
            self.type = Adafruit_DHT.DHT22
        elif (type==2302):
            self.type = Adafruit_DHT.AM2302
        else:
            print('usage 11 for DHT11, 22 for DHT22, 2302 for 2302')
            sys.exit(1)

        if (pin>0):
            self.pin = pin

    def getData(self):
        humidity, temperature = Adafruit_DHT.read_retry(self.type, self.pin) 

        if humidity is not None and temperature is not None:
            print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
            return (humidity, temperature)
        else:
            print('Failed to get reading. Try again!')
            sys.exit(1)

