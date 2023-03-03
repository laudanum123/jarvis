import json
import pyaudio
import numpy as np
import logging
import warnings
import vosk

# Define parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
THRESHOLD = 50

# Initialize Vosk model
model = vosk.Model(model_name = "vosk-model-small-en-us-0.15")
recognizer = vosk.KaldiRecognizer(model, RATE)

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open audio stream
stream = p.open(format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

while True:
    # Read audio data
    data = stream.read(CHUNK)

    recognizer.AcceptWaveform(data)
    result = recognizer.Result()
    text = json.loads(result)['text']
    # Convert audio data to numpy array
    data_thresh = np.frombuffer(data, dtype=np.int16)

    # Capture and log warnings

    square = np.square(data_thresh)
    mean = np.mean(square)
    sqrt = np.sqrt(mean)

    rms = sqrt

    # Check if the root mean square is above the threshold
    if rms > THRESHOLD and 'hello' in text:
    # If sound is detected, use Vosk to transcribe speech
        # If "Hello" is recognized, do something
        print("Hello detected!")
