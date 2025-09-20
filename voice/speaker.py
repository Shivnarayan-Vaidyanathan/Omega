import pyttsx3

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty("rate", 175)   # speed of speech
engine.setProperty("volume", 0)   # volume (0.0 to 1.0)

def speak(text: str):
    """Speak text aloud"""
    print(f"🗣️ Omega says: {text}")
    engine.say(text)
    engine.runAndWait()