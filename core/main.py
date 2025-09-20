import sys
import os
import time
import numpy as np
import sounddevice as sd
import whisper

# Import services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from voice import speaker
from apps import launcher_service
from web import search_service, site_service
from rpa import voice_rpa   # ✅ Import RPA service
from rpa import youtube_tools

# Wake words / aliases
WAKE_ALIASES = ["omega", "hello", "hey omega", "okay omega"]

# ✅ Configurable commands
EXIT_COMMANDS = ["shutdown", "exit program", "terminate", "quit"]
SLEEP_COMMANDS = ["thanks", "thank you"]

# Whisper setup
MODEL = whisper.load_model("small")
SAMPLE_RATE = 16000
CHANNELS = 1


def listen_command(duration=5) -> str | None:
    """
    Record audio for given duration and transcribe with Whisper.
    Returns recognized text (lowercase) or None.
    """
    print("🎙 Listening...")
    audio = sd.rec(int(duration * SAMPLE_RATE),
                   samplerate=SAMPLE_RATE,
                   channels=CHANNELS,
                   dtype="float32")
    sd.wait()

    try:
        result = MODEL.transcribe(audio.flatten(), fp16=False, language="en")
        text = result.get("text", "").strip()
        if text:
            print(f"🗣 Heard: {text}")
            return text.lower()
    except Exception as e:
        print(f"⚠️ Whisper transcription failed: {e}")

    return None


def main():
    speaker.speak(
        "Omega is online. Say 'omega' or 'hello' to wake me up, 'thanks' to pause, or 'shutdown' to exit completely."
    )

    while True:
        command = listen_command()

        if command:
            # ✅ Global shutdown
            if any(exit_cmd in command for exit_cmd in EXIT_COMMANDS):
                speaker.speak("Shutting down completely. Goodbye!")
                sys.exit(0)

            # ✅ Wake word detection (flexible matching)
            if any(alias in command for alias in WAKE_ALIASES):
                print(f"✨ Wake word detected! Heard: {command}")
                speaker.speak("Yes, I'm listening. You can give multiple commands. Say 'thanks' to pause or 'shutdown' to exit.")

                # Enter follow-up command session
                while True:
                    followup = listen_command()
                    if followup:
                        print(f"🎯 User said: {followup}")

                        # ✅ Shutdown inside follow-up loop
                        if any(exit_cmd in followup for exit_cmd in EXIT_COMMANDS):
                            speaker.speak("Shutting down completely. Goodbye!")
                            sys.exit(0)

                        # ✅ Sleep mode commands
                        if any(sleep_cmd in followup for sleep_cmd in SLEEP_COMMANDS):
                            speaker.speak("You're welcome! Returning to sleep mode.")
                            break  # exit follow-up session

                        # 👉 Try launching an app
                        if launcher_service.launch_app(followup):
                            speaker.speak(f"Launching {followup}")
                            continue

                        # 👉 Try closing an app
                        if launcher_service.close_app(followup):
                            speaker.speak(f"Closing {followup}")
                            continue

                        # 👉 Try RPA session
                        if voice_rpa.run_session(followup):
                            speaker.speak(f"Running automation session: {followup}")
                            continue

                        # 👉 Try opening a site
                        site = site_service.open_site(
                            followup.replace("open", "").replace("launch", "").strip()
                        )
                        if site:
                            speaker.speak(f"Opening {site}")
                            continue

                        # 👉 Try web search
                        if any(word in followup for word in ["search", "google", "bing", "duckduckgo"]):
                            handle_web_search(followup)
                            continue

                        if "play video" in followup or "youtube" in followup:
                           # launch video as usual
                           speaker.speak("Playing YouTube video...")
    
                           # Start ad skip loop in background
                           from threading import Thread
                           Thread(target=youtube_tools.auto_skip_ads, args=(300, 2), daemon=True).start()

                        # 👉 If nothing matched
                        speaker.speak("Sorry, I don’t know that command yet.")
                    else:
                        speaker.speak("I didn’t hear anything.")


def handle_web_search(followup: str):
    """Handles search queries based on keyword (Google, Bing, DuckDuckGo, etc.)"""
    followup = followup.lower()

    if "search" in followup:
        query = followup.replace("search", "").strip()
        search_service.search_web(query)
        speaker.speak(f"Searching for {query}")
        return

    elif "google" in followup:
        query = followup.replace("google", "").strip()
        search_service.search_web(query, "google")
        speaker.speak(f"Searching Google for {query}")
        return

    elif "bing" in followup:
        query = followup.replace("bing", "").strip()
        search_service.search_web(query, "bing")
        speaker.speak(f"Searching Bing for {query}")
        return

    elif "duckduckgo" in followup:
        query = followup.replace("duckduckgo", "").strip()
        search_service.search_web(query, "duckduckgo")
        speaker.speak(f"Searching DuckDuckGo for {query}")
        return

    else:
        speaker.speak("I couldn’t understand the search request.")


if __name__ == "__main__":
    main()