import json
import time
import pyautogui
import os
import base64
import io
from PIL import Image
import pygetwindow as gw
from .input_blocker import InputBlocker


def _focus_window(window_title):
    """Try to focus a window by its title (best-effort)."""
    try:
        for w in gw.getWindowsWithTitle(window_title):
            if not w.isActive:
                w.activate()
            return True
    except Exception:
        pass
    return False


def _find_image_on_screen(img_data):
    """Try to locate a screenshot snippet on the screen."""
    try:
        image_bytes = base64.b64decode(img_data)
        img = Image.open(io.BytesIO(image_bytes))
        location = pyautogui.locateOnScreen(img, confidence=0.85)
        if location:
            return pyautogui.center(location)
    except Exception as e:
        print(f"⚠️ Image match failed: {e}")
    return None


def play_session(file_path, llm_instructions=None, dry_run=False):
    """
    Replays a recorded session from a JSON file.
    Uses window info, image matching, or coordinates as fallbacks.
    Supports 'dry_run' mode for simulation/testing without actual clicks/typing.
    """
    with open(file_path, "r") as f:
        events = json.load(f)

    print(f"▶️ Replaying session from {file_path}... (Press ESC to stop)")
    blocker = InputBlocker()
    blocker.start_blocking()
    start_time = time.time()
    last_clicks = {}

    for idx, event in enumerate(events):
        if blocker.is_stopped():
            print("⏹️ Stopped by user.")
            break

        # --- LLM Override Hook ---
        if llm_instructions:
            action_override = llm_instructions.get(idx)
            if action_override == "skip":
                print(f"⏭️ Skipping step {idx}")
                continue
            elif isinstance(action_override, dict):
                event = action_override

        # --- Timing ---
        delay = event["time"] - (time.time() - start_time)
        if delay > 0:
            time.sleep(delay)

        etype = event["action"]
        details = event["details"]
        tag = details.get("tag")
        desc = details.get("description")
        if tag or desc:
            print(f"📝 Step {idx}: {tag or ''} {desc or ''}".strip())

        # === Mouse Clicks ===
        if etype == "mouse_click":
            x, y = details["x"], details["y"]
            button = details["button"].split(".")[-1]
            pressed = details.get("pressed", False)

            if not pressed:  # only handle release to perform click
                pos = None
                action_desc = f"Click at ({x},{y}) with {button}"
                
                # Try window focus
                if details.get("window") and _focus_window(details["window"]):
                    pos = (x, y)
                    action_desc += f" in window '{details['window']}'"
                # Try screenshot matching
                elif details.get("screenshot"):
                    center_pos = _find_image_on_screen(details["screenshot"])
                    if center_pos:
                        pos = (center_pos.x, center_pos.y)
                        action_desc += " using screenshot match"
                    else:
                        print("⚠️ Screenshot not found, using raw coords")
                        pos = (x, y)
                else:
                    pos = (x, y)

                if dry_run:
                    print(f"[DRY RUN] Would {action_desc}")
                else:
                    pyautogui.click(pos[0], pos[1], button=button)
                    time.sleep(0.1)

        # === Mouse Scroll ===
        elif etype == "mouse_scroll":
            dx, dy = details.get("dx", 0), details.get("dy", 0)
            if dry_run:
                print(f"[DRY RUN] Would scroll dx={dx}, dy={dy} at ({details['x']},{details['y']})")
            else:
                pyautogui.scroll(dy, x=details["x"], y=details["y"])
                time.sleep(0.05)

        # === Keyboard Input ===
        elif etype == "key_press":
            key = details["key"]
            if len(key) == 1:
                if dry_run:
                    print(f"[DRY RUN] Would press key '{key}'")
                else:
                    pyautogui.keyDown(key)
            else:
                special_key = key.replace("Key.", "")
                if dry_run:
                    print(f"[DRY RUN] Would press special key '{special_key}'")
                else:
                    try:
                        pyautogui.keyDown(special_key)
                    except Exception:
                        print(f"⚠️ Unsupported key: {key}")

        elif etype == "key_release":
            key = details["key"]
            if len(key) == 1:
                if dry_run:
                    print(f"[DRY RUN] Would release key '{key}'")
                else:
                    pyautogui.keyUp(key)
            else:
                special_key = key.replace("Key.", "")
                if dry_run:
                    print(f"[DRY RUN] Would release special key '{special_key}'")
                else:
                    try:
                        pyautogui.keyUp(special_key)
                    except Exception:
                        print(f"⚠️ Unsupported key: {key}")

        # === Future: LLM Action ===
        elif etype == "llm_action":
            print(f"🤖 LLM action: {details['command']}")

    blocker.stop_blocking()
    print("✅ Session finished.")