import json
import time
import pyautogui
from input_blocker import InputBlocker

# Disable failsafe (⚠️ careful)
pyautogui.FAILSAFE = False


def play_session(file_path, llm_instructions=None):
    """
    Replays a recorded session from a JSON file.
    Optionally, llm_instructions can modify the playback.
    """

    with open(file_path, "r") as f:
        events = json.load(f)

    print(f"▶️ Replaying session from {file_path}... (Press ESC to stop)")

    blocker = InputBlocker()
    blocker.start_blocking()

    start_time = time.time()
    last_clicks = {}  # track pressed state per button

    for idx, event in enumerate(events):
        if blocker.is_stopped():  # stop if ESC pressed
            print("⏹️ Stopped by user.")
            break

        # --- LLM override hook ---
        if llm_instructions:
            action_override = llm_instructions.get(idx)
            if action_override == "skip":
                print(f"⏭️ Skipping step {idx}")
                continue
            elif isinstance(action_override, dict):
                event = action_override  # replace

        # --- Timing ---
        delay = event["time"] - (time.time() - start_time)
        if delay > 0:
            time.sleep(delay)

        etype = event["action"]
        details = event["details"]

        # === Mouse Clicks ===
        if etype == "mouse_click":
            x, y = details["x"], details["y"]
            button = details["button"].split(".")[-1]
            pressed = details.get("pressed", False)

            if pressed:
                last_clicks[button] = (x, y)
            else:
                if button in last_clicks:
                    px, py = last_clicks.pop(button)
                    pyautogui.click(px, py, button=button)
                    time.sleep(0.1)

        # === Mouse Scroll ===
        elif etype == "mouse_scroll":
            pyautogui.scroll(details["dy"], x=details["x"], y=details["y"])
            time.sleep(0.05)

        # === Keyboard Input ===
        elif etype == "keyboard_input":
            key = details["key"]

            if len(key) == 1:  # normal characters
                pyautogui.typewrite(key)
            else:  # special keys
                special_key = key.replace("Key.", "")
                try:
                    pyautogui.press(special_key)
                except Exception:
                    print(f"⚠️ Unsupported key: {key}")
            time.sleep(0.05)

        # === Future: LLM Action ===
        elif etype == "llm_action":
            print(f"🤖 LLM action: {details['command']}")
            # Placeholder for AI integration

    blocker.stop_blocking()
    print("✅ Session finished.")