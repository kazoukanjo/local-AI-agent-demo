from PySide6.QtCore import QObject,Signal
class HotkeyController(QObject):
    activated=Signal()
    def __init__(self,hotkey='ctrl+shift+space'):
        super().__init__(); self.listener=None; self.hotkey=hotkey
    def start(self):
        try:
            from pynput import keyboard
            combo='<ctrl>+<shift>+<space>'
            hk=keyboard.HotKey(keyboard.HotKey.parse(combo),self.activated.emit)
            def canonical(f): return lambda key:f(self.listener.canonical(key))
            self.listener=keyboard.Listener(on_press=canonical(hk.press),on_release=canonical(hk.release)); self.listener.daemon=True; self.listener.start(); return True
        except Exception as e: print('Hotkey disabled:',e); return False
    def stop(self):
        if self.listener:
            try:self.listener.stop()
            except Exception:pass
