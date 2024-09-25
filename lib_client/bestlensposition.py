'''
Takes 10 images at different lens positions on the Pi Camera and
returns the best one based on blurriness (laplacian variance)
Made to test what the output is and if its actually the best image '''

import time
from picamera2 import Picamera2
from libcamera import controls
import os
import cv2 
import numpy as np 
from PIL import Image


class AutoFocusCamera:
    def __init__(self):
        self.picam2 = Picamera2()
        config = self.picam2.create_still_configuration()
        self.picam2.configure(config)
        self.picam2.start()
        time.sleep(2)  # Allow time for the camera to initialize

    def capture_and_save(self, lens_position):
        # Set the lens position
        self.picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": lens_position})
        time.sleep(0.5)  # Allow time for focus to adjust

        # Capture the image as a numpy array
        image_array = self.picam2.capture_array()

        # Convert the numpy array to a PIL Image
        image = Image.fromarray(image_array)

        # Save the image
        filename = f"focus_test/image_position_{lens_position:.0f}.jpg"
        image.save(filename)
        print(f"Captured image with lens position {lens_position:.0f}")

        return image_array

    def auto_focus_and_capture(self):
        # Create a directory to store the images
        os.makedirs("focus_test", exist_ok=True)

        # Define the range of lens positions to try
        # For Raspberry Pi Camera Module 3
        lens_positions = range(0, 11)  # Integer values from 0 to 10

        captured_images = []

        for position in lens_positions:
            image_array = self.capture_and_save(position)
            captured_images.append(image_array)

        print("Focus test complete. Images saved in 'focus_test' directory.")
        return captured_images

    def __del__(self):
        self.picam2.stop()

def variance_of_laplacian(image):
    # Convert image to grayscale if it's not already
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    return cv2.Laplacian(gray, cv2.CV_64F).var()

def find_best_focused_image(images, filenames):
    focus_measures = []

    for i, image in enumerate(images):
        fm = variance_of_laplacian(image)
        focus_measures.append((filenames[i], fm))

    focus_measures.sort(key=lambda x: x[1], reverse=True)
    return focus_measures[0][0]

def main():
    camera = AutoFocusCamera()
    images, filenames = camera.auto_focus_and_capture()
    print(f"Captured {len(images)} images at different lens positions.")

    best_image = find_best_focused_image(images, filenames)
    print(f"The best focused image is: {best_image}")

if __name__ == "__main__":
    main()

def main():
    camera = AutoFocusCamera()
    images = camera.auto_focus_and_capture()
    print(f"Captured {len(images)} images at different lens positions.")

if __name__ == "__main__":
    main()