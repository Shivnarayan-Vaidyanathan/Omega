import sys
import os
import time

# Import services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from voice import listener, speaker
from apps import launcher_service
from web import search_service, site_service   # ✅ new imports

# Wake word
WAKE_WORD = "omega"

# ✅ Configurable commands
EXIT_COMMANDS = ["shutdown", "exit program", "terminate", "quit"]
SLEEP_COMMANDS = ["thanks", "thank you"]


def main():
    recognizer, mic = listener.setup_listener()
    speaker.speak("Omega is online. Say 'omega' to wake me up, 'thanks' to pause, or 'shutdown' to exit completely.")

    while True:
        command = listener.listen_command(recognizer, mic)

        if command:
            print(f"🗣 Heard: {command}")
            command = command.lower()

            # ✅ Global shutdown
            if any(exit_cmd in command for exit_cmd in EXIT_COMMANDS):
                speaker.speak("Shutting down completely. Goodbye!")
                sys.exit(0)

            # Wake word detected
            if WAKE_WORD in command.split():
                print(f"✨ Wake word detected! Heard: {command}")
                speaker.speak("Yes, I'm listening. You can give multiple commands. Say 'thanks' to pause or 'shutdown' to exit.")

                # Enter follow-up command session
                while True:
                    followup = listener.listen_command(recognizer, mic)
                    if followup:
                        print(f"🎯 User said: {followup}")
                        followup = followup.lower()

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

                        # 👉 Try opening a site
                        site = site_service.open_site(followup.replace("open", "").replace("launch", "").strip())
                        if site:
                            speaker.speak(f"Opening {site}")
                            continue

                        # 👉 Try web search
                        if any(word in followup for word in ["search", "google", "bing", "duckduckgo"]):
                            handle_web_search(followup)
                            continue

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