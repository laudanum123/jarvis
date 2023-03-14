import pyttsx3
import os
import configparser

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '../config.ini'))
engine = pyttsx3.init(driverName='sapi5')

tts_speed = config.getint('TTS', 'tts_speed')

# Get all the available voices
voices = engine.getProperty('voices')
engine.setProperty('rate', tts_speed)

def speak(text: str) -> None:
    """
    Converts the input text to speech using pyttsx3 engine and speaks it.

    Args:
    text (str): The input text that needs to be spoken.

    Returns:
    None
    """
    engine.say(text)
    engine.runAndWait()