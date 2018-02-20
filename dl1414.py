try:
    from machine import Pin, SPI, RTC
except:
    from pyb import Pin, SPI, RTC
import time


class Dl1414(object):

    def __init__(self, spi=1, rclk=16, digit0=4, digit1=0, edge='right', display_length=20):
        self.char_mapping = {1: [1, 1], 2: [1, 0], 3: [0, 1], 4: [0, 0]}
        self.spi = SPI(spi, baudrate=3000000, polarity=0, phase=0, mode=SPI.MASTER)
        self.rclk = Pin(rclk, Pin.OUT)
        self.digit0 = Pin(digit0, Pin.OUT)
        self.digit1 = Pin(digit1, Pin.OUT)
        self.display_length = display_length
        self.edge = edge
        self.display_buffer = ''

        self.rclk.off()
        self.digit0.off()
        self.digit1.off()
        self.spi.write(b'\xff\xff')
        self.rclk.on()
        self.rclk.off()
        self.display_writer()

    def content_role(self, content):
        if len(content) < self.display_length:
            if self.edge == 'right':
                content = ' '*(self.display_length - len(content)) + content
            else:
                content = content + ' '*(self.display_length - len(content))
        elif len(content) > self.display_length:
            content = content[:self.display_length]
        else:
            pass
        return content

    def display_writer(self, content=''):
        content = self.content_role(content)
        if self.display_buffer == content:
            return None
        else:
            self.display_buffer = content
        working_content = []
        for word_id in range(len(content)):
            cal_id = word_id + 1
            display_id_raw = cal_id // 4
            char_id = cal_id % 4
            if char_id > 0:
                display_id = display_id_raw + 1
            else:
                display_id = display_id_raw
            if char_id == 0:
                char_id = 4
            working_content.append((content[word_id], 255 - (2 ** (display_id - 1)), char_id))

        for each_char in working_content:
            self.spi.write(b'\xff\x00')  # 拉高片选使得所有1414不可操作，避免之前数据的干扰
            self.rclk.on()
            self.rclk.off()
            self.spi.write(bytes([each_char[1], ord(each_char[0])]))  # 片选+目标字
            digit0_value, digit1_value = self.char_mapping[each_char[2]]
            self.digit0.value(digit0_value)
            self.digit1.value(digit1_value)
            self.rclk.on()
            self.rclk.off()

    def show_content(self, content, direction='left', duration=5000):
        content = self.content_role(content)
        time_base = duration//20
        if direction == self.edge:
            content = content.strip()
        if direction == 'left':
            for i in range(20):
                time.sleep_ms(time_base)
                content = (content+' ')[1:]
                self.display_writer(content)
        else:
            for i in range(20):
                time.sleep_ms(time_base)
                content = ' '+content[:20]
                self.display_writer(content)


if __name__ == '__main__':

    def zfill(tbd_string, number):
        tbd_string = str(tbd_string)
        if len(tbd_string) < number:
            return ' ' * (number - len(tbd_string)) + tbd_string
        else:
            return tbd_string


    time_info = time.localtime(a - 946656000) #a是当前时间戳，后面的数字是pby的时间偏移，这段代码是设置时间用的
    year, monty, day, hour, minute, second, week, yearday = [int(i) for i in time_info]
    rtc.datetime((year, monty, day, week, hour, minute, second, 0))

    while True:
        year, monty, day, week, hour, minute, second, msec = rtc.datetime()
        string = str(year) + '-' + zfill(monty, 2) + '-' + zfill(day, 2) + '  ' + zfill(hour, 2) + ':' + zfill(minute,2) + ':' + zfill(second, 2)
        c.display_writer(string)
        time.sleep(0.2)

