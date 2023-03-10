import wave
import struct

import openai
import pvporcupine
import pyaudio
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

FORMAT = pyaudio.paInt16
CHANNELS = config.getint('AUDIO', 'channels')
RATE = config.getint('AUDIO', 'rate')
CHUNK = config.getint('AUDIO', 'chunk')
THRESHOLD = config.getint('AUDIO', 'threshold')
WAVE_OUTPUT_FILENAME = "output.wav"

# Initialize PyAudio
p = pyaudio.PyAudio()


def wave_recorder(frames: list[bytes]) -> None:
    """
    Saves audio frames to a WAV file.

    Args:
        frames: List of audio frames to save.

    Returns:
        None
    """

    # Create a new wave file with the given filename
    wf = wave.open("output.wav", "wb")

    # Set the audio parameters for the wave file
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(RATE)

    # Write the audio frames to the wave file
    wf.writeframes(b''.join(frames))

    # Close the wave file
    wf.close()


def record_question(p: pyaudio.PyAudio) -> list[bytes]:
    """
    Records an audio question and returns the recorded audio frames.

    Args:
        p: PyAudio instance.

    Returns:
        A list of recorded audio frames.
    """

    # Create an audio stream with the specified parameters
    question_stream = p.open(rate=RATE,
                             channels=CHANNELS,
                             format=pyaudio.paInt16,
                             input=True,
                             frames_per_buffer=CHUNK)

    print("* recording")

    # Create an empty list to store the audio frames
    frames = []

    # Record audio frames for 5 seconds
    for i in range(0, int(RATE / CHUNK * 5)):
        data = question_stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    # Return the recorded audio frames
    return frames
def wake_word(stream: pyaudio.Stream, porcupine: pvporcupine.Porcupine) -> int:
    """
    Processes a single audio frame and returns the keyword index if detected, otherwise -1.

    Args:
        stream: Audio stream.
        porcupine: Porcupine instance.

    Returns:
        Keyword index if detected, otherwise -1.
    """

    # Read a single audio frame from the stream
    pcm = stream.read(porcupine.frame_length)

    # Convert the PCM data to a list of samples
    pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

    # Process the audio frame and return the keyword index
    return porcupine.process(pcm)

def transcibe_voice(path):

    audio_file = open(path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    return transcript


messages = [
    {
        "role": "system",
        "content": "You are a helpful AI assistant.",
    }
]
def transcribe_to_gpt(transcript):
    global messages


    messages.append({"role": "user", "content": transcript["text"]})

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

    system_message = response["choices"][0]["message"]
    messages.append(system_message)

    # subprocess.call(["espeak", system_message["content"]])

    chat_transcript = ""
    for message in messages:
        if message["role"] != "system":
            chat_transcript += message["role"] + ": " + message["content"] + "\n\n"

    return chat_transcript
