import pyttsx3
import os
import configparser
import msvcrt

# Read configuration file
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '../config.ini'))

# Initialize pyttsx3 engine
engine = pyttsx3.init(driverName='sapi5')

# Get TTS speed from configuration file
tts_speed = config.getint('TTS', 'tts_speed')

# Get all available voices and set TTS speed
voices = engine.getProperty('voices')
engine.setProperty('rate', tts_speed)


def speak(text: str, speak_condition: bool = True) -> None:
    """
    Converts the input text to speech using pyttsx3 engine and speaks it.

    Args:
    text (str): The input text that needs to be spoken.
    speak_condition (bool, optional): Whether or not to continue speaking. Defaults to True.

    Returns:
    None
    """
    # Split text into sentences
    text = text.split('.')

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
