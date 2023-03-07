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



def init_jarvis() -> None:
    """
    Initializes the Jarvis voice assistant and runs the main loop.

    Returns:
        None.
    """

    try:
        # Create a Porcupine instance with the Jarvis keyword
        porcupine = pvporcupine.create(keywords=['jarvis'])

        # Open an audio stream for the wake word detector
        wake_word_stream = p.open(rate=porcupine.sample_rate,
                                  channels=1,
                                  format=pyaudio.paInt16,
                                  input=True,
                                  frames_per_buffer=porcupine.frame_length)

        # Main loop
        while True:
            # Listen for the wake word
            keyword_index = wake_word(wake_word_stream, porcupine)

            if keyword_index >= 0:
                print("Listening...")
                # Record the user's question
                frames = record_question(p)

                # Save the recorded audio to a WAV file
                wave_recorder(frames)
                audio_file = open("output.wav", "rb")
                transcript = openai.Audio.transcribe("whisper-1", audio_file)
                print(transcript)

    finally:
        # Clean up resources
        if porcupine is not None:
            porcupine.delete()
