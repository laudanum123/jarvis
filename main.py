import pyaudio
import numpy as np
import logging
import warnings

# Define parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
THRESHOLD = 50

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open audio stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

while True:
    # Read audio data
    data = stream.read(CHUNK)
    # Convert audio data to numpy array
    data = np.frombuffer(data, dtype=np.int16)

    # Capture and log warnings

    square = np.square(data)
    mean = np.mean(square)
    sqrt = np.sqrt(mean)

    rms = sqrt

    # Check if the root mean square is above the threshold
    if rms > THRESHOLD:
        # If sound is detected, do something
        print("Sound detected!")
