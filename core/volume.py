from typing import Optional

try:
    from pycaw.pycaw import AudioUtilities
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False


class VolumeController:

    def __init__(self):
        self._volume_interface = None
        if PYCAW_AVAILABLE:
            try:
                device = AudioUtilities.GetSpeakers()
                # الخاصية EndpointVolume تعطي واجهة IAudioEndpointVolume جاهزة مباشرة
                self._volume_interface = device.EndpointVolume
            except Exception as e:
                print(f"[VolumeController] Error: {e}")

    def is_available(self) -> bool:
        return PYCAW_AVAILABLE and self._volume_interface is not None

    def get_volume(self) -> Optional[int]:
        if not self.is_available():
            return None
        try:
            scalar = self._volume_interface.GetMasterVolumeLevelScalar()
            return int(round(scalar * 100))
        except Exception as e:
            print(f"[VolumeController] Error 2: {e}")
            return None

    def set_volume(self, value: int) -> bool:
        if not self.is_available():
            return False
        clamped = max(0, min(100, value))
        try:
            self._volume_interface.SetMasterVolumeLevelScalar(clamped / 100.0, None)
            return True
        except Exception as e:
            print(f"[VolumeController] Error 3: {e}")
            return False

    def is_muted(self) -> Optional[bool]:
        if not self.is_available():
            return None
        try:
            return bool(self._volume_interface.GetMute())
        except Exception as e:
            print(f"[VolumeController] Error 4: {e}")
            return None

    def set_mute(self, muted: bool) -> bool:
        if not self.is_available():
            return False
        try:
            self._volume_interface.SetMute(1 if muted else 0, None)
            return True
        except Exception as e:
            print(f"[VolumeController] Error 5: {e}")
            return False

    def toggle_mute(self) -> Optional[bool]:
        current = self.is_muted()
        if current is None:
            return None
        new_state = not current
        self.set_mute(new_state)
        return new_state


class MicrophoneController:

    def __init__(self):
        self._mic_interface = None
        if PYCAW_AVAILABLE:
            try:
                device = AudioUtilities.GetMicrophone()
                self._mic_interface = device.EndpointVolume
            except Exception as e:
                print(f"[MicrophoneController] Error Mic: {e}")

    def is_available(self) -> bool:
        return PYCAW_AVAILABLE and self._mic_interface is not None

    def is_muted(self) -> Optional[bool]:
        if not self.is_available():
            return None
        try:
            return bool(self._mic_interface.GetMute())
        except Exception as e:
            print(f"[MicrophoneController] Error 6: {e}")
            return None

    def set_mute(self, muted: bool) -> bool:
        if not self.is_available():
            return False
        try:
            self._mic_interface.SetMute(1 if muted else 0, None)
            return True
        except Exception as e:
            print(f"[MicrophoneController] Error 7: {e}")
            return False

    def toggle_mute(self) -> Optional[bool]:
        current = self.is_muted()
        if current is None:
            return None
        new_state = not current
        self.set_mute(new_state)
        return new_state
