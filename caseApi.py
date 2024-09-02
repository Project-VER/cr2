import gpiod
import time
import threading

# Define GPIO chip and lines
chip = gpiod.Chip('gpiochip0')
button_read = chip.get_line(3)
button_desc_chat = chip.get_line(2)

# Configure the lines as input
config = gpiod.line_request()
config.request_type = gpiod.line_request.DIRECTION_INPUT
config.consumer = "gpio_handler"

button_read.request(config)
button_desc_chat.request(config)

# Function placeholders
def read():
    print("Running read function...")
    time.sleep(5)  # Simulate function execution time
    print("Read function complete.")

def desc():
    print("Running desc function...")
    time.sleep(2)  # Simulate function execution time
    print("Desc function complete.")

def chat():
    print("Running chat function...")
    time.sleep(3)  # Simulate function execution time
    print("Chat function complete.")

# To block other button presses during function execution
lock = threading.Lock()

# Timing and state tracking for double press
last_press_time = 0
double_press_threshold = 0.5  # 500ms for double press

def handle_button_read():
    if lock.acquire(blocking=False):
        try:
            read()
        finally:
            lock.release()

def handle_button_desc_chat():
    global last_press_time
    current_time = time.time()
    time_diff = current_time - last_press_time

    if time_diff < double_press_threshold:
        if lock.acquire(blocking=False):
            try:
                chat()
            finally:
                lock.release()
    else:
        last_press_time = current_time
        threading.Timer(double_press_threshold, lambda: trigger_desc_if_no_double()).start()

def trigger_desc_if_no_double():
    if time.time() - last_press_time >= double_press_threshold:
        if lock.acquire(blocking=False):
            try:
                desc()
            finally:
                lock.release()

def main():
    try:
        while True:
            # Polling the buttons
            if button_read.get_value() == 1:
                handle_button_read()

            if button_desc_chat.get_value() == 1:
                handle_button_desc_chat()
        time.sleep(0.1)  # Polling interval
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()
