#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 18:42:56 2024

@author: abigailhiggins
"""
import cv2
from detectron2.utils.logger import setup_logger
setup_logger()

from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog

import time

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

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Can't receive frame. Exiting...")
            break
        start_time = time.time()
        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        outputs = predictor(frame)
        instances = outputs["instances"].to("cpu")
        classes = instances.pred_classes if instances.has("pred_classes") else None
        scores = instances.scores if instances.has("scores") else None

        for i, cls in enumerate(classes):
            confidence = scores[i] * 100
            if cls == 77:
                print(f"Phone detected with {confidence:.2f}% confidence")

        # Visualization
        v = Visualizer(frame[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)
        out = v.draw_instance_predictions(instances)
        cv2.imshow('Detectron2 Webcam', out.get_image()[:, :, ::-1])
        
        

        
        outputs = predictor(frame)
        print("Inference time: {:.2f} seconds".format(time.time() - start_time))


        if cv2.waitKey(1) == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()





