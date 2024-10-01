'''
Takes 10 images and records FOM (Figure of Merit) value and 
picks image with best FOM value '''

from picamera2 import Picamera2
import time
from PIL import Image
import io
import cv2

def capture_image_with_fom(picam):
    metadata = picam.capture_metadata()
    fom = metadata['AfState'].FocusFoM
    
    # Capture image directly as a numpy array
    image = picam.capture_array()
    
    # Convert from BGR to RGB color space
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    return image_rgb, fom

def main():
    picam2 = Picamera2()
    config = picam2.create_still_configuration()
    picam2.configure(config)
    picam2.start()

    # Allow time for auto exposure to settle
    time.sleep(2)

    images_with_fom = []
    
    print("Capturing 10 images...")
    for i in range(10):
        image, fom = capture_image_with_fom(picam2)
        images_with_fom.append((image, fom))
        print(f"Image {i+1} captured. FoM: {fom}")
        time.sleep(0.5)  # Short delay between captures

    # Find the image with the highest FoM
    best_image, best_fom = max(images_with_fom, key=lambda x: x[1])
    
    print(f"\nBest image FoM: {best_fom}")
    
    # Save the best image
    cv2.imwrite("best_fom_image.jpg", cv2.cvtColor(best_image, cv2.COLOR_RGB2BGR))
    print("Best image saved as 'best_fom_image.jpg'")

    picam2.stop()


if __name__ == "__main__":
    main()
