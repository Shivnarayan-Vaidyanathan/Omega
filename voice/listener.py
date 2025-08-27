import speech_recognition as sr
import time

DEBUG = True  # set to False if you don’t want live threshold updates


def setup_listener():
    """Initialize recognizer and microphone with adaptive threshold"""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("🎧 Calibrating for background noise... please stay quiet")
        recognizer.adjust_for_ambient_noise(source, duration=2)

        # Enable dynamic adaptation
        recognizer.dynamic_energy_threshold = True
        recognizer.dynamic_energy_adjustment_damping = 0.1   # faster adaptation
        recognizer.dynamic_energy_ratio = 0.1                # speech must be ~30% louder than noise

        print(f"✅ Calibration complete. Starting energy threshold: {recognizer.energy_threshold}")

    return recognizer, mic


def listen_command(recognizer, mic, wake_word=None):
    """Listen for command, return recognized text"""
    with mic as source:
        try:
            if DEBUG:
                print("📡 Listening... (energy threshold will adapt)")
                # Show live threshold values every 0.5s while waiting
                for _ in range(10):  
                    #print(f"🔎 Current threshold: {recognizer.energy_threshold}")
                    time.sleep(0.5)

            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            command = recognizer.recognize_google(audio, language="en-IN").lower()
            print(f"🎤 Heard: {command}")

            if wake_word:
                # Wake word mode (must match exact word)
                if wake_word in command.split():
                    return command
                else:
                    return None
            else:
                return command

        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"⚠️ Speech service error: {e}")
            return None