from pynput import keyboard, mouse

class InputBlocker:
    """
    Blocks user keyboard + mouse input during playback,
    but does NOT block programmatic inputs from pyautogui.
    """

    def __init__(self):
        self.keyboard_listener = None
        self.mouse_listener = None
        self._stopped = False

    def _block_keyboard(self, key):
        # ESC stops everything
        if key == keyboard.Key.esc:
            self._stopped = True
            return False  # stop keyboard listener
        return False  # Block ALL other keystrokes

    def _block_mouse(self, *args):
        # Block ALL mouse events (move, click, scroll)
        return False

    def start_blocking(self):
        """Starts blocking keyboard + mouse input from the user"""
        self._stopped = False

        self.keyboard_listener = keyboard.Listener(on_press=self._block_keyboard)
        self.mouse_listener = mouse.Listener(
            on_click=self._block_mouse,
            on_scroll=self._block_mouse,
            on_move=self._block_mouse
        )

        self.keyboard_listener.start()
        self.mouse_listener.start()

    def stop_blocking(self):
        """Stops blocking input"""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()

    def is_stopped(self):
        """Check if ESC was pressed by user"""
        return self._stopped