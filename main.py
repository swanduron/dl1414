import machine
import time
import _thread
import bme280
from dl1414 import Dl1414
from ds3231 import DS3231
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

DAY_OF_WEEK_IN_DS = {
    1:'MON',
    2:'TUE',
    3:'WED',
    4:'THU',
    5:'FRI',
    6:'SAT',
    0:'SUN'
}

TIME_TEMPLATE = '%s-%s-%s %s %s:%s:%s'
TEST_STRING = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()'
gps_synbit = '!'
time_buffer = ()
seen_sat = '0'
tick_counter = int(time.time())

global_i2c = machine.I2C(2)


def ds_chip_sync(now_date, ds_ins):
    ds_timestamp = 0
    gps_timestamp = 0
    if gps_synbit == '@':
        ds_year, ds_month, ds_day = ds_ins.DATE()
        ds_year = ds_year + 2000
        ds_hour, ds_minute, ds_second = ds_ins.TIME()
        C = ds_year // 100
        y = ds_year % 100
        ds_week = abs((C // 4 - 2 * C + y + y // 4 + (26 * (ds_month + 1)) // 10 + ds_day - 1) % 7)
        ds_timestamp = time.mktime((ds_year, ds_month, ds_day, ds_hour, ds_minute, ds_second, ds_week, 0))
        try:
            gps_timestamp = time.mktime(now_date)
        except:
            pass
    if abs(gps_timestamp - ds_timestamp) > 15 and gps_synbit == '@':
        year, month, day, hour, minute, second, week, day_in_year = now_date
        ds_ins.DATE([year % 100, month, day])
        ds_ins.TIME([hour, minute, second])

def zfill(tbd_string, number=2):
    tbd_string = str(tbd_string)
    if len(tbd_string) < number:
        return '0' * (number - len(tbd_string)) + tbd_string
    else:
        return tbd_string


def get_day_in_year(year, month, day):
    days = 0
    monthes = [0, 31, 0, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if (year % 4 == 0 & year % 100 != 0) | (year % 400 == 0):
        monthes[2] = 29
    else:
        monthes[2] = 28
    for i in range(1,month):
        days += monthes[i]
    days += day
    return days


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
display = Dl1414(1, 'Y1', 'Y2', 'Y3', display_length=24)
ds_chip = DS3231(global_i2c)
_thread.start_new_thread(gps_reader, (uart_interface,))

bme = bme280.BME280(i2c=global_i2c)

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
    if time_buffer or True:
        if gps_synbit == '@':
            year, month, day, hour, minute, second, week, day_in_year = [zfill(i) for i in time_buffer]
            display_string = TIME_TEMPLATE % (
            year, month, day, DAY_OF_WEEK[int(week)] + gps_synbit, hour, minute, second)
        else:
            year, month, day = ds_chip.DATE()
            year = year + 2000
            C = year // 100
            y = year % 100
            hour, minute, second = ds_chip.TIME()
            week = abs((C // 4 - 2 * C + y + y // 4 + (26 * (month + 1)) // 10 + day - 1) % 7)
            day_in_year = get_day_in_year(year, month, day)
            year, month, day, hour, minute, second, week, day_in_year = [zfill(i) for i in (
                year, month, day, hour, minute, second, week, day_in_year)]
            display_string = TIME_TEMPLATE % (
            year, month, day, DAY_OF_WEEK_IN_DS[int(week)] + gps_synbit, hour, minute, second)
        if time.time() - tick_counter > 5:
            display.move_content()
            # display.slide_in('%s DAYS IN YEAR %s' % (day_in_year, year))
            bme_value = bme.values
            display.slide_in('%s_%s_%s' % (bme_value[0], bme_value[2], bme_value[1].upper()))
            time.sleep(3)
            tick_counter = time.time()
            display.move_content()
            display.slide_in(display_string)
            ds_chip_sync(time_buffer, ds_chip)
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