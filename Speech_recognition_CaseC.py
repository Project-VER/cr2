# import packages
import vosk
from vosk import Model, KaldiRecognizer
import pyaudio
import json 
import re

# retrieve model and create model object
model = Model(r"C:\Users\User\Downloads\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15")

# create recognizer object
recognizer = KaldiRecognizer(model, 16000)

# pyaudio object
mic = pyaudio.PyAudio()

# frames per buffer
fpb = 32000

# configure microphone bitrate and buffer duration
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=fpb)
stream.start_stream()

"""
Function definitions
"""
# searches text for keywords in a list, returns keyword if found otherwise returns None
def find_keyword(keyword_list, text):
    for keyword in keyword_list:
        match = re.search(keyword, text)
        found_keyword = None

        if match != None:   #keyword detected
            found_keyword = match.group(0)
            return found_keyword
        else:
            continue

    return None     #return None if no keyword is found



""" 
Main code
"""
# loop to listen to audio and print output text
try:
    while True:
        data = stream.read(fpb)

        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            text = json.loads(result)["text"]  # Parse JSON and extract "text"
            print(text)

            #list of accepted keywords
            keyword_list = ["read", "describe", "chat"] 

            # search text for keywords
            found_keyword = find_keyword(keyword_list, text)

            # Direct to appropriate function according to detected keyword
            if found_keyword != None:   # keyword found
                match found_keyword:
                    case "read":
                        print("Read function reached :)")
                    case "describe":
                        print("Describe function reached :)")
                    case "chat":
                        print("Chat function reached :)")
                break


                        


except KeyboardInterrupt:
    print("\nStopping...")
finally:
    stream.stop_stream()
    stream.close()
    mic.terminate()


