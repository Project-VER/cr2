import gpiod
import time

# Initialize the GPIO chip and lines
chip = gpiod.Chip('gpiochip4')
button_desc = chip.get_line(2)
button_read = chip.get_line(3)

# Request the lines
button_desc.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
button_read.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)

# Variables to track button states and timings
last_desc_press = 0
desc_press_count = 0
debounce_time = 0.05  # 50 ms debounce time
double_click_time = 0.4  # 400 ms for double click detection

try:
    while True:
        # Check the read button
        if button_read.get_value() == 0:
            print("read")
            time.sleep(debounce_time)

        # Check the desc button
        if button_desc.get_value() == 0:
            current_time = time.time()
            if current_time - last_desc_press > debounce_time:
                if current_time - last_desc_press < double_click_time:
                    desc_press_count += 1
                    if desc_press_count == 2:
                        print("chat")
                        desc_press_count = 0
                else:
                    if desc_press_count == 1:
                        print("desc")
                    desc_press_count = 1

                last_desc_press = current_time
                time.sleep(debounce_time)

        # Check if we need to reset the desc_press_count
        if desc_press_count == 1 and time.time() - last_desc_press > double_click_time:
            print("desc")
            desc_press_count = 0

        time.sleep(0.01)  # Small delay to prevent CPU hogging

except KeyboardInterrupt:
    print("Program terminated by user")
finally:
    # Release the GPIO lines
    button_desc.release()
    button_read.release()
