import json
import os
import subprocess
import psutil  # dependency to manage processes
from pathlib import Path
import pygetwindow as gw  # ✅ For window-level closing

APPS_FILE = os.path.join(os.path.dirname(__file__), "apps.json")

# ✅ Synonyms for user-friendly commands
LAUNCH_KEYWORDS = ["open", "launch", "start", "run"]
CLOSE_KEYWORDS = ["close", "quit"]


def load_apps():
    """Load apps from apps.json"""
    if not os.path.exists(APPS_FILE):
        return []
    with open(APPS_FILE, "r") as f:
        data = json.load(f)
        return data.get("apps", [])


def launch_app(app_name):
    """Launch app by name or alias"""
    apps = load_apps()
    app_name_lower = app_name.lower()
    for app in apps:
        if app_name_lower == app["name"].lower() or app_name_lower in [a.lower() for a in app.get("aliases", [])]:
            try:
                print(f"🚀 Launching {app['name']}...")
                subprocess.Popen(app["command"], shell=True)
                return True
            except Exception as e:
                print(f"⚠️ Failed to launch {app['name']}: {e}")
                return False
    print(f"❌ App '{app_name}' not found in registry.")
    return False


def close_app(app_name):
    """Close app by name or alias using process names or window title (for web apps)"""
    apps = load_apps()
    app_name_lower = app_name.lower()

    for app in apps:
        if app_name_lower == app["name"].lower() or app_name_lower in [a.lower() for a in app.get("aliases", [])]:

            # --- Special handling for browser-based apps ---
            if app.get("is_web_app", False):
                try:
                    windows = gw.getWindowsWithTitle(app_name)
                    if not windows:
                        print(f"⚠️ No window found with title containing '{app_name}'")
                        return False
                    for win in windows:
                        print(f"🛑 Closing window: {win.title}")
                        win.close()
                    return True
                except Exception as e:
                    print(f"⚠️ Failed to close window '{app_name}': {e}")
                    return False

            # ✅ Special handling for Calculator (UWP app)
            if app_name_lower in ["calculator", "calc"]:
                try:
                    print(f"🛑 Closing Calculator via taskkill...")
                    ret_code = os.system("taskkill /IM Calculator.exe /F >nul 2>&1")
                    if ret_code == 0:
                        print(f"✅ Calculator closed successfully.")
                        return True
                    else:
                        print(f"⚠️ Calculator was not running.")
                        return False
                except Exception as e:
                    print(f"⚠️ Failed to close Calculator: {e}")
                    return False

            # Use "processes" field if exists, else fallback to basename of command
            process_names = app.get("processes", [])
            if not process_names:
                cmd_path = app.get("command", "")
                if cmd_path:
                    process_names = [Path(cmd_path).name]  # e.g., notepad.exe
                else:
                    print(f"⚠️ No process names or command defined for {app['name']}")
                    return False

            closed = False
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    if proc.info["name"] and proc.info["name"].lower() in [p.lower() for p in process_names]:
                        print(f"🛑 Closing {proc.info['name']} (PID: {proc.info['pid']})...")
                        proc.terminate()
                        closed = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if closed:
                print(f"✅ {app['name']} closed successfully.")
                return True
            else:
                print(f"⚠️ No running processes found for {app['name']}.")
                return False

    print(f"❌ App '{app_name}' not found in registry.")
    return False


# ✅ Simple CLI test harness
if __name__ == "__main__":
    while True:
        action = input("Enter command (open/close/exit): ").strip().lower()
        if action in ["exit", "quit"]:
            break

        parts = action.split(maxsplit=1)
        if len(parts) < 2:
            print("⚠️ Please enter in format: <command> <app>")
            continue

        cmd, app = parts[0], parts[1]

        if cmd in LAUNCH_KEYWORDS:
            launch_app(app)
        elif cmd in CLOSE_KEYWORDS:
            close_app(app)
        else:
            print("⚠️ Unknown command. Try 'open <app>' or 'close <app>'")