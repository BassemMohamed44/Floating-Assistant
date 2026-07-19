<div align="center">
  <img width="260" height="260" src="https://github.com/BassemMohamed44/assets/venom.png" alt="Venom Floating Assistant Icon"/>
  <h1 align="center">Venom Floating Assistant  𝐕🕷️🕸️</h1>
  <p align="center">A Windows desktop utility that shows a floating</p>
</div>

<div align="center">
  <img src="https://img.shields.io/static/v1?label=Issues&message=0open&color=4C0099" alt="issues"/>
  <img src="https://img.shields.io/static/v1?label=License&message=MIT&color=4C0099" alt="license"/>
  <img src="https://img.shields.io/static/v1?label=Security&message=Learning_Resources&color=4C0099" alt="security"/>
  <br>
  <img src="https://img.shields.io/static/v1?label=Python&message=Projects&color=4C0099" alt="projects"/>
  <img src="https://img.shields.io/static/v1?label=Venom&message=Floating-Assistant&color=4C0099" alt="projects"/>
</div>
<br>
<div align="center">
  
  [![Instagram](https://img.shields.io/badge/Instagram-%23E4405F.svg?style=for-the-badge&logo=Instagram&logoColor=white)](https://instagram.com/@bassemmohamed_0)
  [![Reddit](https://img.shields.io/badge/Reddit-%23FF4500.svg?style=for-the-badge&logo=Reddit&logoColor=white)](https://reddit.com/user/00xBassem)
  [![X](https://img.shields.io/badge/X-black.svg?style=for-the-badge&logo=X&logoColor=white)](https://x.com/@Basem2Mohamed)
  
</div>

<p align="center">Made possible by <a href="https://bassemmohamed.pages.dev/"><strong>BassemMohamed</strong></a></p>




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
