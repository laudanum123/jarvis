import tts
import pvporcupine
import pyaudio
import threading
import os
import select


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


def listen_for_keypress(stop_event):
    if os.name == "nt":
        while not stop_event.is_set():
            if msvcrt.kbhit():
                key = msvcrt.getch().decode("utf-8")
                if key.lower() == "r":
                    return
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(sys.stdin.fileno())
            while not stop_event.is_set():
                if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                    key = sys.stdin.read(1)
                    if key.lower() == "r":
                        return
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


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
            # stop_event = threading.Event()
            # key_listener = threading.Thread(
            #     target=listen_for_keypress, args=(stop_event,)
            # )
            # key_listener.start()

            # Listen for the wake word
            keyword_index = wake_word(wake_word_stream, porcupine)

            # stop_event.set()
            # key_listener.join()
            keyword_detect = [msvcrt.kbhit() and chr(ord(msvcrt.getch())) if os.name == "nt" else sys.stdin.read(1)]

            if keyword_index >= 0 or "r" in keyword_detect:
                # Record the user's question
                frames = record_question(p)

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
