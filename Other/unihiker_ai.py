# -*- coding: UTF-8 -*-
# unihikerAI V1.2

import wave
import time
import openai
import pyaudio
import textwrap
from pinpong.board import Board, Pin
from pinpong.extension.unihiker import *
from unihiker import GUI, Audio

# Iniitialize Board
gui = GUI()
audio = Audio()
Board().begin()
openai.api_key = ""

# Global Variables
prompt = "You are a helpful assistant. You must answer with no more than two sentences"
previous_messages = [{"role": "system", "content": prompt}]
whisper_response = ""
output_filename = 'audio-recording.wav'

# GUI
green_bar = (122, 222, 44)
yellow_bar = (222, 222, 44)
red_bar = (222, 88, 44)
blue_bar = (44, 44, 222)
info_title2 = gui.draw_text(x=120, y=10, text='User (A)', font_size=12, origin='top')
info_text2 = gui.draw_text(x=120, y=30, text='', font_size=10, origin='top')
time_bar_bg = gui.draw_line(x0=20, y0=5, x1=220, y1=5, width=5, color=(222,222,222))
time_bar = gui.draw_line(x0=20, y0=5, x1=220, y1=5, width=5, color=red_bar)
info_title1 = gui.draw_text(x=120, y=140, text='ChatGPT (B)', font_size=12, origin='top')
info_text1 = gui.draw_text(x=120, y=160, text='', font_size=10, origin='top')

def btn_a_rising_handler(pin):
    global whisper_response
    print("Pressed button A (record 5s audio clip)")
    info_text2.config(text='Recording...')
    timed_audio_record(5)
    info_text2.config(text='Digesting Audio...')
    time_bar.config(color=yellow_bar)
    whisper_response = whisper_digest(output_filename)
    wrapped_text = textwrap.fill(whisper_response, 35, max_lines=6, placeholder=' ~')
    info_text2.config(text=wrapped_text)
    print("Whisper response:", whisper_response)
    time_bar.config(color=red_bar)

def btn_b_rising_handler(pin):
    print("Pressed button B (digest audio file)")
    info_text1.config(text='Digesting Chat...')
    time_bar.config(color=yellow_bar)
    previous_messages.append({"role": "user", "content": whisper_response})
    response_text = get_response_from_openai(previous_messages)
    previous_messages.append({"role": "assistant", "content": response_text})
    wrapped_text = textwrap.fill(response_text, 35, max_lines=8, placeholder=' ~')
    info_text1.config(text=wrapped_text)
    print("ChatGPT response:", response_text)
    time_bar.config(color=red_bar)

def timed_audio_record(duration=5):
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 44100
    seconds = duration
    frames = []
    p = pyaudio.PyAudio()
    
    print('Recording')
    time_bar.config(color=green_bar)
    stream = p.open(
        format=sample_format,
        channels=channels,
        rate=fs,
        frames_per_buffer=chunk,
        input=True)
    for i in range(0, int(fs / chunk * seconds)):
        time_perc = i/int(fs / chunk * seconds)
        time_bar.config(x0=20, x1=20+(time_perc * 200))
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    print('Finished recording')
    wf = wave.open(output_filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()
    
def whisper_digest(file_name):
    try:
        file = open(file_name, "rb")
        return openai.Audio.transcribe("whisper-1", file)["text"]
    except Exception as e:
        return "Unknown OpenAI Whisper Error: " + str(e)    
    
def get_response_from_openai(previous_messages):
    try:
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = previous_messages,
            temperature = 0.2,
            max_tokens = 3500,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return "Unknown OpenAI ChatGPT Error: " + str(e)

# Register interrupt event handlers for buttons
button_a.irq(trigger=Pin.IRQ_RISING, handler=btn_a_rising_handler)  # Trigger a on rising edge
button_b.irq(trigger=Pin.IRQ_RISING, handler=btn_b_rising_handler)  # Trigger b on rising edge

while True:
    time.sleep(.1)
