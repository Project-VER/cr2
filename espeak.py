#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 10:14:33 2024

@author: abigailhiggins
"""

#https://espeak.sourceforge.net/

import subprocess

def speak(text):
    subprocess.run(['espeak', text], check=True)

speak("Hello, this is eSpeak")


