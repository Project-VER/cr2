import gpiod
import time
import threading

# GPIO chip and line numbers
CHIP = 'gpiochip4'
BUTTON_DESC_LINE = 2
BUTTON_READ_LINE = 3

# Timing constants
DEBOUNCE_TIME = 0.05  # 50ms debounce
DOUBLE_CLICK_TIME = 0.3  # 300ms for double-click detection

# Global variables
last_press_time = 0
is_function_running = False
button_press_lock = threading.Lock()
pending_click = False

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

def handle_button_desc():
    global last_press_time, is_function_running, pending_click
    
    current_time = time.time()
    if current_time - last_press_time < DOUBLE_CLICK_TIME:
        print("Double click detected")
        pending_click = False
        if not is_function_running:
            is_function_running = True
            threading.Thread(target=chat).start()
    else:
        print("First click detected, waiting for potential second click")
        pending_click = True
        last_press_time = current_time

def handle_button_read():
    global is_function_running
    
    if not is_function_running:
        print("Read button pressed")
        is_function_running = True
        threading.Thread(target=read).start()

def main():
    global pending_click, last_press_time
    chip = gpiod.Chip(CHIP)
    
    try:
        button_desc = chip.get_line(BUTTON_DESC_LINE)
        button_read = chip.get_line(BUTTON_READ_LINE)
        
        button_desc.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
        button_read.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
        
        last_desc_state = 1
        last_read_state = 1
        
        while True:
            desc_state = button_desc.get_value()
            read_state = button_read.get_value()
            
            if desc_state == 0 and last_desc_state == 1:
                handle_button_desc()
            
            if read_state == 0 and last_read_state == 1:
                handle_button_read()
            
            # Check for pending single click
            if pending_click and time.time() - last_press_time >= DOUBLE_CLICK_TIME:
                pending_click = False
                if not is_function_running:
                    print("Single click confirmed")
                    is_function_running = True
                    threading.Thread(target=desc).start()
            
            last_desc_state = desc_state
            last_read_state = read_state
            
            time.sleep(0.01)  # Small delay to reduce CPU usage
            
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'button_desc' in locals():
            button_desc.release()
        if 'button_read' in locals():
            button_read.release()
        chip.close()

if __name__ == "__main__":
    main()
