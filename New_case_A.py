import cv2
from pynput import keyboard
from threading import Timer
from playsound import playsound

# Global state variables
r_tap_count = 0
f_tap_count = 0
mode_timer_r = None
mode_timer_f = None
mode_timeout = 0.3  # Time window for consecutive taps in seconds

# Path to sound file for chat mode
file_path = 'message-13716.mp3'

# Define actions for each mode based on the tap count and key
def trigger_action_r():
    global r_tap_count
    if r_tap_count == 1:
        print("Describe Mode Triggered!")
    elif r_tap_count == 2:
        print("Chat Mode Triggered!")
        playsound(file_path)
    r_tap_count = 0  # Reset tap count after handling

def trigger_action_f():
    global f_tap_count
    if f_tap_count == 1:
        print("Read Mode Triggered!")
    f_tap_count = 0  # Reset tap count after handling

# Keyboard event handlers
def on_press(key):
    global r_tap_count, f_tap_count, mode_timer_r, mode_timer_f
    try:
        if key.char == 'r':
            r_tap_count += 1  # Increment tap count
            # Restart the timer every time 'r' is pressed
            if mode_timer_r is not None:
                mode_timer_r.cancel()
            mode_timer_r = Timer(mode_timeout, trigger_action_r)
            mode_timer_r.start()
        elif key.char == 'f':
            f_tap_count += 1
            if mode_timer_f is not None:
                mode_timer_f.cancel()
            mode_timer_f = Timer(mode_timeout, trigger_action_f)
            mode_timer_f.start()
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.esc:  # Exit condition
        return False

def main_routine():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 30)
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()  # Start to listen on a separate thread

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Quit if 'q' is pressed
            break

    cap.release()
    cv2.destroyAllWindows()
    listener.stop()  # Stop listener when done

if __name__ == '__main__':
    main_routine()
