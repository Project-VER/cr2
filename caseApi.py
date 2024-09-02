import gpiod
import time
import threading

# GPIO chip and line numbers
CHIP = "gpiochip0"
BUTTON_2_LINE = 2
BUTTON_3_LINE = 3

# Timing constants
DEBOUNCE_TIME = 0.05  # 50ms debounce
DOUBLE_CLICK_TIME = 0.3  # 300ms for double-click detection

# Global variables
last_press_time = 0
is_function_running = False
button_press_lock = threading.Lock()

def read():
    global is_function_running
    print("Running read function")
    time.sleep(2)  # Simulating some work
    is_function_running = False

def desc():
    global is_function_running
    print("Running desc function")
    time.sleep(2)  # Simulating some work
    is_function_running = False

def chat():
    global is_function_running
    print("Running chat function")
    time.sleep(2)  # Simulating some work
    is_function_running = False

def handle_button_2(event):
    global last_press_time, is_function_running
    
    if is_function_running:
        return
    
    current_time = time.time()
    if event.type == gpiod.LineEvent.FALLING_EDGE:
        with button_press_lock:
            if current_time - last_press_time < DOUBLE_CLICK_TIME:
                print("Double click detected")
                is_function_running = True
                threading.Thread(target=chat).start()
            else:
                last_press_time = current_time
                time.sleep(DOUBLE_CLICK_TIME)
                if time.time() - last_press_time >= DOUBLE_CLICK_TIME:
                    print("Single click detected")
                    is_function_running = True
                    threading.Thread(target=desc).start()

def handle_button_3(event):
    global is_function_running
    
    if is_function_running:
        return
    
    if event.type == gpiod.LineEvent.FALLING_EDGE:
        with button_press_lock:
            print("Button 3 pressed")
            is_function_running = True
            threading.Thread(target=read).start()

def main():
    chip = gpiod.Chip(CHIP)
    
    button_2 = chip.get_line(BUTTON_2_LINE)
    button_3 = chip.get_line(BUTTON_3_LINE)
    
    button_2.request(consumer="button-2", type=gpiod.LINE_REQ_EV_FALLING_EDGE)
    button_3.request(consumer="button-3", type=gpiod.LINE_REQ_EV_FALLING_EDGE)
    
    try:
        while True:
            event_2 = button_2.event_wait(sec=1)
            if event_2:
                handle_button_2(event_2)
            
            event_3 = button_3.event_wait(sec=1)
            if event_3:
                handle_button_3(event_3)
            
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        button_2.release()
        button_3.release()

if __name__ == "__main__":
    main()
