import json
import os
import subprocess

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

# For testing
if __name__ == "__main__":
    while True:
        app_to_launch = input("Enter app name to launch: ")
        if app_to_launch.lower() in ["exit", "quit"]:
            break
        launch_app(app_to_launch)