import os

import gradio as gr
import openai, config, subprocess
from gtts import gTTS
import pygame

openai.api_key = config.OPENAI_API_KEY

messages = [
    {
        "role": "system",
        "content": "You are a helpful AI assistant. Always ask the user helpful follow up questions.",
    }
]

pygame.init()


def transcribe(audio):
    global messages

    audio_file = open(audio, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    messages.append({"role": "user", "content": transcript["text"]})

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

    system_message = response["choices"][0]["message"]
    messages.append(system_message)

    # Stop the music playback and unload the file from mixer if it is playing
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    pygame.mixer.music.unload()

    tts = gTTS(system_message["content"], lang="en", tld="us", slow=False)
    tts.save("response.mp3")

    pygame.mixer.music.load("response.mp3")
    pygame.mixer.music.play()

    # subprocess.call(["espeak", system_message["content"]])

    chat_transcript = ""
    for message in messages:
        if message["role"] != "system":
            chat_transcript += message["role"] + ": " + message["content"] + "\n\n"

    return chat_transcript


ui = gr.Interface(
    fn=transcribe, inputs=gr.Audio(source="microphone", type="filepath"), outputs="text"
).launch()
ui.launch()
