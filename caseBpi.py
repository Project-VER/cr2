'''
File: caseBpi.py
Created Date: Monday, September 2nd 2024, 5:06:26 pm
Author: alex-crouch

Project Ver 2024
'''
#!/home/ver/env2/bin/python
#script for one button to listen for keyword allowing the user choose a request.

import sys
sys.path.append('/home/ver/cr2/lib_client')
from picamera2 import Picamera2
from libcamera import Transform, controls
import cv2
import numpy as np
import gpiod
import time
from buffer_helper import *
from audiostream_helper import *
from vosk_helper import *

import sounddevice as sd
#import soundfile as sf

# Initialise buttons
chip = gpiod.Chip('gpiochip4')
button_key = chip.get_line(2)

button_key.request(consumer="Line", type=gpiod.LINE_REQ_EV_RISING_EDGE)

# Initialise STT
STT = STT_Model()

# Initialise Camera
picam2 = Picamera2()
camera_config = picam2.create_video_configuration(
    transform=Transform(vflip=1,hflip=1),
    main={"size": (1920, 1080)},  # 1080p resolution
    controls={
        "FrameRate": 30,           # Set frame rate to 30 fps
	#"HorizontalFlip": True,    # Apply horizontal flip
        #"VerticalFlip": True       # Apply vertical flip
    }
)
picam2.configure(camera_config)

picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
picam2.start()
time.sleep(2)

# Initialize frame buffer
frame_buffer = [None] * 10
frame_pointer = 0

audio_streamer = AudioStreamer()
timer = True
desc_prompt = 'Describe this image in 40 words. Use natural language suitable for conversion to speech.'
read_prompt = 'Read all the text in this image. Include what you think the text represents as you respond. Use natural language and full stops only'

t = np.linspace(0,3,int(16000*5), False)
sine_wave = 0.3* np.sin(2*np.pi*440*t)

# Main loop
try:
	# Press to describe, hold to chat
#	while True:
#		if button_key.get_value() == 0:
#			print('Key')
#			requested_function = STT.key()
#			print(requested_function)
#			if requested_function == 'Read':
#				
#			if requested_function == 'Talk':
    while True:
        # Capture frame
        frame = picam2.capture_array()
        
        if frame is None:
            print("Can't receive frame. Exiting ...")
            break

        # Store frame in buffer
        frame_buffer[frame_pointer] = frame
        frame_pointer = (frame_pointer + 1) % 10
#!!!add try incase server is off        
        if button_key.get_value() != 1:
            requested_function = STT.key()
            best_image_index = pick_best_image(frame_buffer)
            rgb = cv2.cvtColor(frame_buffer[best_image_index], cv2.COLOR_BGR2RGB)
            cv2.imwrite('best_image.png', rgb)
            #encrypt(key, 'best_image.png', 'encd')
            print("Best image is:", best_image_index)
            print(requested_function)
            if requested_function == 'Describe':
               audio_streamer.run_audio_stream('best_image.png', desc_prompt, timer)
            if requested_function == 'Read':
               audio_streamer.run_audio_stream('best_image.png', read_prompt, timer)
            if requested_function == 'Talk':
                sd.play(sine_wave*.5, 16000)
                time.sleep(0.5)
                sd.stop()
                prompt = STT.run()
                print('not blocking')
                if button_key.get_value() != 1:
                    STT.stop()
                audio_streamer.run_audio_stream('best_image.png', prompt, timer)

        # Short delay to prevent CPU overuse
        time.sleep(0.01)
        
        if cv2.waitKey(1) == ord('q'):  # Keep 'q' key as backup exit
            break

finally:
    picam2.stop()
    #cv2.destroyAllWindows()
