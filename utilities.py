import wave
import struct
import pvporcupine
import pyaudio
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

FORMAT = pyaudio.paInt16
CHANNELS = config.getint('DEFAULT', 'channels')
RATE = config.getint('DEFAULT', 'rate')
CHUNK = config.getint('DEFAULT', 'chunk')
THRESHOLD = config.getint('DEFAULT', 'threshold')

# Initialize PyAudio
p = pyaudio.PyAudio()

def wave_recorder():

    wf = wave.open("output.wav", "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(RATE)

    return wf

print("JARVIS is now listening...")
print("*" * 50)

def wake_word():

    try:
        porcupine = pvporcupine.create(keywords=['jarvis'])

        p = pyaudio.PyAudio()
        audio_stream = p.open(rate = porcupine.sample_rate,
                                channels = 1,
                                format = pyaudio.paInt16,
                                input = True,
                                frames_per_buffer = porcupine.frame_length)
        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("JARVIS is awake!")
    finally:
        if porcupine is not None:
            porcupine.delete()