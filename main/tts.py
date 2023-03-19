import os
import configparser
import platform
import subprocess

# Read configuration file
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "../config.ini"))

# Get TTS speed from configuration file
tts_speed = config.getint("TTS", "tts_speed")

# Determine the operating system
operating_system = platform.system()

if operating_system == "Windows":
    import pyttsx3
    import msvcrt

    # Initialize pyttsx3 engine
    engine = pyttsx3.init(driverName="sapi5")

    # Get all available voices and set TTS speed
    voices = engine.getProperty("voices")
    engine.setProperty("rate", tts_speed)


def speak(text: str, speak_condition: bool = True) -> None:
    """
    Converts the input text to speech using the appropriate TTS engine and speaks it.

    Args:
    text (str): The input text that needs to be spoken.
    speak_condition (bool, optional): Whether or not to continue speaking. Defaults to True.

    Returns:
    None
    """
    if operating_system == "Windows":
        # Split text into sentences
        text = text.split(".")

        # Speak each sentence until speak_condition is False
        while speak_condition:
            for sentence in text:
                # Check for key press to stop speaking
                if msvcrt.kbhit():
                    if ord(msvcrt.getch()) == 32:  # 32 is the ASCII code for space
                        speak_condition = False
                        break
                else:
                    engine.say(sentence)
                    engine.runAndWait()
    elif operating_system == "Linux":
        # Split text into sentences
        text = text.split(".")

        # Speak each sentence until speak_condition is False
        for sentence in text:
            if speak_condition:
                subprocess.run(
                    ["espeak", f"-s {tts_speed}", "-w", "/tmp/tts_output.wav", sentence]
                )
                subprocess.run(
                    ["paplay", "/tmp/tts_output.wav"], stderr=subprocess.DEVNULL
                )
            else:
                break
    else:
        print("Unsupported operating system")
