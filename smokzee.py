import discord
import asyncio
import speech_recognition as sr
import librosa
import sounddevice as sd
from gtts import gTTS
import os

BOT_TOKEN = 'MTI4MzM0MDMxNDQ2MjkxMjUzMg.GVIgaq.6TWSILkxYUrQ1dwrsZ8pq43vf0ybruInR1xjGY'
IP_RESPONSE = "The IP is play.magmc.xyz"

recognizer = sr.Recognizer()
frames = []

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    channel = client.get_channel('1135664708419063830')
    await channel.connect()
    await listen_for_commands(channel)


async def listen_for_commands(channel):
    while True:
        try:
            await listen_for_voice(channel)
            if len(frames) > 0:
                text = await process_voice_command(frames)
                if text:
                    if "what is the ip" in text:
                        await respond_with_voice(channel, IP_RESPONSE)
                    else:
                        await respond_with_voice(channel, text)
                frames = []
        except Exception as e:
            print(f'Error: {e}')

async def listen_for_voice(channel):
    voice_client = client.voice_client
    audio_input = voice_client.audio_input
    audio_source = voice_client.source
    while True:
        frame = audio_input.read(160)
        frames.append(frame)
        if librosa.effects.vad(frame, sr=16000, hop_length=160, vad_mode="aggressive"):
            continue
        if len(frames) > 1000:
            break

async def process_voice_command(frames):
    audio = b''.join(frames)
    with sr.AudioData(audio, sample_rate=16000) as audio_data:
        text = recognizer.recognize_google(audio_data)
    return text.lower()

async def respond_with_voice(channel, text):
    speech = gTTS(text=text, lang='en')
    speech.save("temp.wav")
    voice_client = client.voice_client
    audio_source = discord.FFmpegAudioSource("temp.wav")
    voice_client.play(audio_source, after=lambda e: print(f"Finished playing: {e}"))
    await asyncio.sleep(audio_source.duration)
    os.remove("temp.wav")

client.run(BOT_TOKEN)
