'''
Script that goes through the Raspberry Pi autofocus cycle manually 
and then takes a photo
'''
from picamera2 import Picamera2
import time

# Initialize the camera
picam2 = Picamera2()
config = picam2.create_preview_configuration()
picam2.configure(config)
picam2.start()

def auto_focus_and_capture():
    print("Starting autofocus...")
    
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
        print("Autofocus failed.")

try:
    auto_focus_and_capture()
except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    picam2.stop()
    print("Camera stopped.")