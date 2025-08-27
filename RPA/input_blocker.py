from pynput import keyboard, mouse


class InputBlocker:
    def __init__(self):
        self.kb_listener = None
        self.mouse_listener = None
        self.stop_flag = False

    def start_blocking(self):
        """Block all inputs except ESC"""

        def on_press(key):
            if key == keyboard.Key.esc:
                self.stop_flag = True
                return False  # stop keyboard listener
            return False  # block all keys

        def on_click(x, y, button, pressed):
            return False  # block all clicks

        self.kb_listener = keyboard.Listener(on_press=on_press, suppress=True)
        self.mouse_listener = mouse.Listener(on_click=on_click, suppress=True)

        self.kb_listener.start()
        self.mouse_listener.start()

    def stop_blocking(self):
        """Release inputs"""
        if self.kb_listener:
            self.kb_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()

    def is_stopped(self):
        return self.stop_flag