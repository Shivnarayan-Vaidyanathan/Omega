# rpa/youtube_tools.py

import pyautogui
import time

def skip_youtube_ad():
    """
    Detects YouTube 'Skip Ad' button on screen and clicks it.
    Returns True if ad was skipped, False otherwise.
    """
    try:
        # Screenshot of Skip Ad button saved as 'skip_ad_button.png'
        button = pyautogui.locateOnScreen("skip_ad_button.png", confidence=0.7)
        if button:
            pyautogui.click(pyautogui.center(button))
            print("✅ Skipped YouTube ad")
            return True
    except Exception as e:
        print(f"⚠️ Error skipping ad: {e}")
    return False

def auto_skip_ads(duration=60, interval=2):
    """
    Continuously checks for Skip Ad button for a given duration.
    Useful for videos with multiple ads in a row.
    """
    start_time = time.time()
    while time.time() - start_time < duration:
        skipped = skip_youtube_ad()
        time.sleep(interval)