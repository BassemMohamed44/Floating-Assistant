# Floating Assistant

A Windows desktop program that displays a floating circular button (similar to AssistiveTouch) that always remains above all windows, is draggable, and opens a quick control menu for Wi-Fi, Bluetooth, sound, brightness, screenshots, and system actions.

## Screenshot

<img src="assets\Floating Assistant.png" alt="FA">

## Install

The program requires **Windows 10/11** و **Python 3.10+**.

```bash
pip install -r requirements.txt
```

> Note: Some libraries (`pycaw`, `comtypes`, `pywin32`, `win10toast`, `keyboard`)
> It only works on Windows and will not install or work on other systems.

## Run

```bash
python main.py
```

Upon first launch, a blue circular button will appear in the top corner of the screen. Drag it anywhere, and then press it once (without dragging) to bring up the quick control menu.

## Features

- A floating, retractable button that automatically saves its position in `data/settings.json`.
- Quick control menu: Wi-Fi، Bluetooth، Volume، Microphone، Brightness، Night Light،
  Screenshot، Task Manager، File Explorer، Settings، Lock، Sign Out، Restart،
  Shutdown، Sleep.
- Full settings window: Button size/color/transparency, animation speed, language (Arabic/English),
  Dark/Light mode, Start with Windows startup, Reset, Export/Import settings.
- General keyboard shortcuts:
  - `Ctrl+Alt+W` To open/close the menu.
  - `Ctrl+Alt+S` To capture an instant screenshot.
- Windows Toast notifications for every operation (Wi-Fi on/off, saving a screenshot, ...).
- All time-consuming operations (network scanning, PowerShell) run in separate threads to prevent the interface from freezing..

## Project Structure

```
project/
├── main.py                  # Main operating point
├── config.py                 # General settings and translations
├── requirements.txt
├── assets/                   # Icons and images (Optional: Place icon.ico here)
├── ui/
│   ├── floating_button.py    # Floating button
│   ├── popup_menu.py         # pop-up menu
│   └── settings_window.py    # Settings window
├── core/
│   ├── wifi.py
│   ├── bluetooth.py
│   ├── brightness.py         # It also includes NightLightController
│   ├── volume.py             # VolumeController + MicrophoneController
│   ├── screenshot.py
│   ├── notifications.py
│   ├── system_actions.py     # Lock / Sign Out / Restart / Shutdown / Sleep
│   └── shortcuts.py          # ShortcutManager (Global Hotkeys)
├── utils/
│   ├── storage.py            # Save/Load Settings JSON
│   ├── animations.py         # animation Fade in/out
│   └── startup.py            # Run with Windows startup via Registry
└── data/
    └── settings.json
```

## Technical Notes

- **Bluetooth**: Windows does not provide a direct, official API for full Bluetooth control from applications.
  Desktop: `Enable-PNPDevice` / `Disable-PNPDevice` via PowerShell is used as the best available solution; if sufficient powers are not available, the Bluetooth settings page will automatically open as an alternative plan.
- **Night Light**: There is no stable official API for programmatically activated across Windows versions, 
  so its settings page opens directly to ensure reliability.
- to activate **Start with Windows startup**،The program adds a value in
  `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`، This does not require administrator privileges.
- To create a file `.exe` Distributable, can be used `pyinstaller`:
  ```bash
  pyinstaller --noconsole --onefile --add-data "assets;assets" main.py
  ```
