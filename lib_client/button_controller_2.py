'''
File: button_controller.py
Created Date: Tuesday, September 3rd 2024, 1:25:42 pm
Author: alex-crouch

Project Ver 2024
'''

import gpiod
import time
import threading
import sounddevice as sd
import soundfile as sf
from audiostream_helper2 import AudioStreamer
from picamera2 import Picamera2
from libcamera import Transform, controls
import cv2
import numpy as np
from buffer_helper import *
from vosk import Model, KaldiRecognizer
import queue
from collections import deque
import json
import re

class CameraController:
    def __init__(self):
        self.picam2 = Picamera2()
        camera_config = self.picam2.create_video_configuration(
            transform=Transform(vflip=1, hflip=1),
            # main={"size": (1920, 1080)},  # 1080p resolution
            # main={"size": (2304, 1296)},
            main={"size": (4608, 2592)},
            # controls={"FrameRate": 30}    # Set frame rate to 30 fps
            controls={"FrameRate": 15}    # Set frame rate to 15 fps for 4K
        )
        self.picam2.configure(camera_config)
        self.picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
        self.picam2.start()
        time.sleep(2)  # Allow camera to initialize

        self.frame_buffer = [None] * 10
        self.frame_pointer = 0


    def capture_frame(self):
        frame = self.picam2.capture_array()
        if frame is not None:
            self.frame_buffer[self.frame_pointer] = frame
            self.frame_pointer = (self.frame_pointer + 1) % 10
        return frame is not None
    
    def focus_capture(self, focus_value):
        self.picam2.set_controls({"LensFocus": focus_value}) #Set focus value
        time.sleep(0.5) # Allow time for focus to adjust
        focus_values = [i/10 for i in range(11)] #0.0 to 1.0 in steps of 0.1
        for focus in focus_values:
            frame_array = capture_frame(focus)

        print("Focus test complete, picking best image now")

    def get_best_image(self):
        best_image_index = pick_best_image(self.frame_buffer)
        rgb = cv2.cvtColor(self.frame_buffer[best_image_index], cv2.COLOR_BGR2RGB)
        cv2.imwrite('best_image.png', rgb)
        print("Best image is:", best_image_index)
        return 'best_image.png'  # Return the encrypted image filename

class GPIOButtonControl:
    def __init__(self, case = 'caseA'):
        self.chip = gpiod.Chip('gpiochip4')
        self.button_desc = self.chip.get_line(2)
        self.button_read = self.chip.get_line(3)
        self.button_desc.request(consumer="Line", type=gpiod.LINE_REQ_EV_RISING_EDGE)
        self.button_read.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
        self.selected_case = case
        self.running = False
        self.current_function = None
        self.function_start_time = None
        self.last_cancel_time = None
        self.chat_start_time = None
        self.key_start_time = None
        self.chat_grace_period = 3  # 3 seconds grace period

        # Set the pre-configured prompts
        self.describe_prompt = 'Describe this image in 40 words. Use natural language suitable for conversion to speech.'
        self.read_prompt = 'Read all the text in this image. Include what you think the text represents as you respond. Use natural language and full stops only'

        # Load the cancel sound
        self.cancel_sound, self.file_samplerate = sf.read('/home/ver/cr2/lib_client/cancel.wav')
        self.desc_sound, self.file_samplerate = sf.read('/home/ver/cr2/lib_client/desc.wav')
        self.read_sound, self.file_samplerate = sf.read('/home/ver/cr2/lib_client/read.wav')
        self.chat_sound, self.file_samplerate = sf.read('/home/ver/cr2/lib_client/chat.wav')
        self.select_sound, self.file_samplerate = sf.read('/home/ver/cr2/lib_client/select.wav')
        self.help_sound, self.file_samplerate = sf.read('/home/ver/cr2/lib_client/help.wav')
        self.no_internet_sound, self.file_samplerate = sf.read('/home/ver/cr2/lib_client/internot.wav')

        # Initialize AudioStreamer and CameraController
        self.audio_streamer = AudioStreamer()
        self.camera_controller = CameraController()

        # Initialize Vosk model for speech recognition
        self.model = Model(lang="en-us")
        self.device_info = sd.query_devices(None, "input")
        self.samplerate = int(self.device_info["default_samplerate"])
        self.rec = KaldiRecognizer(self.model, self.samplerate)
        self.q = queue.Queue()

    def play_sound(self, sound):
        sd.play(sound, self.file_samplerate)
        sd.wait()  # Wait for the sound to finish playing

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        self.q.put(bytes(indata))

    def input_key(self):
        detection = None
        keyword = None
        with sd.RawInputStream(samplerate=self.samplerate, blocksize = 8000, device=None,
            dtype="int16", channels=1, callback=self.audio_callback): # begin recording
            rec = KaldiRecognizer(self.model, self.samplerate)  # get STT model ready
            while True:
                if self.current_function is not None:
                # if self.current_function is not None and self.button_desc.get_value() != 0:
                    data = self.q.get() # get audio data from the queue
                    if rec.AcceptWaveform(data):
                        detection = rec.PartialResult()
                        ting = json.loads(detection)
                        print(ting.get("text", ""))
                        if re.search("Describe", detection, re.IGNORECASE) is not None:
                            keyword = 'Describe'
                            print(f'{keyword} detected, quitting')
                            break
                        if re.search("Read", detection, re.IGNORECASE) is not None:
                            keyword = 'Read'
                            print(f'{keyword} detected, quitting')
                            break
                        if re.search("Chat", detection, re.IGNORECASE) is not None:
                            keyword = 'Chat'
                            print(f'{keyword} detected, quitting')
                            break
                        if re.search("Help", detection, re.IGNORECASE) is not None:
                            keyword = 'Help'
                            print(f'{keyword} detected, quitting')
                            break
                else:
                    break
        return keyword

    def input_speech(self):
        detection = None
        with sd.RawInputStream(samplerate=self.samplerate, blocksize = 8000, device=None,
            dtype="int16", channels=1, callback=self.audio_callback): # begin recording
            print("Start speaking...")
            rec = KaldiRecognizer(self.model, self.samplerate)
            while True:
                if self.current_function is not None:
                    data = self.q.get() # get audio data from the queue
                    if rec.AcceptWaveform(data):
                        detection = rec.Result()    # inference on model
                        ting = json.loads(detection)
                        print(ting.get("text", ""))
                else:
                    break
        return detection

    def run_function(self, function_name):
        print(f'Running {function_name}')
        self.running = True
        self.function_start_time = time.time()
        
        if function_name == 'Desc':
            threading.Thread(target=self.play_sound(self.desc_sound)).start()
            text = self.describe_prompt
        elif function_name == 'Read':
            threading.Thread(target=self.play_sound(self.read_sound)).start()
            text = self.read_prompt
        elif function_name == 'Chat':
            threading.Thread(target=self.play_sound(self.chat_sound)).start()
            self.chat_start_time = time.time()
            inputted_speech = self.input_speech()
            text = f"Based on the image, respond to this query: {inputted_speech}"
        elif function_name == 'Key':
            threading.Thread(target=self.play_sound(self.select_sound)).start()
            self.key_start_time = time.time()
            inputted_key = self.input_key()
            if inputted_key == 'Describe':
                threading.Thread(target=self.play_sound(self.desc_sound)).start()
                text = self.describe_prompt
            elif inputted_key == 'Read':
                threading.Thread(target=self.play_sound(self.read_sound)).start()
                text = self.read_prompt
            elif inputted_key == 'Chat':
                threading.Thread(target=self.play_sound(self.chat_sound)).start()
                self.current_function = 'Chat'
                self.chat_start_time = time.time()
                inputted_speech = self.input_speech()
                text = f"Based on the image, respond to this query: {inputted_speech}"
            else:
                threading.Thread(target=self.play_sound(self.help_sound)).start()
                self.running = False
                self.current_function = None
                self.function_start_time = None
                self.chat_start_time = None
                self.key_start_time = None
                return
        else:
            print(f"Unknown function: {function_name}")
            self.running = False
            self.current_function = None
            self.function_start_time = None
            self.chat_start_time = None
            self.key_start_time = None
            return
        if self.current_function is not None:
            try:
                image_path = self.camera_controller.get_best_image()
                self.audio_streamer.run_audio_stream(image_path, text, timer=True)
            except:
                threading.Thread(target=self.play_sound(self.no_internet_sound)).start()
        else:
            self.cancel_function()

        self.running = False
        self.current_function = None
        self.function_start_time = None
        self.chat_start_time = None
        self.key_start_time = None

    def cancel_function(self):
        if self.running and time.time() - self.function_start_time >= 1.5:
            self.running = False
            self.last_cancel_time = time.time()
            print("Function cancelled")
            self.audio_streamer.stop_audio_stream()
            threading.Thread(target=self.play_sound(self.cancel_sound)).start()

    def can_start_new_function(self):
        return (not self.running and 
                (self.last_cancel_time is None or 
                 time.time() - self.last_cancel_time > 1))

    def check_button_desc(self):
        if self.button_desc.get_value() == 0:
            if self.running:
                if self.current_function == 'Chat':
                    if self.chat_start_time and time.time() - self.chat_start_time > self.chat_grace_period:
                        print("Ending Chat function")
                        self.current_function = None  # Stop speech recognition
                    else:
                        print("Chat function is still in grace period")
                else:
                    return  # Don't cancel if it's not a Chat function
            time.sleep(0.4)
            if self.button_desc.get_value() == 0:
                if self.can_start_new_function():
                    self.current_function = 'Chat'
                    threading.Thread(target=self.run_function, args=(self.current_function,)).start()
            else:
                if self.can_start_new_function():
                    self.current_function = 'Desc'
                    threading.Thread(target=self.run_function, args=(self.current_function,)).start()

    def check_button_read(self):
        if self.button_read.get_value() == 0:
            if self.running:
                self.cancel_function()
            elif self.can_start_new_function():
                self.current_function = 'Read'
                threading.Thread(target=self.run_function, args=(self.current_function,)).start()

    def check_button_key(self):
        if self.button_desc.get_value() == 0:
            if self.running:
                # print(f'Button Press {self.current_function}')
                if self.current_function == 'Chat':
                    if self.chat_start_time and time.time() - self.chat_start_time > self.chat_grace_period:
                        print("Ending Chat function")
                        self.current_function = None  # Stop speech recognition
                    else:
                        print("Chat function is still in grace period")
                elif self.current_function == 'Key':
                    if self.key_start_time and time.time() - self.key_start_time > self.chat_grace_period:
                        print("Ending Key function")
                        self.current_function = None  # Stop speech recognition
                    else:
                        print("Key function is still in grace period")
                else:
                    return  # Don't cancel if it's not a Chat function
            elif self.can_start_new_function():
                self.current_function = 'Key'
                threading.Thread(target=self.run_function, args=(self.current_function,)).start()

    def run(self):
        while True:
            if self.selected_case == 'caseA':
                self.camera_controller.capture_frame()
                self.check_button_desc()
                self.check_button_read()
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
            elif self.selected_case == 'caseB':
                self.camera_controller.capture_frame()
                self.check_button_key()
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage

class CaseSelect:
    def __init__(self, case = None):
        self.chip = gpiod.Chip('gpiochip4')
        self.button_desc = self.chip.get_line(2)
        self.button_read = self.chip.get_line(3)
        self.button_desc.request(consumer="Line", type=gpiod.LINE_REQ_EV_RISING_EDGE)
        self.button_read.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
        self.input_case = case
        self.selected_case = None
        self.choose_sound, self.file_samplerate = sf.read('/home/ver/cr2/lib_client/choose.wav')
        self.caseA_sound, self.file_samplerate = sf.read('/home/ver/cr2/lib_client/caseA.wav')
        self.caseB_sound, self.file_samplerate = sf.read('/home/ver/cr2/lib_client/caseB.wav')

    def loop_choose(self):
        threading.Thread(target=self.play_sound(self.choose_sound)).start()

    def play_sound(self, sound):
        sd.play(sound, self.file_samplerate)
        sd.wait()  # Wait for the sound to finish playing

    def check_selection(self):
        if self.button_desc.get_value() == 0 or self.input_case == 'caseA':
            threading.Thread(target=self.play_sound(self.caseA_sound)).start()
            self.selected_case = 'caseA'
        elif self.button_read.get_value() == 0 or self.input_case == 'caseB':
            threading.Thread(target=self.play_sound(self.caseB_sound)).start()
            self.selected_case = 'caseB'

    def run(self):
        if self.input_case is None:
            threading.Thread(target=self.play_sound(self.choose_sound)).start()
        while self.selected_case is None:
            self.check_selection()
            time.sleep(0.01)  # Small delay to prevent excessive CPU usage
        self.chip.close()
        return self.selected_case
# Usage
if __name__ == "__main__":
    case_select = CaseSelect(case='caseA')
    case = case_select.run()
    control = GPIOButtonControl(case)
    control.run()