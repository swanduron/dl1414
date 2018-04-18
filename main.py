import machine
import time
import _thread
# import bme280
from dl1414 import Dl1414
# from ds3231 import DS3231
from pyb import UART, LED
TIME_ZONE = 8

for i in range(4):
    LED(i+1).off()

DAY_OF_WEEK = {
    1:'MON',
    2:'TUE',
    3:'WED',
    4:'THU',
    5:'FRI',
    6:'SAT',
    7:'SUN'
}

TIME_TEMPLATE = '%s-%s-%s %s %s:%s:%s'

gps_synbit = '!'
time_buffer = ()
seen_sat = '0'


def zfill(tbd_string, number=2):
    tbd_string = str(tbd_string)
    if len(tbd_string) < number:
        return '0' * (number - len(tbd_string)) + tbd_string
    else:
        return tbd_string

def gps_reader(uart_interface):
    global gps_synbit
    global time_buffer
    global seen_sat
    while True:
        gps_line = uart_interface.readline()
        try:
            gps_line = gps_line.decode()
            if '$GPRMC' in gps_line:
                gps_info_list = gps_line.split(',')
                time_data = gps_info_list[1]
                year_data = gps_info_list[-4]
                if not time_data:
                    gps_synbit = '!'
                    time_buffer = ()
                    continue
                hour = int(time_data[:2]) + TIME_ZONE
                minute = int(time_data[2:4])
                second = int(time_data[4:6])
                year = int(year_data[:2]) + 2000
                C = year//100
                y = year%100
                month = int(year_data[2:4])
                day = int(year_data[4:6])
                week = abs((C//4 - 2*C + y + y//4 + (26*(month+1))//10 + day - 1)%7)
                time_buffer = year, month, day, week, hour, minute, second, 0
                gps_synbit = '@'
        except:
            uart_interface.write('$PSRF104')


uart_interface = UART(2, 9600)
display = Dl1414(1, 'Y1','Y2','Y3', display_length=24)
_thread.start_new_thread(gps_reader, (uart_interface,))

while True:
    time.sleep(0.1)
    if time_buffer:
        year, month, day, week, hour, minute, second, unknown = [zfill(i) for i in time_buffer]
        display.display_writer(TIME_TEMPLATE % (year, month, day, DAY_OF_WEEK[int(week)]+gps_synbit, hour, minute, second))
    else:
        display.display_writer('LOSS CONNECTION WITH GPS')

# if __name__ == '__main__':
#     print('Simple for bme280')
#     i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))
#     bme = bme280.BME280(i2c=i2c)
#     print(bme.values)
#
#     print('Simple for DS3231')
#     ds = DS3231()
#     ds.DATE([17, 9, 1])
#     ds.TIME([10, 10, 10])
#
#     while True:
#         print('Date:', ds.DATE())
#         print('Time:', ds.TIME())
#         print('TEMP:', ds.TEMP())
#         time.sleep(5)