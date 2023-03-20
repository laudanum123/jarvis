import tts
import pvporcupine
import pyaudio
import os
import simpleaudio as sa


from utilities import (
    p,
    wake_word,
    record_question,
    wave_recorder,
    transcibe_voice,
    transcribe_to_gpt,
)

if os.name == "nt":
    import msvcrt
else:
    import sys
    import termios
    import tty


def play_sound(file_path: str) -> None:
    """
    Play a sound file.

    Args:
        file_path (str): The path to the sound file.

    Returns:
        None.
    """
    wave_obj = sa.WaveObject.from_wave_file(file_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()


def init_jarvis() -> None:
    """
    Initializes the Jarvis voice assistant and runs the main loop.

    Returns:
        None.
    """
    porcupine = None

    try:
        # Create a Porcupine instance with the Jarvis keyword
        porcupine = pvporcupine.create(keywords=["jarvis"])

        # Open an audio stream for the wake word detector
        wake_word_stream = p.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
        )

        # Main loop
        while True:

            # Listen for the wake word
            keyword_index = wake_word(wake_word_stream, porcupine)

            if keyword_index >= 0:

                # Play the start recording sound
                play_sound("../static/button.wav")

                # Record the user's question
                frames = record_question(p)

                # Play the end recording sound
                play_sound("../static/button.wav")

                # Save the recorded audio to a WAV file
                wave_recorder(frames)
                transcript = transcibe_voice("../output.wav")
                response = transcribe_to_gpt(transcript)
                print(response[0])
                tts.speak(response[1])

    except Exception as e:
        print(e)

    finally:
        # Clean up resources
        if porcupine is not None:
            porcupine.delete()
