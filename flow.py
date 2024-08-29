#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 14:13:08 2024

@author: abigailhiggins
"""

import cv2
import numpy as np
import subprocess
from detectron2.utils.logger import setup_logger
from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog

setup_logger()

# Setup configuration for the predictor
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_1x.yaml"))
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_1x.yaml")
cfg.INPUT.MAX_SIZE_TEST = 320
cfg.MODEL.RPN.POST_NMS_TOPK_TEST = 100
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7
cfg.MODEL.DEVICE = "cpu"

predictor = DefaultPredictor(cfg)

# Initialize the webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Webcam could not be opened.")
    exit()

ret, old_frame = cap.read()
old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Can't receive frame. Exiting...")
            break

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate optical flow
        flow = cv2.calcOpticalFlowFarneback(old_gray, frame_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])

        # Detect objects
        outputs = predictor(frame)
        instances = outputs["instances"].to("cpu")
        classes = instances.pred_classes if instances.has("pred_classes") else None
        boxes = instances.pred_boxes.tensor.numpy() if instances.has("pred_boxes") else None

        for i, box in enumerate(boxes):
            cls = classes[i]
            if cls == 67:  # Class index for cell phone
                x, y, x2, y2 = map(int, box)
                phone_flow = magnitude[y:y2, x:x2]
                flow_mean = np.mean(phone_flow)

                # Check if the flow in the region is significant and toward the camera
                if flow_mean > 2:  # Threshold for significant motion towards the camera
                    print("Phone moving towards camera. Interrupting...")
                    subprocess.run(['espeak', 'Phone moving towards camera'])
                    break

        old_gray = frame_gray.copy()

        # Visualization
        v = Visualizer(frame[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)
        out = v.draw_instance_predictions(instances)
        cv2.imshow('Detectron2 Webcam', out.get_image()[:, :, ::-1])

        if cv2.waitKey(1) == ord('q'):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
