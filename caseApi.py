import gpiod
import time

chip = gpiod.Chip('gpiochip4')

button_desc = chip.get_line(2)

#button_desc.request(consumer="Line", type=gpiod.LINE_REQ_EV_BOTH_EDGES)
button_desc.request(consumer="Line", type=gpiod.LINE_REQ_EV_RISING_EDGE)

while True:
	time.sleep(0.1)
	print(button_desc.get_value())
