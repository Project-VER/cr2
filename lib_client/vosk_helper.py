import queue
import sys
import sounddevice as sd
import re
import json
from vosk import Model, KaldiRecognizer
from collections import deque

class RollingBuffer:
    def __init__(self, max_size):
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)
    
    def add(self, item):
        self.buffer.append(item)
    
    def get_all(self):
        return list(self.buffer)

class STT_Model:
    def __init__(self, **kwargs):
        self.model = Model(lang="en-us")    # set to default model
        self.samplerate = None  # initialise samplerate
        self.q = queue.Queue()  # initialise queue
        self.load()

    def load(self):
        device_info = sd.query_devices(None, "input")
        self.samplerate = int(device_info["default_samplerate"])    # soundfile expects an int

    def callback(self, indata, frames, time, status):   # called from a separate thread for each audio block
        if status:
            print(status, file=sys.stderr)
        self.q.put(bytes(indata))
    
    def key(self):
        rolling_buffer = RollingBuffer(max_size=5)
        with sd.RawInputStream(samplerate=self.samplerate, blocksize = 8000, device=None,
            dtype="int16", channels=1, callback=self.callback): # begin recording
            print("#" * 80)
            print("Ctrl+C or say good to stop the recording")
            print("#" * 80)
            rec = KaldiRecognizer(self.model, self.samplerate)  # get STT model ready
            while True:
                data = self.q.get() # get audio data from the queue
                if rec.AcceptWaveform(data):
                    detection = rec.PartialResult()
                    #detection = rec.Result()    # inference on model\
                    ting = json.loads(detection)
                    print(ting.get("text", ""))
                    rolling_buffer.add(ting.get("text", ""))
                    #print(detection)
                    if re.search(r"\bDescribe\b|\bRead\b|\bTalk\b", detection, re.IGNORECASE) is not None: # quit when keyword is detected
                        #key = re.search(r"\bDescribe\b|\bRead\b|\bTalk\b", detection, re.IGNORECASE)
                        if re.search("Describe", detection, re.IGNORECASE) is not None:
                            keyword = 'Describe'
                            print(f'{keyword} detected, quitting')
                            break
                        if re.search("Read", detection, re.IGNORECASE) is not None:
                            keyword = 'Read'
                            print(f'{keyword} detected, quitting')
                            break
                        if re.search("Talk", detection, re.IGNORECASE) is not None:
                            keyword = 'Talk'
                            print(f'{keyword} detected, quitting')
                            break
        return keyword
    
    def run(self):
        self.stop = 0
        rolling_buffer = RollingBuffer(max_size=5)
        with sd.RawInputStream(samplerate=self.samplerate, blocksize = 8000, device=None,
            dtype="int16", channels=1, callback=self.callback): # begin recording
            print("#" * 80)
            print("Ctrl+C or say good to stop the recording")
            print("#" * 80)
            rec = KaldiRecognizer(self.model, self.samplerate)  # get STT model ready
            while True:
                data = self.q.get() # get audio data from the queue
                if rec.AcceptWaveform(data):
                    # detection = rec.PartialResult()
                    detection = rec.Result()    # inference on model\
                    ting = json.loads(detection)
                    print(ting.get("text", ""))
                    rolling_buffer.add(ting.get("text", ""))
                    #print(detection)
                    if self.stop == 1:
                        print('stopped')
                        break
        return rolling_buffer.get_all()
    
    def stop(self):
        self.stop = 1
