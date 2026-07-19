from typing import Callable, Dict, Optional

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False


class ShortcutManager:

    def __init__(self):
        self._registered_hotkeys: Dict[str, str] = {}  # name -> hotkey string

    def is_available(self) -> bool:
        return KEYBOARD_AVAILABLE

    def register(self, name: str, hotkey: str, callback: Callable) -> bool:
        if not KEYBOARD_AVAILABLE:
            return False
        try:
            self.unregister(name)
            keyboard.add_hotkey(hotkey, callback)
            self._registered_hotkeys[name] = hotkey
            return True
        except Exception as e:
            print(f"[ShortcutManager] Shortcut registration failed '{hotkey}': {e}")
            return False

    def unregister(self, name: str) -> None:
        if not KEYBOARD_AVAILABLE:
            return
        hotkey = self._registered_hotkeys.pop(name, None)
        if hotkey:
            try:
                keyboard.remove_hotkey(hotkey)
            except (KeyError, ValueError):
                pass

    def update(self, name: str, new_hotkey: str, callback: Callable) -> bool:
        self.unregister(name)
        return self.register(name, new_hotkey, callback)

    def unregister_all(self) -> None:
        if not KEYBOARD_AVAILABLE:
            return
        for name in list(self._registered_hotkeys.keys()):
            self.unregister(name)

    def get_current_hotkey(self, name: str) -> Optional[str]:
        return self._registered_hotkeys.get(name)
