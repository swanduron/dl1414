import machine
import time
import _thread
# import bme280
from dl1414 import Dl1414
# from ds3231 import DS3231
from pyb import UART, LED, RTC
TIME_ZONE = 8

for i in range(4):
    LED(i+1).off()

DAY_OF_WEEK = {
    0:'MON',
    1:'TUE',
    2:'WED',
    3:'THU',
    4:'FRI',
    5:'SAT',
    6:'SUN'
}

TIME_TEMPLATE = '%s-%s-%s %s %s:%s:%s'
TEST_STRING = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()'
gps_synbit = '!'
time_buffer = ()
seen_sat = '0'
tick_counter = int(time.time())

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
                _hour = int(time_data[:2])
                _minute = int(time_data[2:4])
                _second = int(time_data[4:6])
                _year = int(year_data[4:6]) + 2000
                _month = int(year_data[2:4])
                _day = int(year_data[:2])
                _C = _year//100
                _y = _year%100
                _week = abs((_C//4 - 2*_C + _y + _y//4 + (26*(_month+1))//10 + _day - 1)%7)
                time_stamp = time.mktime((_year, _month, _day, _hour, _minute, _second, _week, 0)) + 8 * 3600
                time_buffer = time.localtime(time_stamp)
                gps_synbit = '@'
        except:
            gps_synbit = '!'
            time_buffer = ()
            uart_interface.write('$PSRF104')


uart_interface = UART(2, 9600)
display = Dl1414(1, 'Y1','Y2','Y3', display_length=24)
_thread.start_new_thread(gps_reader, (uart_interface,))

string_buffer = ''
for i in TEST_STRING:
    display.display_writer(string_buffer)
    string_buffer+=i
    if len(string_buffer) > 24:
        string_buffer = string_buffer[1:]
    time.sleep_ms(20)
display.move_content()

while True:
    time.sleep(0.1)
    if time_buffer:
        year, month, day, hour, minute, second, week, day_in_year = [zfill(i) for i in time_buffer]
        display_string = TIME_TEMPLATE % (year, month, day, DAY_OF_WEEK[int(week)]+gps_synbit, hour, minute, second)
        if time.time() - tick_counter > 5:
            display.move_content()
            display.slide_in('%s DAYS IN YEAR %s' % (day_in_year, year))
            time.sleep(3)
            tick_counter = time.time()
            display.move_content()
            display.slide_in(display_string)
        else:
            display.display_writer(display_string)
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