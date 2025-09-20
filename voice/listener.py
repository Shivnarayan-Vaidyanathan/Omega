# voice/listener.py

import os
import numpy as np
import sounddevice as sd
import whisper

# Load Whisper model once
MODEL = whisper.load_model("small")

SAMPLE_RATE = 16000
CHANNELS = 1

def listen_command(duration=5):
    """
    Records audio from the microphone and transcribes it with Whisper.
    """
    print("🎙 Listening...")
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="float32")
    sd.wait()

    # Transcribe with Whisper
    result = MODEL.transcribe(audio.flatten(), fp16=False, language="en")
    text = result.get("text", "").strip()

    if text:
        print(f"🗣 Heard: {text}")
        return text.lower()
    else:
        print("❌ Did not catch anything")
        return None