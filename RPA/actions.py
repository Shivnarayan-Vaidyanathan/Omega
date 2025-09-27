# rpa/actions.py
import cv2
import pyautogui
import numpy as np
from pywinauto import Application

def click_button(app_title, button_name, fallback_image=None, confidence=0.8):
    """
    Try clicking a UI element via UI Automation first, fallback to image recognition if needed.
    """
    try:
        app = Application(backend="uia").connect(title_re=app_title)
        dlg = app.window(title_re=app_title)
        dlg[button_name].click_input()
        print(f"✅ Clicked '{button_name}' using UIA")
        return True
    except Exception as e:
        print(f"⚠️ UIA failed: {e}")

        if fallback_image:
            screen = pyautogui.screenshot()
            screen = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2GRAY)
            template = cv2.imread(fallback_image, 0)
            res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val >= confidence:
                pyautogui.click(max_loc)
                print(f"✅ Clicked '{button_name}' using fallback image")
                return True
            else:
                print(f"❌ Could not find '{button_name}' in fallback image")

    return False