import os
from recorder import Recorder
from player import play_session

SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "..", "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)

if __name__ == "__main__":
    print("🤖 Omega RPA CLI")
    print("1. Record session")
    print("2. Play session")
    choice = input("Choose option (1/2): ").strip()

    if choice == "1":
        Recorder().record()
    elif choice == "2":
        sessions = [
            f for f in os.listdir(SESSIONS_DIR) if f.endswith(".json")
        ]
        if not sessions:
            print("⚠️ No sessions found.")
        else:
            for i, s in enumerate(sessions):
                print(f"{i+1}. {s}")
            sel = int(input("Select session number: ")) - 1
            play_session(os.path.join(SESSIONS_DIR, sessions[sel]))