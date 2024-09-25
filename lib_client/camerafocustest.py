#test focus script 


import time
from picamera2 import Picamera2
from libcamera import controls
import os

def auto_focus_and_capture():
    # Initialize the camera
    picam2 = Picamera2()
    config = picam2.create_still_configuration()
    picam2.configure(config)
    picam2.start()

    time.sleep(2)

    #directory to store the images
    os.makedirs("focus_test", exist_ok=True)

    try:
        # Define the range of focus values to try
        focus_values = [i/10 for i in range(11)]  # 0.0 to 1.0 in steps of 0.1

        for i, focus in enumerate(focus_values):
            # Set focus
            picam2.set_controls({"LensFocus": focus})
            time.sleep(0.5)  # Allow time for focus to adjust

            # Capture the image
            filename = f"focus_test/image_focus_{focus:.1f}.jpg"
            picam2.capture_file(filename)
            print(f"Captured image with focus value {focus:.1f}")

        print("Focus test complete. Images saved in 'focus_test' directory.")

    finally:
        # Stop the camera
        picam2.stop()

if __name__ == "__main__":
    auto_focus_and_capture()