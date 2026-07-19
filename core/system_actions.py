import ctypes
import subprocess


class SystemActions:

    @staticmethod
    def open_task_manager() -> None:
        try:
            subprocess.Popen("taskmgr.exe")
        except OSError as e:
            print(f"[SystemActions] Task Manager failed to open: {e}")

    @staticmethod
    def open_file_explorer() -> None:
        try:
            subprocess.Popen("explorer.exe")
        except OSError as e:
            print(f"[SystemActions] File Explorer failed to open: {e}")

    @staticmethod
    def launch_path(path: str) -> bool:
        """
        Generic launcher for any user-added program, shortcut, or file path.

        This replaces the old hardcoded per-app methods (VLC, Brave,
        RAMMap, VS Code, System Cleaner, etc.) so users aren't forced to
        edit the source code just to add a program that only exists on
        their own PC. Paths are added at runtime through the "Add App"
        button in the Quick Panel and stored in settings.json.
        """
        if not path:
            return False
        try:
            subprocess.Popen([path])
            return True
        except OSError as e:
            print(f"[SystemActions] Failed to launch '{path}': {e}")
            return False

    @staticmethod
    def open_windows_settings() -> None:
        try:
            subprocess.Popen(["start", "ms-settings:"], shell=True)
        except OSError as e:
            print(f"[SystemActions] Settings failed to open: {e}")

    @staticmethod
    def lock_pc() -> None:
        try:
            ctypes.windll.user32.LockWorkStation()
        except Exception as e:
            print(f"[SystemActions] Device lock failed: {e}")

    @staticmethod
    def restart(force: bool = False) -> None:
        args = ["shutdown", "/r", "/t", "0"]
        if force:
            args.append("/f")
        try:
            subprocess.run(args, check=False)
        except OSError as e:
            print(f"[SystemActions] Restart failed: {e}")

    @staticmethod
    def shutdown(force: bool = False) -> None:
        args = ["shutdown", "/s", "/t", "0"]
        if force:
            args.append("/f")
        try:
            subprocess.run(args, check=False)
        except OSError as e:
            print(f"[SystemActions] Shutdown failed: {e}")

    @staticmethod
    def sleep() -> None:
        try:
            ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
        except Exception as e:
            print(f"[SystemActions] Sleep mode activation failed: {e}")
