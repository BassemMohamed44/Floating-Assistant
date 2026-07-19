import json
import os
import shutil
from typing import Any, Dict

from config import SETTINGS_FILE, DATA_DIR, DEFAULT_SETTINGS


class SettingsStorage:

    def __init__(self, settings_path: str = SETTINGS_FILE):
        self.settings_path = settings_path
        self._settings: Dict[str, Any] = {}
        self._ensure_data_dir()
        self.load()

    def _ensure_data_dir(self) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        if not os.path.exists(self.settings_path):
            self._settings = DEFAULT_SETTINGS.copy()
            self.save()
            return self._settings

        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            merged = DEFAULT_SETTINGS.copy()
            merged.update(loaded)
            self._settings = merged
        except (json.JSONDecodeError, OSError):
            self._settings = DEFAULT_SETTINGS.copy()
            self.save()

        return self._settings

    def save(self) -> None:
        self._ensure_data_dir()
        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, ensure_ascii=False, indent=4)
        except OSError as e:
            print(f"[SettingsStorage] Error while saving the settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def set(self, key: str, value: Any, autosave: bool = True) -> None:
        self._settings[key] = value
        if autosave:
            self.save()

    def get_all(self) -> Dict[str, Any]:
        return self._settings.copy()

    def update_many(self, values: Dict[str, Any], autosave: bool = True) -> None:
        self._settings.update(values)
        if autosave:
            self.save()

    def reset_to_default(self) -> None:
        self._settings = DEFAULT_SETTINGS.copy()
        self.save()

    def export_to(self, destination_path: str) -> bool:
        try:
            self.save()
            shutil.copyfile(self.settings_path, destination_path)
            return True
        except OSError as e:
            print(f"[SettingsStorage] Export fo setings failed: {e}")
            return False

    def import_from(self, source_path: str) -> bool:
        try:
            with open(source_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return False
            merged = DEFAULT_SETTINGS.copy()
            merged.update(data)
            self._settings = merged
            self.save()
            return True
        except (json.JSONDecodeError, OSError) as e:
            print(f"[SettingsStorage] Failed to import sttings: {e}")
            return False
