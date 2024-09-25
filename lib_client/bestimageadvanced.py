'''
Takes 10 images at 10 different focus values 
Calculates average brightness and composition using rule of thirds 
Gets normalised values for FOM, brightness and composition and calculated overall score 
Picks best image
'''

from picamera2 import Picamera2
from libcamera import controls
import time
import numpy as np
import cv2

def analyze_image(image):
    # Convert to grayscale for brightness analysis
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray_image)
    
   # Simple composition analysis (rule of thirds)
    height, width = image.shape[:2]
    thirds_x, thirds_y = width // 3, height // 3
    
    # Check if any edges are close to the thirds lines
    edges = cv2.Canny(gray_image, 100, 200)
    thirds_score = np.sum(edges[thirds_y-5:thirds_y+5, :]) + \
                   np.sum(edges[2*thirds_y-5:2*thirds_y+5, :]) + \
                   np.sum(edges[:, thirds_x-5:thirds_x+5]) + \
                   np.sum(edges[:, 2*thirds_x-5:2*thirds_x+5])
    
    return brightness, thirds_score


def capture_image_with_analysis(picam):
    metadata = picam.capture_metadata()
    fom = metadata['AfState'].FocusFoM
    
    # Capture image directly as a numpy array
    image = picam.capture_array()
    
    # Convert from BGR to RGB color space
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    brightness, composition_score = analyze_image(image_rgb)
    
    return image_rgb, fom, brightness, composition_score

def main():
    picam2 = Picamera2()
    config = picam2.create_still_configuration()
    picam2.configure(config)
    picam2.start()

    time.sleep(2)  # Allow time for auto exposure to settle

    images_with_data = []
    focus_positions = range(0, 11) # Integer values from 0 to 10
    
    print("Capturing images with focus bracketing...")
    for pos in focus_positions:
        picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": float(pos)})
        time.sleep(0.5)  # Allow time for focus to adjust
        
        image, fom, brightness, composition = capture_image_with_analysis(picam2)
        images_with_data.append((image, fom, brightness, composition, pos))
        print(f"Image captured. FoM: {fom:.2f}, Brightness: {brightness:.2f}, Composition: {composition:.2f}")

    # Normalize scores
    foms = [f for _, f, _, _, _ in images_with_data]
    brightnesses = [b for _, _, b, _, _ in images_with_data]
    compositions = [c for _, _, _, c, _ in images_with_data]
    
    norm_foms = (foms - np.min(foms)) / (np.max(foms) - np.min(foms))
    norm_bright = 1 - np.abs(np.array(brightnesses) - 128) / 128  # 128 is middle gray
    norm_comp = (compositions - np.min(compositions)) / (np.max(compositions) - np.min(compositions))
    
    # Calculate overall scores (you can adjust weights here)
    overall_scores = 0.5 * norm_foms + 0.25 * norm_bright + 0.25 * norm_comp
    
    best_index = np.argmax(overall_scores)
    best_image, best_fom, best_brightness, best_composition, best_focus = images_with_data[best_index]
    
    print(f"\nBest image - FoM: {best_fom:.2f}, Brightness: {best_brightness:.2f}, "
          f"Composition: {best_composition:.2f}, Focus Position: {best_focus:.2f}")
    
    best_image.save("best_overall_image.jpg")
    print("Best image saved as 'best_overall_image.jpg'")

    picam2.stop()

if __name__ == "__main__":
    main()