# Venom Floating Assistant

A Windows desktop utility that shows a floating, draggable circular button (similar to iOS AssistiveTouch) that always stays on top of every window. Tap it to open a **Quick Panel** with fast controls for Wi-Fi, Bluetooth, volume, brightness, microphone, screenshots, and common system actions — plus your own custom app shortcuts.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-informational)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

---

## Features

- **Floating button** that remembers its position, size, color, and opacity (`data/settings.json`).
- **Quick Panel** with:
  - Wi-Fi / Bluetooth / Microphone toggles (live status, instant feedback).
  - Night Light shortcut.
  - Volume & Brightness sliders with live percentage.
  - Screenshot, Task Manager, File Explorer, Settings.
  - Lock PC, Restart, Shutdown, Sleep (with confirmation for destructive actions).
  - **Custom Apps**: add any program on your PC as a quick-launch tile — no code editing required. Tap ➕ to add, tap ✎ (edit mode) then ✕ to remove, or right-click a tile to remove it directly.
- **Settings window**: button size/color/opacity, animation speed, language (Arabic/English), dark/light theme, run on Windows startup, manage/remove custom apps, reset to defaults.
- **Global hotkeys**:
  - `Ctrl+Alt+W` → toggle the Quick Panel.
  - `Ctrl+Alt+S` → instant screenshot.
- **Windows toast notifications** for every action (Wi-Fi on/off, screenshot saved, etc.).
- All slow operations (radio state, PowerShell/WinRT calls, launching apps) run on background threads so the UI never freezes.

## Requirements

- **Windows 10 or 11** (this project relies on Windows-only APIs: WinRT Radios, `pycaw`, `pywin32`).
- **Python 3.10+**

```bash
pip install -r requirements.txt
```

> `pycaw`, `comtypes`, `pywin32`, `win10toast`, `keyboard`, and the `winrt-*` packages only work on Windows and will not install/run on macOS or Linux.

## Run

```bash
python venom_floating.py
```

On first launch a blue circular button appears near the top of the screen. Drag it anywhere; a plain click (no drag) opens the Quick Panel.

## Project Structure

```
 Venom Floating Assistant/
├── venom_floating.py                   # Entry point
├── config.py                  # Default settings + translations (ar/en)
├── requirements.txt
├── assets/                    # Icons / images
├── ui/
│   ├── floating_button.py     # The draggable floating button
│   ├── popup_menu.py          # Quick Panel (toggles, sliders, action tiles, custom apps)
│   └── settings_window.py     # Settings window
├── core/
│   ├── wifi.py                 # Wi-Fi radio control (WinRT Radios API)
│   ├── bluetooth.py            # Bluetooth radio control (WinRT Radios API)
│   ├── brightness.py           # BrightnessController + NightLightController
│   ├── volume.py                # VolumeController + MicrophoneController (pycaw)
│   ├── screenshot.py
│   ├── notifications.py
│   ├── system_actions.py       # Lock / Restart / Shutdown / Sleep / generic app launcher
│   └── shortcuts.py            # Global hotkeys (ShortcutManager)
├── utils/
│   ├── storage.py               # Load/save settings.json
│   ├── animations.py            # Fade in/out animations
│   └── startup.py               # Run on Windows startup (registry)
└── data/
    └── settings.json            # Local, user-specific — not tracked in git
```

## How Wi-Fi / Bluetooth control works

Older versions of this project disabled the network adapter / Bluetooth device entirely (`netsh admin=disable`, `Disable-PnpDevice`), which also removed the icon from the taskbar. The current implementation uses the **Windows Radio Management API** (`Windows.Devices.Radios`) via the in-process `winrt` Python bindings — the same API Action Center's own toggle uses. This only turns the radio on/off, so the device (and its taskbar icon) always stays present, and toggling is fast since no external process is spawned per click.

## Adding your own apps

The Quick Panel no longer hardcodes any personal file paths. Use the **➕ Add App** tile to browse for an `.exe`, give it a name, and it's saved to `data/settings.json` under `custom_apps`. Remove an app via edit mode (✎ → ✕), right-click on the tile, or the "Manage Added Apps" section in Settings.

## Building a distributable `.exe`

```bash
pyinstaller --noconsole --onefile --add-data "assets;assets" main.py
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and please follow the [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Security

See [SECURITY.md](SECURITY.md) for how to report a vulnerability.

## License

Licensed under the [MIT License](LICENSE).
