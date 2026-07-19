import os
from datetime import datetime
from typing import Optional

from PIL import ImageGrab


class ScreenshotController:

    def __init__(self, save_directory: str):
        self.save_directory = save_directory

    def set_save_directory(self, path: str) -> None:
        self.save_directory = path

    def _generate_filename(self) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"Screenshot_{timestamp}.png"

    def capture(self) -> Optional[str]:

        try:
            os.makedirs(self.save_directory, exist_ok=True)
            filename = self._generate_filename()
            full_path = os.path.join(self.save_directory, filename)

            image = ImageGrab.grab()
            image.save(full_path, "PNG")
            return full_path
        except OSError as e:
            print(f"[ScreenshotController] Failed to capture or save image: {e}")
            return None
