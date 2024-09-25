'''
Script that goes through the Raspberry Pi autofocus cycle manually 
and then takes a photo
'''
from picamera2 import Picamera2
import time
import RPi.GPIO as GPIO

# Set up GPIO
GPIO.setmode(GPIO.BCM)
BUTTON_PIN = 17  # Change this to the GPIO pin you're using
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize the camera
picam2 = Picamera2()
config = picam2.create_preview_configuration()
picam2.configure(config)
picam2.start()

def auto_focus_and_capture():
    print("Press the button to autofocus and capture an image.")
    
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            print("Button pressed. Starting autofocus...")
            
            # Start autofocus
            picam2.set_controls({"AfMode": 1, "AfTrigger": 1})
            
            # Wait for autofocus to complete (adjust this time if needed)
            time.sleep(2)
            
            # Capture metadata to check if autofocus is successful
            metadata = picam2.capture_metadata()
            if metadata['AfState'] == 0:
                print("Autofocus successful. Capturing image...")
                picam2.capture_file("autofocused_image.jpg")
                print("Image captured as 'autofocused_image.jpg'")
            else:
                print("Autofocus failed. Please try again.")
            
            # Wait for button release
            while GPIO.input(BUTTON_PIN) == GPIO.LOW:
                time.sleep(0.1)
        
        time.sleep(0.1)

try:
    auto_focus_and_capture()
except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    picam2.stop()
    GPIO.cleanup()