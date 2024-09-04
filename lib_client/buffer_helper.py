#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 20:34:19 2024

@author: abigailhiggins
"""

import cv2
import numpy as np

def calculate_blurriness(frame_buffer):
    """ Calculate the Laplacian variance of an image """
    gray = cv2.cvtColor(frame_buffer, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance

def calculate_glare(frame_buffer, threshold=230):
    """ Calculate glare areas by thresholding bright regions """
    gray = cv2.cvtColor(frame_buffer, cv2.COLOR_BGR2GRAY)
    _, thresholded = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    glare_area = np.sum(thresholded > 0) / np.size(gray)
    return glare_area

def pick_best_image(frame_buffer):
    best_image_idx = -1
    best_score = -1

    for idx, buf_frame in enumerate(frame_buffer):
        blurriness = calculate_blurriness(buf_frame)
        glare = calculate_glare(buf_frame)
        score = blurriness - 10 * glare  # Adjust weights as necessary

        # window_name = f'Buffered Frame {idx + 1} (Blurriness: {blurriness:.2f}, Glare: {glare:.4f}, Score: {score:.2f})'
        # cv2.imshow(window_name, buf_frame)
        # cv2.waitKey(0)
        # cv2.destroyWindow(window_name)

        if best_score == -1 or score > best_score:
            best_score = score
            best_image_idx = idx 

    if best_image_idx != -1:
        print(f'The best image is at index {best_image_idx + 1} with a score of {best_score}')
        return best_image_idx
    else:
        print("No valid images in buffer.")