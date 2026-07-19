import asyncio
import subprocess
from typing import Optional

try:
    from winrt.windows.devices.radios import (
        Radio,
        RadioKind,
        RadioState,
        RadioAccessStatus,
    )
    _WINRT_AVAILABLE = True
except ImportError:
    _WINRT_AVAILABLE = False


class BluetoothController:

    def __init__(self):
        self._radio: Optional["Radio"] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    # -------------------------------------------------------------------
    # Event loop / async helpers
    # -------------------------------------------------------------------
    def _get_loop(self) -> asyncio.AbstractEventLoop:
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
        return self._loop

    def _run(self, coro):
        return self._get_loop().run_until_complete(coro)

    async def _get_radio(self):
        if self._radio is not None:
            return self._radio
        access = await Radio.request_access_async()
        if access != RadioAccessStatus.ALLOWED:
            return None
        radios = await Radio.get_radios_async()
        for r in radios:
            if r.kind == RadioKind.BLUETOOTH:
                self._radio = r
                return r
        return None

    # -------------------------------------------------------------------
    # Public API (unchanged signatures)
    # -------------------------------------------------------------------
    def is_enabled(self) -> Optional[bool]:
        if not _WINRT_AVAILABLE:
            return None
        try:
            async def _task():
                radio = await self._get_radio()
                if radio is None:
                    return None
                return radio.state == RadioState.ON
            return self._run(_task())
        except Exception as e:
            print(f"[BluetoothController] Error checking state: {e}")
            return None

    def _set_state(self, state) -> bool:
        try:
            async def _task():
                radio = await self._get_radio()
                if radio is None:
                    return False
                await radio.set_state_async(state)
                return radio.state == state
            return self._run(_task())
        except Exception as e:
            print(f"[BluetoothController] Error setting state: {e}")
            return False

    def enable(self) -> bool:
        if _WINRT_AVAILABLE and self._set_state(RadioState.ON):
            return True
        self.open_bluetooth_settings()
        return False

    def disable(self) -> bool:
        if _WINRT_AVAILABLE and self._set_state(RadioState.OFF):
            return True
        self.open_bluetooth_settings()
        return False

    def toggle(self) -> Optional[bool]:
        current = self.is_enabled()
        if current is None:
            self.open_bluetooth_settings()
            return None
        if current:
            self.disable()
            return False
        else:
            self.enable()
            return True

    @staticmethod
    def open_bluetooth_settings() -> None:
        try:
            subprocess.Popen(["start", "ms-settings:bluetooth"], shell=True)
        except OSError as e:
            print(f"[BluetoothController] Bluetooth settings failed to open: {e}")
