import gpiod
import time
import threading


chip = gpiod.Chip('gpiochip4')

button_desc = chip.get_line(2)
button_read = chip.get_line(3)

button_desc.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
button_read.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)



# GPIO chip and line numbers
CHIP = "gpiochip4"
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

def handle_button_2():
    global last_press_time, is_function_running
    
    with button_press_lock:
        if is_function_running:
            return
        
        current_time = time.time()
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

def handle_button_3():
    global is_function_running
    
    with button_press_lock:
        if is_function_running:
            return
        
        print("Button 3 pressed")
        is_function_running = True
        threading.Thread(target=read).start()

def main():
    chip = gpiod.Chip(CHIP)
    
    try:
        button_2 = chip.get_line(BUTTON_2_LINE)
        button_3 = chip.get_line(BUTTON_3_LINE)
        
        config = gpiod.LineRequest()
        config.request_type = gpiod.LINE_REQ_EV_FALLING_EDGE
        config.flags = gpiod.LINE_REQ_DIR_IN

        button_2.request(config)
        button_3.request(config)
        
        while True:
            event_2 = button_2.event_read()
            if event_2:
                handle_button_2()
            
            event_3 = button_3.event_read()
            if event_3:
                handle_button_3()
            
            time.sleep(0.01)  # Small delay to reduce CPU usage
            
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'button_2' in locals():
            button_2.release()
        if 'button_3' in locals():
            button_3.release()
        chip.close()

if __name__ == "__main__":
    main()
