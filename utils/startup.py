import os
import sys

try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False

from config import APP_NAME

RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


class StartupManager:

    def __init__(self, app_name: str = APP_NAME):
        self.app_name = app_name

    def _get_executable_path(self) -> str:
        if getattr(sys, "frozen", False):
            return f'"{sys.executable}"'
        script_path = os.path.abspath(sys.argv[0])
        python_exe = sys.executable.replace("python.exe", "pythonw.exe")
        return f'"{python_exe}" "{script_path}"'

    def is_enabled(self) -> bool:
        if not WINREG_AVAILABLE:
            return False
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_READ) as key:
                winreg.QueryValueEx(key, self.app_name)
                return True
        except FileNotFoundError:
            return False
        except OSError:
            return False

    def enable(self) -> bool:
        if not WINREG_AVAILABLE:
            return False
        try:
            exe_path = self._get_executable_path()
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, exe_path)
            return True
        except OSError as e:
            print(f"[StartupManager] Automatic activation failed: {e}")
            return False

    def disable(self) -> bool:
        if not WINREG_AVAILABLE:
            return False
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, self.app_name)
            return True
        except FileNotFoundError:
            return True
        except OSError as e:
            print(f"[StartupManager] Automatic cancellation failed: {e}")
            return False

    def set_enabled(self, enabled: bool) -> bool:
        return self.enable() if enabled else self.disable()
