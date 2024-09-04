'''
File: audiostream_helper.py
Created Date: Monday, September 2nd 2024, 3:46:57 pm
Author: alex-crouch

Project Ver 2024
'''
import numpy as np
import sounddevice as sd
import requests
import time

class AudioStreamer:
    def __init__(self, base_address = '192.168.193.33', port = 8000, samplerate = 24000, channels = 1):
        self.base_address = base_address
        self.port = port
        self.url = f'http://{base_address}:{port}'
        self.samplerate = samplerate
        self.channels = channels
        self.running = False
        self.stream = None
        self.response = None
        self.starttime = None
        self.call = False
                
    def run_audio_stream(self, image_path, text, timer=False):
        # option to print request to stream time handling
        if timer is True:
            self.starttime = time.time()
            self.call = True
        self.running = True
        
        # initialise sounddevice stream
        self.stream = sd.OutputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            dtype='float32',
        )
        
        files = {'file': open(image_path, 'rb')}
        data = {'text': text}
        
        self.response = requests.get(self.url, files=files, data=data, stream=True)
        
        with self.stream:
            print("Audio Stream Commenced")
            try:
                for chunk in self.response.iter_content(chunk_size=56):
                    if self.call is True:   # print time on first chunk if enabled
                        elapsed_time = time.time() - self.starttime
                        print('[{}] finished in {} ms'.format('Request to Stream', int(elapsed_time * 1_000)))
                        self.call = False
                    if chunk and self.running:  # continuously write to output device
                        audio_data = np.frombuffer(chunk, dtype=np.int16)
                        audio_float = audio_data.astype(np.float32) / 32768.0
                        self.stream.write(audio_float)
                    else:
                        break
            except Exception as e:
                print(f"Error: {e}")
            finally:    # tidy up stream and connection
                print("Finished Audio Stream")
                self.stream.close()
                self.response.close()
                self.running = False

    def stop_audio_stream(self):
        self.running = False
        print("Stopping the audio stream...")
