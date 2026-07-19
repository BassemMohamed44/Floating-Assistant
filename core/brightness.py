from typing import Optional

try:
    import screen_brightness_control as sbc
    SBC_AVAILABLE = True
except ImportError:
    SBC_AVAILABLE = False


class BrightnessController:

    def get_brightness(self) -> Optional[int]:
        if not SBC_AVAILABLE:
            return None
        try:
            values = sbc.get_brightness()
            if values:
                return int(values[0])
        except Exception as e:
            print(f"[BrightnessController] Brightness could not be read: {e}")
        return None

    def set_brightness(self, value: int) -> bool:
        if not SBC_AVAILABLE:
            return False
        clamped_value = max(0, min(100, value))
        try:
            sbc.set_brightness(clamped_value)
            return True
        except Exception as e:
            print(f"[BrightnessController] Brightness could not be adjusted: {e}")
            return False

    def is_supported(self) -> bool:
        return SBC_AVAILABLE and self.get_brightness() is not None


class NightLightController:

    @staticmethod
    def open_night_light_settings() -> None:
        import subprocess
        try:
            subprocess.Popen(["start", "ms-settings:nightlight"], shell=True)
        except OSError as e:
            print(f"[NightLightController] Night light settings failed to open: {e}")
