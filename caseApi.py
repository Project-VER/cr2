'''
File: caseApi.py
Created Date: Monday, September 2nd 2024, 3:43:57 pm
Author: alex-crouch

Project Ver 2024
'''
import gpiod
import time

chip = gpiod.Chip('gpiochip4')
button_desc = chip.get_line(2)
button_read = chip.get_line(3)

button_desc.request(consumer="Line", type=gpiod.LINE_REQ_EV_RISING_EDGE)
button_read.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)

# Press to describe, hold to chat
while True:
    if button_desc.get_value() == 0:
        time.sleep(0.4)
        if button_desc.get_value() == 0:
            print('Chat')
            time.sleep(10)
        else:
            print('Desc')
            time.sleep(10)
    if button_read.get_value() == 0:
        print('Read')
        time.sleep(10)