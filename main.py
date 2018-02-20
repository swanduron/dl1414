import machine
import time

import bme280
from dl1414 import Dl1414
from ds3231 import DS3231

if __name__ == '__main__':
    print('Simple for bme280')
    i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))
    bme = bme280.BME280(i2c=i2c)
    print(bme.values)

    print('Simple for DS3231')
    ds = DS3231()
    ds.DATE([17, 9, 1])
    ds.TIME([10, 10, 10])

    while True:
        print('Date:', ds.DATE())
        print('Time:', ds.TIME())
        print('TEMP:', ds.TEMP())
        time.sleep(5)