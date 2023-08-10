# -*- coding: utf-8 -*-

import openai
import speech_recognition as sr
import elevenlabs
import sounddevice
import soundfile
import io

prompt = """
You are like a helpful assistant or something idk.
"""
init_messsage = "Buh-Nah-Nuh GPT Is Now Activated!"
input_location = "sent_recordings\\input.wav"
previous_messages = [{"role": "system", "content": prompt}]
openai.api_key = ""
elevenlabs.set_api_key("")

class color:
    red = '\x1b[1;31;40m'
    green = '\x1b[1;32;40m'
    yellow = '\x1b[1;33;40m'
    blue = '\x1b[1;34;40m'
    end = '\x1b[0m'

def say(text):
    print(color.blue + "Elevenlabs Digesting" + color.end)
    try:
        audio = elevenlabs.generate(
            text=text,
            voice="Bella",
            model="eleven_monolingual_v1",
        )
        print(color.blue + "Attempting Playback" + color.end)
        sounddevice.play(*soundfile.read(io.BytesIO(audio)),
                         device=sounddevice.query_devices(kind='output')['index'])
        sounddevice.wait()
        print(color.blue + "Finished Playback" + color.end)
    except Exception as e:
        print(color.red + "Unknown Playback ChatGPT Error: " + str(e) + color.end)
        exit()

def get_response_from_openai(previous_messages):
    print(color.blue + "ChatGPT Digesting" + color.end)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=previous_messages,
            temperature=0.2,
            max_tokens=3500,
        )
        print(color.yellow + "ChatGPT Response: " + response["choices"][0]["message"]["content"] + color.end)
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(color.red + "Unknown OpenAI ChatGPT Error: " + str(e) + color.end)
        exit()


def get_transcript_from_audio(file_name):
    print(color.blue + "Whisper Digesting" + color.end)
    try:
        wavfile = open(file_name, "rb")
        transcription = openai.Audio.transcribe("whisper-1", wavfile)["text"]
        print(color.green + 'Voice Input: ' +  transcription + color.end)
        return transcription
    except Exception as e:
        print(color.red + "Unknown OpenAI Whisper Error: " + str(e) + color.end)
        exit()


def record_audio(file_output):
    r = sr.Recognizer()
    print(color.green + 'Recording Starting Now!' + color.end)
    try:
        with sr.Microphone(device_index=sounddevice.query_devices(kind='input')['index']) as source:
            r.adjust_for_ambient_noise(source, duration=0.25)
            audio = r.listen(source)
        with open(file_output, 'wb') as file:
            wav_data = audio.get_wav_data()
            file.write(wav_data)
        print(color.green + 'Finished Recording!' + color.end)
    except Exception as e:
        print(color.red + "Recording Error: " + str(e) + color.end)
        exit()


def digest_voice(previous_messages):
    try:
        record_audio(input_location)
        user_response = get_transcript_from_audio(input_location)
        previous_messages.append({"role": "user", "content": user_response})
        response_text = get_response_from_openai(previous_messages)
        previous_messages.append(
            {"role": "assistant", "content": response_text})
        return response_text
    except Exception as e:
        print(color.red + "Voice Digestion Error: " + str(e) + color.end)
        exit()


if __name__ == '__main__':
    say(init_messsage)
    say(get_response_from_openai(previous_messages))
    while True:
        say(digest_voice(previous_messages))
