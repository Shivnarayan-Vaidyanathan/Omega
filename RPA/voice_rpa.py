# rpa/voice_rpa.py

import os
import numpy as np
import sounddevice as sd
import whisper
from fuzzywuzzy import process
from .player import play_session

# Folder where sessions are saved
SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "sessions")

# Map voice commands to session files
VOICE_COMMANDS = {
    "defense matrix": "defense_matrix.json",
    "idu": "idu.json",
    "wifi": "wifi.json"
}

# Load Whisper model once
MODEL = whisper.load_model("small")

SAMPLE_RATE = 16000
CHANNELS = 1

# Track dry-run mode
DRY_RUN_MODE = False

def record_and_transcribe(duration=5) -> str | None:
    """
    Record mic input for given duration and transcribe with Whisper.
    Returns recognized text (lowercase) or None if nothing captured.
    """
    print("🎙 Listening for RPA command...")
    audio = sd.rec(int(duration * SAMPLE_RATE),
                   samplerate=SAMPLE_RATE,
                   channels=CHANNELS,
                   dtype="float32")
    sd.wait()

    try:
        result = MODEL.transcribe(audio.flatten(),
                                  fp16=False,
                                  language="en")
        text = result.get("text", "").strip()
        if text:
            print(f"🗣 You said: {text}")
            return text.lower()
    except Exception as e:
        print(f"⚠️ Whisper transcription failed: {e}")

    return None

def run_session(command: str, dry_run=False, llm_instructions=None):
    """
    Match the voice command to a recorded session and play it.
    """
    choices = VOICE_COMMANDS.keys()
    match, score = process.extractOne(command, choices)
    if score >= 80:  # only match if similarity is high
        session_file = VOICE_COMMANDS[match]
        file_path = os.path.join(SESSIONS_DIR, session_file)
        if os.path.exists(file_path):
            print(f"▶️ Running session for '{match}'{' (dry-run)' if dry_run else ''}...")
            play_session(file_path, llm_instructions=llm_instructions, dry_run=dry_run)
            return True
    return False

def main():
    """
    Standalone mode: run RPA sessions via direct voice input.
    Supports toggling dry-run mode via voice.
    """
    global DRY_RUN_MODE
    while True:
        command = record_and_transcribe()
        if not command:
            continue

        # Toggle dry-run mode
        if "dry run on" in command:
            DRY_RUN_MODE = True
            print("⚡ Dry-run mode activated. No clicks or keystrokes will be performed.")
            continue
        elif "dry run off" in command:
            DRY_RUN_MODE = False
            print("✅ Dry-run mode deactivated. Sessions will execute normally.")
            continue

        # Run session
        if run_session(command, dry_run=DRY_RUN_MODE):
            continue

        # Exit
        elif "exit" in command or "quit" in command:
            print("👋 Exiting Voice RPA.")
            break
        else:
            print("🤔 Command not recognized.")

if __name__ == "__main__":
    main()