import json
import os
import subprocess
import signal
import psutil   # new dependency to manage processes

APPS_FILE = os.path.join(os.path.dirname(__file__), "apps.json")

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
    """Close app by name or alias using process name from apps.json"""
    apps = load_apps()
    app_name_lower = app_name.lower()

    for app in apps:
        if app_name_lower == app["name"].lower() or app_name_lower in [a.lower() for a in app.get("aliases", [])]:
            process_names = app.get("processes", [])
            if not process_names:
                print(f"⚠️ No process names defined for {app['name']} in apps.json")
                return False

            closed = False
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    if proc.info["name"] and proc.info["name"].lower() in [p.lower() for p in process_names]:
                        print(f"❌ Closing {proc.info['name']} (PID: {proc.info['pid']})...")
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

# For testing
if __name__ == "__main__":
    while True:
        action = input("Enter 'open <app>' or 'close <app>' (or 'exit'): ").strip().lower()
        if action in ["exit", "quit"]:
            break
        if action.startswith("open "):
            launch_app(action.replace("open ", "", 1))
        elif action.startswith("close "):
            close_app(action.replace("close ", "", 1))
        else:
            print("⚠️ Unknown command. Use 'open <app>' or 'close <app>'")