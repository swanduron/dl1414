# PROJECT CODE VENUE
This clock project bases on micropyhon pyb v1.0 and v1.1. By design, this clock is automatic synced by GPS and depends on DS3231 high level RTC chip.
When clock starts first, it will search GPS and try to sync the time info into DS3231.

# dl1414
This lib is used to drive DL1414 matrix, which has been delivered in to this project, please see other file

# ds3231
This is a base lib for DS3231 chip, it uses iic bus and can be access with a very simple way.

# BME280
This lib for driving BME280 sensor. This sensor use IIC bus and has very quickly probe periodic.