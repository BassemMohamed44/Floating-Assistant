# Contributing to Floating Assistant

Thanks for your interest in contributing! This is a personal, actively-developed
project, so please open an issue to discuss larger changes before investing a
lot of time in a pull request.

## Ground rules

- Please read and follow the [Code of Conduct](CODE_OF_CONDUCT.md).
- This project is **Windows-only** (it depends on WinRT, `pycaw`, `pywin32`).
  You'll need Windows 10/11 to actually run and test it end-to-end.

## Getting set up

```bash
git clone https://github.com/<your-fork>/floating-assistant.git
cd "Floating Assistant"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Project layout & architecture

The project follows a light Clean Architecture split:

- **`core/`** — Pure logic and OS integration (Wi-Fi, Bluetooth, volume,
  brightness, screenshots, system actions, notifications, hotkeys). No UI
  code lives here. Each controller exposes a small, predictable public API
  (e.g. `is_enabled()`, `enable()`, `disable()`, `toggle()`) so the UI layer
  never needs to know *how* a feature is implemented.
- **`ui/`** — `customtkinter`-based UI (floating button, Quick Panel,
  Settings window). UI code calls into `core/` controllers and never talks to
  Windows APIs directly.
- **`utils/`** — Cross-cutting helpers: settings persistence (`storage.py`),
  animations, startup registration.
- **`config.py`** — Default settings and the `ar`/`en` translation tables.

When adding a feature, prefer this flow: implement the logic in `core/`,
expose a small interface, then wire it up in `ui/`.

## Coding style

- Python 3.10+, type hints on public methods where practical.
- Keep OS calls wrapped in `try/except` and fail gracefully (log with
  `print(f"[ComponentName] ...")`, don't crash the UI thread).
- Any operation that can block (subprocess, PowerShell/WinRT calls, file
  dialogs) should run on a background `threading.Thread`, then hop back to
  the UI thread via `self.after(0, ...)`.
- Don't hardcode personal file paths (e.g. a specific `C:\Users\<you>\...`
  program path). Use the **Custom Apps** mechanism (`settings["custom_apps"]`)
  or a config value instead, so the app stays usable for everyone.
- Add both `ar` and `en` entries in `config.py`'s `TRANSLATIONS` for any new
  user-facing string, and use `tr("your_key", self.lang)` rather than hardcoded text.

## Submitting changes

1. Fork the repo and create a branch: `git checkout -b feature/short-description`.
2. Make your changes, keeping commits focused and descriptive.
3. Make sure the app still launches (`python main.py`) and the feature you
   touched works as expected on Windows.
4. Run a quick syntax/compile check: `python -m py_compile <changed files>`.
5. Open a pull request describing **what** changed and **why**, and mention
   how you tested it.

## Reporting bugs

Please include:
- Windows version (10/11) and Python version.
- Steps to reproduce.
- What you expected vs. what happened.
- Relevant console output/error traceback if the app printed one.

## Reporting security issues

Please **do not** open a public issue for security vulnerabilities — see
[SECURITY.md](SECURITY.md) for how to report them privately.
