import gpiod
import time

chip = gpiod.Chip('gpiochip4')
button_desc = chip.get_line(2)
button_desc.request(consumer="Line", type=gpiod.LINE_REQ_EV_RISING_EDGE)

last_press_time = 0
press_count = 0
timeout = 2  # seconds

while True:
    if button_desc.event_wait(sec=1):
        event = button_desc.event_read()
        if event.type == gpiod.LineEvent.RISING_EDGE:
            current_time = time.time()
            if current_time - last_press_time > timeout:
                press_count = 1
            else:
                press_count += 1
            
            last_press_time = current_time
            
            if press_count == 1:
                time.sleep(0.5)  # Wait a bit to see if there's a second press
                if press_count == 1:
                    print("Desc")
            elif press_count == 2:
                print("Chat")
                press_count = 0
    
    # Reset press count if timeout is reached
    if time.time() - last_press_time > timeout:
        press_count = 0
