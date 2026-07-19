import threading
from config import ASSETS_DIR
import os

try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False


class NotificationManager:

    def __init__(self, app_name: str = "Floating Assistant"):
        self.app_name = app_name
        self._toaster = ToastNotifier() if TOAST_AVAILABLE else None
        self._icon_path = os.path.join(ASSETS_DIR, "icon.ico")

    def notify(self, title: str, message: str, duration: int = 3) -> None:
    
        if not TOAST_AVAILABLE or self._toaster is None:
            print(f"[Notification] {title}: {message}")
            return

        icon = self._icon_path if os.path.exists(self._icon_path) else None

        def _show():
            try:
                self._toaster.show_toast(
                    title,
                    message,
                    icon_path=icon,
                    duration=duration,
                    threaded=True,
                )
            except Exception as e:
                print(f"[NotificationManager] Failed to display notification: {e}")

        thread = threading.Thread(target=_show, daemon=True)
        thread.start()
