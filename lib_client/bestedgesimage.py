from picamera2 import Picamera2
import cv2
import numpy as np
import time

def edge_detection_autofocus(picam, num_steps=10, roi=None):
    max_sharpness = 0
    best_position = 0
    
    # Get the current focus range
    focus_range = picam.camera_controls['LensPosition']
    min_focus, max_focus = focus_range['min'], focus_range['max']
    step_size = (max_focus - min_focus) / num_steps
    
    for i in range(num_steps):
        focus_value = min_focus + i * step_size
        picam.set_controls({"AfMode": 2, "LensPosition": focus_value})
        time.sleep(0.1)  # Allow time for focus to adjust
        
        # Capture frame
        frame = picam.capture_array()
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply ROI if specified
        # if roi:
        #     gray = gray[roi[1]:roi[3], roi[0]:roi[2]]
        
        # Calculate edge sharpness
        edges = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = np.var(edges)
        
        print(f"Focus position: {focus_value:.2f}, Sharpness: {sharpness:.2f}")
        
        if sharpness > max_sharpness:
            max_sharpness = sharpness
            best_position = focus_value
    
    return best_position

def main():
    picam = Picamera2()
    config = picam.create_preview_configuration()
    picam.configure(config)
    picam.start()
    
    try:
        while True:
            input("Press Enter to perform edge detection autofocus (or Ctrl+C to quit)...")
            
            # Perform edge detection autofocus
            best_focus = edge_detection_autofocus(picam)
            
            print(f"Best focus position: {best_focus:.2f}")
            picam.set_controls({"AfMode": 2, "LensPosition": best_focus})
            
            # Capture and save the focused image
            focused_image = picam.capture_array()
            cv2.imwrite("edge_focused_image.jpg", focused_image)
            print("Focused image saved as 'edge_focused_image.jpg'")
    
    except KeyboardInterrupt:
        print("Exiting...")
    
    finally:
        picam.stop()

if __name__ == "__main__":
    main()