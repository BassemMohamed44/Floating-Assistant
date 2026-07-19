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


class WifiController:

    def __init__(self):
        self._radio: Optional["Radio"] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._interface_name: Optional[str] = None

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
            if r.kind == RadioKind.WI_FI:
                self._radio = r
                return r
        return None

    # -------------------------------------------------------------------
    # Public API (unchanged signatures)
    # -------------------------------------------------------------------
    def is_enabled(self) -> bool:
        if _WINRT_AVAILABLE:
            try:
                async def _task():
                    radio = await self._get_radio()
                    if radio is None:
                        return None
                    return radio.state == RadioState.ON
                result = self._run(_task())
                if result is not None:
                    return result
            except Exception as e:
                print(f"[WifiController] Error checking state: {e}")
        return self._is_enabled_netsh_fallback()

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
            print(f"[WifiController] Error setting state: {e}")
            return False

    def enable(self) -> bool:
        if _WINRT_AVAILABLE:
            return self._set_state(RadioState.ON)
        return False

    def disable(self) -> bool:
        if _WINRT_AVAILABLE:
            return self._set_state(RadioState.OFF)
        return False

    def toggle(self) -> bool:
        if self.is_enabled():
            self.disable()
            return False
        else:
            self.enable()
            return True

    # -------------------------------------------------------------------
    # Fallback only used if no Wi-Fi radio is exposed via the Radio API
    # (very rare / older drivers). This keeps the adapter enabled in
    # Device Manager and only reports connectivity state via netsh.
    # -------------------------------------------------------------------
    def _run_netsh(self, args: list) -> str:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                startupinfo=startupinfo,
                timeout=10,
            )
            return result.stdout
        except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
            print(f"[WifiController] Error during command execution: {e}")
            return ""

    def _detect_interface_name(self) -> str:
        if self._interface_name:
            return self._interface_name

        output = self._run_netsh(["netsh", "interface", "show", "interface"])
        for line in output.splitlines():
            if "Wi-Fi" in line or "wireless" in line.lower():
                self._interface_name = "Wi-Fi"
                return self._interface_name

        self._interface_name = "Wi-Fi"
        return self._interface_name

    def _is_enabled_netsh_fallback(self) -> bool:
        interface = self._detect_interface_name()
        output = self._run_netsh(
            ["netsh", "interface", "show", "interface", f"name={interface}"]
        )
        return "Enabled" in output or "متصل" in output or "Connected" in output
