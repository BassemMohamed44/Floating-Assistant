import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import customtkinter as ctk

from config import tr
from utils.animations import WindowAnimator

from core.wifi import WifiController
from core.bluetooth import BluetoothController
from core.brightness import BrightnessController, NightLightController
from core.volume import VolumeController, MicrophoneController
from core.screenshot import ScreenshotController
from core.notifications import NotificationManager
from core.system_actions import SystemActions


# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
BG = "#0B0E1A"
CARD_BG = "#161C2C"
CARD_HOVER = "#1E2536"
BORDER = "#232B3E"

GREEN_ON_BG = "#15532D"
GREEN_BADGE = "#22C55E"
BLUE_ACCENT_BG = "#1E3A6B"
BLUE_BADGE = "#3B82F6"

TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#8B93A7"
TEXT_MUTED = "#5B6478"

TILE_ICON_COLORS = {
    "screenshot": "#1D4ED8",
    "task_manager": "#2563EB",
    "file_explorer": "#F59E0B",
    "settings": "#8B5CF6",
    "lock": "#16A34A",
    "restart": "#3B82F6",
    "shutdown": "#EF4444",
    "sleep": "#7C3AED",
    "app_default": "#F97316",
    "add_app": "#2563EB",
    "remove": "#EF4444",
}


class PopupMenu(ctk.CTkToplevel):

    def __init__(self, master, settings_storage):
        super().__init__(master)
        self.settings = settings_storage
        self.lang = self.settings.get("language", "ar")
        self._apps_edit_mode = False

        self.wifi = WifiController()
        self.bluetooth = BluetoothController()
        self.brightness = BrightnessController()
        self.night_light = NightLightController()
        self.volume = VolumeController()
        self.mic = MicrophoneController()
        self.screenshot = ScreenshotController(self.settings.get("screenshot_save_path"))
        self.notifier = NotificationManager()

        self._toggle_cards = {}

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0)
        self.withdraw()
        self.configure(fg_color=BG)

        self._animator = WindowAnimator(self, duration=self.settings.get("animation_speed", 0.15))
        self._is_open = False

        self._build_ui()
        self.bind("<FocusOut>", lambda e: self.hide())

    # -------------------------------------------------------------------
    # GUI
    # -------------------------------------------------------------------
    def _build_ui(self) -> None:
        container = ctk.CTkFrame(self, corner_radius=20, fg_color=BG, border_width=1, border_color=BORDER)
        container.pack(padx=4, pady=4, fill="both", expand=True)

        self._build_header(container)
        self._build_toggle_row(container)
        self._build_sliders_row(container)
        self._build_actions_grid(container)

        self._refresh_states_async()

    # -------------------------------------------------------------------
    # Header: title + edit (pencil) + settings (gear)
    # -------------------------------------------------------------------
    def _build_header(self, container) -> None:
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16, 10))

        ctk.CTkLabel(
            header, text="Quick Panel", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_PRIMARY
        ).pack(side="left")

        gear_btn = ctk.CTkLabel(
            header, text="⚙", width=34, height=34, corner_radius=17, fg_color=CARD_BG,
            text_color=TEXT_PRIMARY, font=ctk.CTkFont(size=15)
        )
        gear_btn.pack(side="right", padx=(6, 0))
        gear_btn.bind("<Button-1>", lambda e: self._open_settings_placeholder())

        edit_bg = BLUE_ACCENT_BG if self._apps_edit_mode else CARD_BG
        pencil_btn = ctk.CTkLabel(
            header, text="✎", width=34, height=34, corner_radius=17, fg_color=edit_bg,
            text_color=TEXT_PRIMARY, font=ctk.CTkFont(size=14)
        )
        pencil_btn.pack(side="right", padx=(6, 0))
        pencil_btn.bind("<Button-1>", lambda e: self._toggle_edit_mode())

    # -------------------------------------------------------------------
    # Toggle cards: Wi-Fi / Bluetooth / Microphone / Night light
    # -------------------------------------------------------------------
    def _build_toggle_row(self, container) -> None:
        row = ctk.CTkFrame(container, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(0, 10))
        for col in range(4):
            row.grid_columnconfigure(col, weight=1)

        self._toggle_cards["wifi"] = self._build_toggle_card(
            row, "📶", tr("Wi-Fi", self.lang), self._toggle_wifi, 0
        )
        self._toggle_cards["bluetooth"] = self._build_toggle_card(
            row, "🔵", tr("Bluetooth", self.lang), self._toggle_bluetooth, 1
        )
        self._toggle_cards["mic"] = self._build_toggle_card(
            row, "🎤", tr("Microphone", self.lang), self._toggle_mic, 2
        )
        self._toggle_cards["night_light"] = self._build_toggle_card(
            row, "🌙", tr("Night light", self.lang), self._toggle_night_light, 3, static=True
        )

    def _build_toggle_card(self, parent, icon, label, command, col, static=False):
        card = ctk.CTkFrame(parent, corner_radius=16, fg_color=CARD_BG)
        card.grid(row=0, column=col, padx=4, pady=4, sticky="nsew")

        badge = ctk.CTkLabel(
            card, text="✓", width=20, height=20, corner_radius=10,
            fg_color=GREEN_BADGE, text_color="white", font=ctk.CTkFont(size=10, weight="bold")
        )
        # placed on demand via _apply_toggle_card_state

        icon_lbl = ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=26))
        icon_lbl.pack(pady=(18, 6))

        title_lbl = ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_PRIMARY)
        title_lbl.pack()

        status_lbl = ctk.CTkLabel(card, text="—", font=ctk.CTkFont(size=11), text_color=TEXT_SECONDARY)
        status_lbl.pack(pady=(2, 16))

        for widget in (card, icon_lbl, title_lbl, status_lbl):
            widget.bind("<Button-1>", lambda e: command())

        if static:
            status_lbl.configure(text=tr("settings", self.lang))

        return {"card": card, "badge": badge, "status": status_lbl}

    def _apply_toggle_card_state(self, key: str, is_on: bool, on_text: str, off_text: str) -> None:
        refs = self._toggle_cards.get(key)
        if not refs:
            return
        refs["card"].configure(fg_color=GREEN_ON_BG if is_on else CARD_BG)
        refs["status"].configure(text=on_text if is_on else off_text, text_color=GREEN_BADGE if is_on else TEXT_SECONDARY)
        if is_on:
            refs["badge"].place(relx=1.0, rely=0.0, x=-10, y=10, anchor="ne")
        else:
            refs["badge"].place_forget()

    # -------------------------------------------------------------------
    # Sliders: Volume / Brightness
    # -------------------------------------------------------------------
    def _build_sliders_row(self, container) -> None:
        row = ctk.CTkFrame(container, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(0, 10))
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1)

        volume_card = ctk.CTkFrame(row, corner_radius=14, fg_color=CARD_BG)
        volume_card.grid(row=0, column=0, padx=4, pady=4, sticky="nsew")
        vol_header = ctk.CTkFrame(volume_card, fg_color="transparent")
        vol_header.pack(fill="x", padx=14, pady=(12, 0))
        ctk.CTkLabel(vol_header, text=f"🔊  {tr('volume', self.lang)}", text_color=TEXT_PRIMARY).pack(side="left")
        current_vol = self.volume.get_volume()
        self.volume_pct_label = ctk.CTkLabel(
            vol_header, text=f"{current_vol if current_vol is not None else 50}%", text_color=BLUE_BADGE, font=ctk.CTkFont(weight="bold")
        )
        self.volume_pct_label.pack(side="right")
        self.volume_slider = ctk.CTkSlider(
            volume_card, from_=0, to=100, command=self._on_volume_change,
            progress_color=BLUE_BADGE, button_color="#FFFFFF"
        )
        self.volume_slider.pack(fill="x", padx=14, pady=(6, 14))
        self.volume_slider.set(current_vol if current_vol is not None else 50)

        brightness_card = ctk.CTkFrame(row, corner_radius=14, fg_color=CARD_BG)
        brightness_card.grid(row=0, column=1, padx=4, pady=4, sticky="nsew")
        bri_header = ctk.CTkFrame(brightness_card, fg_color="transparent")
        bri_header.pack(fill="x", padx=14, pady=(12, 0))
        ctk.CTkLabel(bri_header, text=f"☀️  {tr('brightness', self.lang)}", text_color=TEXT_PRIMARY).pack(side="left")
        current_brightness = self.brightness.get_brightness()
        self.brightness_pct_label = ctk.CTkLabel(
            bri_header, text=f"{current_brightness if current_brightness is not None else 50}%",
            text_color="#E5E7EB", font=ctk.CTkFont(weight="bold")
        )
        self.brightness_pct_label.pack(side="right")
        self.brightness_slider = ctk.CTkSlider(
            brightness_card, from_=0, to=100, command=self._on_brightness_change,
            progress_color="#E5E7EB", button_color="#FFFFFF"
        )
        self.brightness_slider.pack(fill="x", padx=14, pady=(6, 14))
        self.brightness_slider.set(current_brightness if current_brightness is not None else 50)

    # -------------------------------------------------------------------
    # Action tiles grid (Screenshot, Task manager, ... + custom apps)
    # -------------------------------------------------------------------
    def _build_actions_grid(self, container) -> None:
        grid = ctk.CTkFrame(container, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=12, pady=(0, 14))
        for col in range(4):
            grid.grid_columnconfigure(col, weight=1)

        self._grid_row = 0
        self._grid_col = 0

        self._add_tile(grid, "📷", TILE_ICON_COLORS["screenshot"], tr("Screenshot", self.lang), self._take_screenshot)
        self._add_tile(grid, "🖥", TILE_ICON_COLORS["task_manager"], tr("Task manager", self.lang), SystemActions.open_task_manager)
        self._add_tile(grid, "📁", TILE_ICON_COLORS["file_explorer"], tr("File explorer", self.lang), SystemActions.open_file_explorer)
        self._add_tile(grid, "⚙", TILE_ICON_COLORS["settings"], tr("Settings", self.lang), self._open_settings_placeholder)

        self._add_tile(grid, "🔒", TILE_ICON_COLORS["lock"], tr("Lock PC", self.lang), SystemActions.lock_pc)
        self._add_tile(grid, "🔄", TILE_ICON_COLORS["restart"], tr("Restart", self.lang), lambda: self._confirm_action("restart"))
        self._add_tile(grid, "⏻", TILE_ICON_COLORS["shutdown"], tr("Shutdown", self.lang), lambda: self._confirm_action("shutdown"))
        self._add_tile(grid, "🛌", TILE_ICON_COLORS["sleep"], tr("Sleep", self.lang), SystemActions.sleep)

        self._build_custom_apps_section(grid)

    def _add_tile(self, grid, icon, icon_bg, label, command, danger=False):
        row, col = self._grid_row, self._grid_col

        tile = ctk.CTkFrame(grid, corner_radius=14, fg_color=CARD_BG)
        tile.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

        icon_badge = ctk.CTkLabel(
            tile, text=icon, width=34, height=34, corner_radius=10,
            fg_color=icon_bg, font=ctk.CTkFont(size=15)
        )
        icon_badge.pack(side="left", padx=(10, 10), pady=10)

        text_color = "#FCA5A5" if danger else TEXT_PRIMARY
        text_lbl = ctk.CTkLabel(tile, text=label, anchor="w", text_color=text_color, font=ctk.CTkFont(size=13, weight="bold"))
        text_lbl.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=10)

        for widget in (tile, icon_badge, text_lbl):
            widget.bind("<Button-1>", lambda e: command())

        self._grid_col += 1
        if self._grid_col > 3:
            self._grid_col = 0
            self._grid_row += 1

        return tile

    # -------------------------------------------------------------------
    # Custom user-added apps (no code changes needed to add a program)
    # -------------------------------------------------------------------
    def _build_custom_apps_section(self, grid) -> None:
        apps = self.settings.get("custom_apps", [])

        for app in apps:
            if self._apps_edit_mode:
                tile = self._add_tile(
                    grid, app.get("icon", "📦"), TILE_ICON_COLORS["app_default"],
                    app.get("name", "App"), lambda a=app: self._confirm_remove_app(a), danger=False
                )
                remove_badge = ctk.CTkLabel(
                    tile, text="✕", width=18, height=18, corner_radius=9,
                    fg_color=TILE_ICON_COLORS["remove"], text_color="white", font=ctk.CTkFont(size=9, weight="bold")
                )
                remove_badge.place(relx=1.0, rely=0.0, x=-6, y=6, anchor="ne")
                remove_badge.bind("<Button-1>", lambda e, a=app: self._confirm_remove_app(a))
            else:
                tile = self._add_tile(
                    grid, app.get("icon", "📦"), TILE_ICON_COLORS["app_default"],
                    app.get("name", "App"), lambda a=app: self._launch_custom_app(a)
                )
                # Right-click also removes, as a quick shortcut for power users
                tile.bind("<Button-3>", lambda e, a=app: self._confirm_remove_app(a))

        self._add_tile(grid, "➕", TILE_ICON_COLORS["add_app"], tr("add_app", self.lang), self._add_custom_app)

    def _launch_custom_app(self, app: dict) -> None:
        def task():
            success = SystemActions.launch_path(app.get("path", ""))
            if not success:
                self.after(0, lambda: self.notifier.notify(
                    app.get("name", ""), tr("app_launch_failed", self.lang)
                ))
        threading.Thread(target=task, daemon=True).start()

    def _add_custom_app(self) -> None:
        path = filedialog.askopenfilename(
            title=tr("add_app", self.lang),
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
        )
        if not path:
            return

        default_name = os.path.splitext(os.path.basename(path))[0]
        name = simpledialog.askstring(
            tr("add_app", self.lang), tr("app_name_prompt", self.lang),
            initialvalue=default_name, parent=self,
        )
        if not name:
            name = default_name

        apps = self.settings.get("custom_apps", [])
        apps.append({"name": name, "path": path, "icon": "🚀"})
        self.settings.set("custom_apps", apps)
        self._rebuild()

    def _confirm_remove_app(self, app: dict) -> None:
        confirmed = messagebox.askyesno(
            tr("remove_app", self.lang),
            f"{tr('remove_app_confirm', self.lang)} {app.get('name', '')}?"
        )
        if not confirmed:
            return
        apps = self.settings.get("custom_apps", [])
        apps = [a for a in apps if not (a.get("path") == app.get("path") and a.get("name") == app.get("name"))]
        self.settings.set("custom_apps", apps)
        self._rebuild()

    def _toggle_edit_mode(self) -> None:
        self._apps_edit_mode = not self._apps_edit_mode
        self._rebuild()

    # -------------------------------------------------------------------
    # Button toggle logic - operates in separate threads to prevent freezing
    # -------------------------------------------------------------------
    def _toggle_wifi(self) -> None:
        def task():
            new_state = self.wifi.toggle()
            msg_key = "wifi_enabled" if new_state else "wifi_disabled"
            self.notifier.notify(tr("wifi", self.lang), tr(msg_key, self.lang))
            self.after(0, self._refresh_wifi_state)
        threading.Thread(target=task, daemon=True).start()

    def _toggle_bluetooth(self) -> None:
        def task():
            new_state = self.bluetooth.toggle()
            if new_state is not None:
                msg_key = "bluetooth_enabled" if new_state else "bluetooth_disabled"
                self.notifier.notify(tr("bluetooth", self.lang), tr(msg_key, self.lang))
            self.after(0, self._refresh_bluetooth_state)
        threading.Thread(target=task, daemon=True).start()

    def _toggle_mic(self) -> None:
        def task():
            new_state = self.mic.toggle_mute()
            if new_state is not None:
                msg_key = "mic_muted" if new_state else "mic_unmuted"
                self.notifier.notify(tr("microphone", self.lang), tr(msg_key, self.lang))
            self.after(0, self._refresh_mic_state)
        threading.Thread(target=task, daemon=True).start()

    def _toggle_night_light(self) -> None:
        self.night_light.open_night_light_settings()

    def _on_volume_change(self, value) -> None:
        self.volume.set_volume(int(value))
        if hasattr(self, "volume_pct_label"):
            self.volume_pct_label.configure(text=f"{int(value)}%")

    def _on_brightness_change(self, value) -> None:
        self.brightness.set_brightness(int(value))
        if hasattr(self, "brightness_pct_label"):
            self.brightness_pct_label.configure(text=f"{int(value)}%")

    def _take_screenshot(self) -> None:
        def task():
            path = self.screenshot.capture()
            if path:
                self.notifier.notify(tr("screenshot", self.lang), tr("screenshot_saved", self.lang))
        threading.Thread(target=task, daemon=True).start()

    def _open_settings_placeholder(self) -> None:
        if hasattr(self, "on_open_settings") and self.on_open_settings:
            self.on_open_settings()
        self.hide()

    # -------------------------------------------------------------------
    # Update current statuses when the menu is opened
    # -------------------------------------------------------------------
    def _refresh_states_async(self) -> None:
        threading.Thread(target=self._refresh_wifi_state, daemon=True).start()
        threading.Thread(target=self._refresh_bluetooth_state, daemon=True).start()
        threading.Thread(target=self._refresh_mic_state, daemon=True).start()

    def _refresh_wifi_state(self) -> None:
        try:
            enabled = self.wifi.is_enabled()
            self.after(0, lambda: self._apply_toggle_card_state(
                "wifi", bool(enabled), tr("wifi_enabled", self.lang), tr("wifi_disabled", self.lang)
            ))
        except Exception:
            pass

    def _refresh_bluetooth_state(self) -> None:
        try:
            enabled = self.bluetooth.is_enabled()
            self.after(0, lambda: self._apply_toggle_card_state(
                "bluetooth", bool(enabled), tr("bluetooth_enabled", self.lang), tr("bluetooth_disabled", self.lang)
            ))
        except Exception:
            pass

    def _refresh_mic_state(self) -> None:
        try:
            muted = self.mic.is_muted()
            self.after(0, lambda: self._apply_toggle_card_state(
                "mic", not bool(muted), tr("mic_unmuted", self.lang), tr("mic_muted", self.lang)
            ))
        except Exception:
            pass

    # -------------------------------------------------------------------
    # Confirmation windows for sensitive procedures
    # -------------------------------------------------------------------
    def _confirm_action(self, action_type: str) -> None:
        confirm_win = ctk.CTkToplevel(self)
        confirm_win.title("")
        confirm_win.overrideredirect(True)
        confirm_win.attributes("-topmost", True)
        confirm_win.geometry("320x140+{}+{}".format(
            self.winfo_x() + 20, self.winfo_y() + 40
        ))

        frame = ctk.CTkFrame(confirm_win, corner_radius=16, fg_color=CARD_BG)
        frame.pack(fill="both", expand=True, padx=6, pady=6)

        message_key = {
            "shutdown": "confirm_shutdown",
            "restart": "confirm_restart",
            "sign_out": "confirm_signout",
        }[action_type]

        ctk.CTkLabel(
            frame, text=tr(message_key, self.lang), wraplength=280,
            font=ctk.CTkFont(size=14), text_color=TEXT_PRIMARY
        ).pack(pady=(16, 12), padx=12)

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=4)

        def execute_and_close():
            confirm_win.destroy()
            if action_type == "shutdown":
                SystemActions.shutdown()
            elif action_type == "restart":
                SystemActions.restart()
            elif action_type == "sign_out":
                SystemActions.sign_out()

        ctk.CTkButton(
            btn_frame, text=tr("yes", self.lang), width=100,
            fg_color="#D9534F", hover_color="#C9302C", command=execute_and_close
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_frame, text=tr("no", self.lang), width=100,
            fg_color="#4A4A4A", hover_color="#5A5A5A", command=confirm_win.destroy
        ).pack(side="left", padx=8)

    # -------------------------------------------------------------------
    # Controlling appearance and hiding with animation
    # -------------------------------------------------------------------
    def show_at(self, x: int, y: int, anchor_size: int) -> None:
        self.update_idletasks()
        menu_width = self.winfo_reqwidth() or 480
        menu_height = self.winfo_reqheight() or 480

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        pos_x = x + anchor_size + 10
        if pos_x + menu_width > screen_w:
            pos_x = x - menu_width - 10

        pos_y = y
        if pos_y + menu_height > screen_h:
            pos_y = screen_h - menu_height - 10
        pos_y = max(10, pos_y)

        self.geometry(f"{menu_width}x{menu_height}+{int(pos_x)}+{int(pos_y)}")
        self._is_open = True
        self._animator.fade_in()
        self.focus_force()
        self._refresh_states_async()

    def hide(self) -> None:
        if not self._is_open:
            return
        self._is_open = False
        self._animator.fade_out()

    def toggle_at(self, x: int, y: int, anchor_size: int) -> None:
        if self._is_open:
            self.hide()
        else:
            self.show_at(x, y, anchor_size)

    def _rebuild(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()
        self._toggle_cards = {}
        self._build_ui()

    def refresh_language(self) -> None:
        self.lang = self.settings.get("language", "ar")
        self._rebuild()
