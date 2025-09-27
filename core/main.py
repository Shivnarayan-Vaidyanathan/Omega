import sys
import os
import time
import ctypes
import subprocess
import numpy as np
import sounddevice as sd
import whisper
from threading import Thread
import string  # ✅ For punctuation removal

# Import services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from voice import speaker
from apps import launcher_service
from web import search_service, site_service
from rpa import voice_rpa
from rpa import youtube_tools

# Wake words / aliases
WAKE_ALIASES = ["omega", "hello", "hey omega", "okay omega"]

# Keywords for app control
LAUNCH_KEYWORDS = ["open", "launch", "start", "run"]
CLOSE_KEYWORDS = ["close", "quit"]

# Configurable commands
EXIT_COMMANDS = ["bye"]   # Normal shutdown
SLEEP_COMMANDS = ["thanks", "thank you"]

# Whisper setup
MODEL = whisper.load_model("small")
SAMPLE_RATE = 16000
CHANNELS = 1

# Track admin mode and dry-run mode
IS_ADMIN_MODE = False
DRY_RUN_MODE = False


def is_admin():
    """Check if running as administrator (Windows only)."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """Restart the script as administrator if not already elevated."""
    global IS_ADMIN_MODE
    if not is_admin():
        print("⚠️ Restarting with administrator privileges...")
        speaker.speak("Restarting with administrator rights. Please approve.")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        IS_ADMIN_MODE = True
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    else:
        IS_ADMIN_MODE = True


def get_wifi_interface():
    """Return the Wi-Fi interface name dynamically."""
    try:
        output = subprocess.check_output('netsh interface show interface', shell=True, text=True)
        for line in output.splitlines():
            line_lower = line.lower()
            if "wireless" in line_lower or "wi-fi" in line_lower or "wi fi" in line_lower:
                parts = line.split()
                interface_name = " ".join(parts[3:]) if len(parts) >= 4 else parts[-1]
                print(f"Detected Wi-Fi interface: '{interface_name}'")
                return interface_name
    except Exception as e:
        print(f"⚠️ Could not detect Wi-Fi interface: {e}")
    return None


def get_last_connected_wifi():
    """Get the most recently connected Wi-Fi profile."""
    try:
        output = subprocess.check_output("netsh wlan show profiles", shell=True, text=True)
        profiles = []
        for line in output.splitlines():
            if "All User Profile" in line:
                profile_name = line.split(":")[1].strip()
                profiles.append(profile_name)
        if profiles:
            # Return the most recently added/last profile
            return profiles[-1]
    except Exception as e:
        print(f"⚠️ Could not retrieve Wi-Fi profiles: {e}")
    return None


def enable_wifi(interface_name, profile_name=None):
    """Enable Wi-Fi interface and optionally connect to a profile."""
    if not interface_name:
        speaker.speak("⚠️ No Wi-Fi interface found.")
        return False

    ret_code = os.system(f'netsh interface set interface name="{interface_name}" admin=ENABLED')
    if ret_code != 0:
        speaker.speak("⚠️ Failed to enable Wi-Fi interface.")
        return False

    time.sleep(3)  # Wait for interface to initialize

    if profile_name:
        ret_code = os.system(f'netsh wlan connect name="{profile_name}"')
        if ret_code != 0:
            speaker.speak(f"⚠️ Wi-Fi enabled but failed to connect to '{profile_name}'")
            return False
        else:
            speaker.speak(f"✅ Wi-Fi connected to '{profile_name}'")
    else:
        speaker.speak("✅ Wi-Fi turned on")
    return True


def disable_wifi(interface_name):
    """Disable Wi-Fi interface."""
    if not interface_name:
        speaker.speak("⚠️ No Wi-Fi interface found.")
        return False
    ret_code = os.system(f'netsh interface set interface name="{interface_name}" admin=DISABLED')
    if ret_code != 0:
        speaker.speak("⚠️ Failed to disable Wi-Fi interface.")
        return False
    else:
        speaker.speak("✅ Wi-Fi turned off")
    return True


def listen_command(duration=5) -> str | None:
    """Record audio and transcribe with Whisper."""
    print("🎙 Listening...")
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="float32")
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


def clean_app_name(followup: str, keyword_list: list[str]) -> str:
    """Remove keyword prefixes and punctuation for app matching."""
    for kw in keyword_list:
        if followup.startswith(kw):
            name = followup[len(kw):].strip()
            return name.translate(str.maketrans('', '', string.punctuation))
    return followup.translate(str.maketrans('', '', string.punctuation))


def handle_web_search(followup: str):
    """Handles search queries."""
    followup = followup.lower()
    if "search" in followup:
        query = followup.replace("search", "").strip()
        search_service.search_web(query)
        speaker.speak(f"Searching for {query}")
    elif "google" in followup:
        query = followup.replace("google", "").strip()
        search_service.search_web(query, "google")
        speaker.speak(f"Searching Google for {query}")
    elif "bing" in followup:
        query = followup.replace("bing", "").strip()
        search_service.search_web(query, "bing")
        speaker.speak(f"Searching Bing for {query}")
    elif "duckduckgo" in followup:
        query = followup.replace("duckduckgo", "").strip()
        search_service.search_web(query, "duckduckgo")
        speaker.speak(f"Searching DuckDuckGo for {query}")
    else:
        speaker.speak("I couldn’t understand the search request.")


def main():
    global IS_ADMIN_MODE, DRY_RUN_MODE
    speaker.speak(
        "Omega is online. Say 'omega' or 'hello' to wake me up, 'thanks' to pause, or 'bye' to exit."
    )

    while True:
        command = listen_command()
        if not command:
            continue

        # ✅ Global shutdown at top-level
        if any(exit_command in command for exit_command in EXIT_COMMANDS):
            speaker.speak("Shutting down completely. Goodbye!")
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)

        # ✅ Global sleep
        if any(sleep in command for sleep in SLEEP_COMMANDS):
            speaker.speak("You're welcome! Returning to sleep mode.")
            continue

        # ✅ Wake word detection
        if any(alias in command for alias in WAKE_ALIASES):
            print(f"✨ Wake word detected! Heard: {command}")
            speaker.speak(
                "Yes, I'm listening. You can give multiple commands. Say 'thanks' to pause, 'stop' to exit, or switch to admin/normal mode."
            )

            while True:
                followup = listen_command()
                if not followup:
                    speaker.speak("I didn’t hear anything.")
                    continue

                print(f"🎯 User said: {followup}")

                # ✅ Global shutdown inside follow-up loop
                if any(exit_command in followup for exit_command in EXIT_COMMANDS):
                    speaker.speak("Shutting down completely. Goodbye!")
                    try:
                        sys.exit(0)
                    except SystemExit:
                        os._exit(0)

                # ✅ Sleep mode inside follow-up
                if any(sleep_cmd in followup for sleep_cmd in SLEEP_COMMANDS):
                    speaker.speak("You're welcome! Returning to sleep mode.")
                    break

                # ✅ Admin mode switching
                if "switch to admin" in followup and not IS_ADMIN_MODE:
                    speaker.speak("This action requires administrative privileges. Please say yes to proceed.")
                    approval = listen_command()
                    if approval and "yes" in approval:
                        run_as_admin()
                        speaker.speak("Switched to admin mode successfully.")
                    else:
                        speaker.speak("Continuing in normal mode.")
                    continue

                if "switch to normal" in followup and IS_ADMIN_MODE:
                    IS_ADMIN_MODE = False
                    speaker.speak("Switched to normal mode.")
                    continue

                # ✅ Dry-run mode switching
                if "enable dry run" in followup:
                    DRY_RUN_MODE = True
                    speaker.speak("Dry run mode enabled. RPA sessions will only log actions.")
                    continue

                if "disable dry run" in followup:
                    DRY_RUN_MODE = False
                    speaker.speak("Dry run mode disabled. RPA sessions will perform real actions.")
                    continue

                # 👉 Wi-Fi / Internet control (dynamic)
                if "wifi" in followup or "internet" in followup:
                    wifi_name = get_wifi_interface()
                    last_profile = get_last_connected_wifi()
                    if "on" in followup or "enable" in followup:
                        enable_wifi(wifi_name, last_profile)
                        continue
                    elif "off" in followup or "disable" in followup:
                        disable_wifi(wifi_name)
                        continue
                    elif "connect" in followup:
                        os.system("start ms-settings:network-wifi")
                        speaker.speak("Opening Wi-Fi connection panel")
                        continue

                # 👉 Launch app
                app_name = clean_app_name(followup, LAUNCH_KEYWORDS)
                if launcher_service.launch_app(app_name):
                    speaker.speak(f"Launching {app_name}")
                    continue

                # 👉 Close app (web-app-safe)
                app_name = clean_app_name(followup, CLOSE_KEYWORDS)
                if launcher_service.close_app(app_name):
                    speaker.speak(f"Closing {app_name}")
                    continue

                # 👉 Try RPA session with dry_run
                if voice_rpa.run_session(followup, dry_run=DRY_RUN_MODE):
                    speaker.speak(f"Running automation session: {followup}")
                    continue

                # 👉 Open site
                site_name = clean_app_name(followup, LAUNCH_KEYWORDS)
                site = site_service.open_site(site_name)
                if site:
                    speaker.speak(f"Opening {site}")
                    continue

                # 👉 Web search
                if any(word in followup for word in ["search", "google", "bing", "duckduckgo"]):
                    handle_web_search(followup)
                    continue

                # 👉 YouTube video commands
                if "play video" in followup or "youtube" in followup:
                    speaker.speak("Playing YouTube video...")
                    Thread(target=youtube_tools.auto_skip_ads, args=(300, 2), daemon=True).start()
                    continue

                # If nothing matched
                speaker.speak("Sorry, I don’t know that command yet.")


if __name__ == "__main__":
    main()