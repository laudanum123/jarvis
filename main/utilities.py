import numpy as np
import wave
import struct
import openai
import pvporcupine
import pyaudio
import configparser
import os
import config as c

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "../config.ini"))

# Read available personas from the personas.ini file
personas_config = configparser.ConfigParser()
personas_config.read(os.path.join(os.path.dirname(__file__), "../personas.ini"))
personas = personas_config.sections()

# Prompt the user to select a persona
print("Available personas:")
for idx, persona in enumerate(personas):
    print(f"{idx + 1}. {persona}")

selected_persona = int(input("Select a persona (enter the number): ")) - 1
persona_name = personas[selected_persona]

# Retrieve messages for the selected persona
messages = eval(personas_config.get(persona_name, "messages"))


FORMAT = pyaudio.paInt16
CHANNELS = config.getint("AUDIO", "channels")
RATE = config.getint("AUDIO", "rate")
CHUNK = config.getint("AUDIO", "chunk")
THRESHOLD = config.getint("AUDIO", "threshold")
DEVICE_ID = config.getint("AUDIO", "device_id")
WAVE_OUTPUT_FILENAME = "../output.wav"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
RESET = "\033[0m"


# Set OpenAI API Key
openai.api_key = c.API_KEY

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
    wf = wave.open("../output.wav", "wb")

    # Set the audio parameters for the wave file
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(RATE)

    # Write the audio frames to the wave file
    wf.writeframes(b"".join(frames))

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
    question_stream = p.open(
        rate=RATE,
        channels=CHANNELS,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=DEVICE_ID,
    )

    print(RED + "Recording..." + RESET)

    # Create an empty list to store the audio frames
    frames = []

    # Initialize variables for silence detection
    silence_threshold = THRESHOLD  # Adjust this value to set the silence threshold
    silence_duration = 0
    is_recording = False

    # Record audio frames until there is no speech for 2 seconds
    while True:
        data = question_stream.read(CHUNK, exception_on_overflow=False)
        rms = np.sqrt(np.mean(np.abs(np.square(np.frombuffer(data, dtype=np.int16)))))
        # If the RMS value is above the silence threshold, start recording
        print(rms)
        if rms > silence_threshold:
            is_recording = True
            silence_duration = 0

        # If the RMS value is below the silence threshold, increment the silence duration
        else:
            silence_duration += 1

        # If we have been silent for 2 seconds, stop recording
        if is_recording and silence_duration > int(RATE / CHUNK * 2):
            break

        # Append the audio frame to the list of frames if we are recording
        if is_recording:
            frames.append(data)

    print(GREEN + "Recording Complete" + RESET)

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
    global messages

    audio_file = open(path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    return transcript


def transcribe_to_gpt(transcript):
    global messages

    messages.append({"role": "user", "content": transcript["text"]})

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

    system_message = response["choices"][0]["message"]
    messages.append(system_message)

    # subprocess.call(["espeak", system_message["content"]])

    chat_transcript = ""
    for message in messages:
        if message["role"] == "user":
            chat_transcript += (
                CYAN
                + message["role"].title()
                + ": "
                + message["content"]
                + RESET
                + "\n"
                + "-" * 50
                + "\n"
            )
        elif message["role"] == "assistant":
            chat_transcript += (
                YELLOW
                + message["role"].title()
                + ": "
                + message["content"]
                + RESET
                + "\n"
            )

    return chat_transcript, system_message["content"]
