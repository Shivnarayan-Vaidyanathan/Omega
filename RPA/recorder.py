import json
import time
import os
from pynput import mouse, keyboard
from datetime import datetime

SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "..", "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)


class Recorder:
    def __init__(self):
        self.events = []
        self.start_time = None

    def _record_event(self, action, details):
        timestamp = time.time() - self.start_time
        self.events.append({
            "time": round(timestamp, 3),
            "action": action,
            "details": details
        })

    def record(self):
        self.start_time = time.time()
        print("🎥 Recording started... Press ESC to stop.")

        def on_click(x, y, button, pressed):
            self._record_event(
                "mouse_click",
                {"x": x, "y": y, "button": str(button), "pressed": pressed}
            )

        def on_scroll(x, y, dx, dy):
            self._record_event(
                "mouse_scroll",
                {"x": x, "y": y, "dx": dx, "dy": dy}
            )

        def on_press(key):
            try:
                k = key.char
            except AttributeError:
                k = str(key)
            self._record_event("keyboard_input", {"key": k})
            if key == keyboard.Key.esc:  # stop recording
                return False

        mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
        keyboard_listener = keyboard.Listener(on_press=on_press)

        mouse_listener.start()
        keyboard_listener.start()
        keyboard_listener.join()  # wait until ESC pressed

        mouse_listener.stop()

        filename = f"session_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        filepath = os.path.join(SESSIONS_DIR, filename)

        with open(filepath, "w") as f:
            json.dump(self.events, f, indent=2)

        print(f"✅ Session saved: {filepath}")
        return filepath


if __name__ == "__main__":
    Recorder().record()