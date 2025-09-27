import json
import time
import os
from pynput import mouse, keyboard
from datetime import datetime
import pyautogui
import win32gui  # for window titles
import io
import base64

SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)

class Recorder:
    def __init__(self):
        self.events = []
        self.start_time = None
        self.next_tag = None  # manual tag for next action

    def _get_active_window(self):
        """Return title of the currently active window."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(hwnd)
        except Exception:
            return "Unknown"

    def _take_screenshot(self, x, y):
        """Capture a small 50x50 screenshot around (x, y) and encode in base64."""
        try:
            box = (x - 25, y - 25, 50, 50)  # 50x50 area
            screenshot = pyautogui.screenshot(region=box)
            buffer = io.BytesIO()
            screenshot.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode("utf-8")
        except Exception as e:
            print(f"⚠️ Screenshot failed: {e}")
            return None

    def _get_new_session_file(self):
        """Always create a new JSON file for the session."""
        filename = f"session_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        return os.path.join(SESSIONS_DIR, filename)

    def _record_event(self, action, details):
        timestamp = time.time() - self.start_time
        window = self._get_active_window()

        event = {
            "time": round(timestamp, 3),
            "action": action,
            "details": details,
            "window": window,
        }

        # Add description
        if action == "mouse_click":
            event["description"] = f"Mouse {details['button']} {'down' if details['pressed'] else 'up'} at ({details['x']},{details['y']})"
        elif action == "mouse_scroll":
            event["description"] = f"Scroll at ({details['x']},{details['y']})"
        elif action in ["key_press", "key_release"]:
            event["description"] = f"Key {action.split('_')[1]}: {details['key']}"
        else:
            event["description"] = f"{action}"

        # Add tag if available
        if self.next_tag:
            event["tag"] = self.next_tag
            self.next_tag = None

        self.events.append(event)

    def record(self):
        self.start_time = time.time()
        print("🎥 Recording started... Press ESC to stop, F2 to tag next action.")

        # --- Mouse ---
        def on_click(x, y, button, pressed):
            screenshot_data = None
            if pressed:
                screenshot_data = self._take_screenshot(x, y)

            details = {
                "x": x,
                "y": y,
                "button": str(button),
                "pressed": pressed,
                "screenshot": screenshot_data,
            }
            self._record_event("mouse_click", details)

        def on_scroll(x, y, dx, dy):
            self._record_event(
                "mouse_scroll",
                {"x": x, "y": y, "dx": dx, "dy": dy},
            )

        # --- Keyboard ---
        def on_press(key):
            try:
                k = key.char
            except AttributeError:
                k = str(key)

            # F2 = tagging mode
            if k == "Key.f2":
                self.next_tag = input("🏷 Enter tag for next action: ")
                print(f"✅ Tag '{self.next_tag}' will be applied to the next event.")
                return

            self._record_event("key_press", {"key": k})

            if key == keyboard.Key.esc:  # stop recording
                return False

        def on_release(key):
            try:
                k = key.char
            except AttributeError:
                k = str(key)
            self._record_event("key_release", {"key": k})

        mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
        keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

        mouse_listener.start()
        keyboard_listener.start()
        keyboard_listener.join()  # wait until ESC pressed
        mouse_listener.stop()

        # --- Save session to new file ---
        filepath = self._get_new_session_file()
        with open(filepath, "w") as f:
            json.dump(self.events, f, indent=2)

        print(f"✅ Session saved: {filepath}")
        return filepath


if __name__ == "__main__":
    Recorder().record()