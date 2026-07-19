from tkinter import colorchooser, filedialog, messagebox
import customtkinter as ctk

from config import tr, DEFAULT_SETTINGS
from utils.startup import StartupManager


class SettingsWindow(ctk.CTkToplevel):

    def __init__(self, master, settings_storage, on_settings_applied):
        super().__init__(master)
        self.settings = settings_storage
        self.on_settings_applied = on_settings_applied
        self.lang = self.settings.get("language", "ar")
        self.startup_manager = StartupManager()

        self.title(tr("settings_title", self.lang))
        self.geometry("480x640")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        self._selected_color = self.settings.get("button_color", "#3B8ED0")
        self.custom_apps = list(self.settings.get("custom_apps", []))

        self._build_ui()

    # -------------------------------------------------------------------
    def _build_ui(self) -> None:
        scroll_frame = ctk.CTkScrollableFrame(self, width=440, height=560)
        scroll_frame.pack(padx=12, pady=12, fill="both", expand=True)

        ctk.CTkLabel(scroll_frame, text=tr("button_size", self.lang), font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", pady=(6, 2)
        )
        self.size_slider = ctk.CTkSlider(scroll_frame, from_=40, to=120, number_of_steps=80)
        self.size_slider.set(self.settings.get("button_size", 60))
        self.size_slider.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(scroll_frame, text=tr("button_color", self.lang), font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", pady=(6, 2)
        )
        color_row = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        color_row.pack(fill="x", pady=(0, 12))
        self.color_preview = ctk.CTkLabel(
            color_row, text="", width=40, height=24, fg_color=self._selected_color, corner_radius=6
        )
        self.color_preview.pack(side="left", padx=(0, 10))
        ctk.CTkButton(color_row, text="🎨", width=50, command=self._choose_color).pack(side="left")

        ctk.CTkLabel(scroll_frame, text=tr("button_opacity", self.lang), font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", pady=(6, 2)
        )
        self.opacity_slider = ctk.CTkSlider(scroll_frame, from_=0.2, to=1.0, number_of_steps=80)
        self.opacity_slider.set(self.settings.get("button_opacity", 0.9))
        self.opacity_slider.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(scroll_frame, text=tr("animation_speed", self.lang), font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", pady=(6, 2)
        )
        self.animation_slider = ctk.CTkSlider(scroll_frame, from_=0.05, to=0.6, number_of_steps=55)
        self.animation_slider.set(self.settings.get("animation_speed", 0.15))
        self.animation_slider.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(scroll_frame, text=tr("language", self.lang), font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", pady=(6, 2)
        )
        self.language_menu = ctk.CTkOptionMenu(scroll_frame, values=["ar", "en"])
        self.language_menu.set(self.settings.get("language", "ar"))
        self.language_menu.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(scroll_frame, text="Theme", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(6, 2))
        self.theme_menu = ctk.CTkOptionMenu(scroll_frame, values=["dark", "light"], command=self._on_theme_preview)
        self.theme_menu.set(self.settings.get("theme", "dark"))
        self.theme_menu.pack(fill="x", pady=(0, 12))

        self.startup_switch = ctk.CTkSwitch(scroll_frame, text=tr("run_on_startup", self.lang))
        if self.settings.get("run_on_startup", False):
            self.startup_switch.select()
        self.startup_switch.pack(anchor="w", pady=(6, 16))

        ctk.CTkLabel(scroll_frame, text=tr("manage_apps", self.lang), font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", pady=(6, 2)
        )
        self.apps_list_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        self.apps_list_frame.pack(fill="x", pady=(0, 16))
        self._render_apps_list()

        action_row = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        action_row.pack(fill="x", pady=(0, 12))
        ctk.CTkButton(action_row, text=tr("save", self.lang), command=self._save_settings).pack(
            side="left", expand=True, fill="x", padx=(0, 6)
        )
        ctk.CTkButton(
            action_row, text=tr("cancel", self.lang), fg_color="#4A4A4A", hover_color="#5A5A5A",
            command=self.destroy
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

        ctk.CTkButton(
            scroll_frame, text=tr("reset_settings", self.lang), fg_color="#D9534F", hover_color="#C9302C",
            command=self._reset_settings
        ).pack(fill="x", pady=(6, 6))

        io_row = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        io_row.pack(fill="x", pady=(0, 6))
        ctk.CTkButton(io_row, text=tr("export_settings", self.lang), command=self._export_settings).pack(
            side="left", expand=True, fill="x", padx=(0, 6)
        )
        ctk.CTkButton(io_row, text=tr("import_settings", self.lang), command=self._import_settings).pack(
            side="left", expand=True, fill="x", padx=(6, 0)
        )

    # -------------------------------------------------------------------
    def _choose_color(self) -> None:
        color_code = colorchooser.askcolor(title=tr("button_color", self.lang), initialcolor=self._selected_color)
        if color_code and color_code[1]:
            self._selected_color = color_code[1]
            self.color_preview.configure(fg_color=self._selected_color)

    def _on_theme_preview(self, value: str) -> None:
        ctk.set_appearance_mode(value)

    def _render_apps_list(self) -> None:
        for widget in self.apps_list_frame.winfo_children():
            widget.destroy()

        if not self.custom_apps:
            ctk.CTkLabel(
                self.apps_list_frame, text=tr("no_apps_added", self.lang),
                text_color="#888888", font=ctk.CTkFont(size=12)
            ).pack(anchor="w", pady=(0, 4))
            return

        for app in self.custom_apps:
            row = ctk.CTkFrame(self.apps_list_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(
                row, text=f"{app.get('icon', '📦')}  {app.get('name', 'App')}", anchor="w"
            ).pack(side="left", fill="x", expand=True)
            ctk.CTkButton(
                row, text="🗑", width=32, height=28,
                fg_color="#D9534F", hover_color="#C9302C",
                command=lambda a=app: self._remove_app(a)
            ).pack(side="right")

    def _remove_app(self, app: dict) -> None:
        confirmed = messagebox.askyesno(
            tr("remove_app", self.lang),
            f"{tr('remove_app_confirm', self.lang)} {app.get('name', '')}?"
        )
        if not confirmed:
            return

        self.custom_apps = [
            a for a in self.custom_apps
            if not (a.get("path") == app.get("path") and a.get("name") == app.get("name"))
        ]
        self.settings.set("custom_apps", self.custom_apps)
        self._render_apps_list()

        if self.on_settings_applied:
            self.on_settings_applied()

    def _save_settings(self) -> None:
        new_values = {
            "button_size": int(self.size_slider.get()),
            "button_color": self._selected_color,
            "button_opacity": round(self.opacity_slider.get(), 2),
            "animation_speed": round(self.animation_slider.get(), 2),
            "language": self.language_menu.get(),
            "theme": self.theme_menu.get(),
            "run_on_startup": bool(self.startup_switch.get()),
        }
        self.settings.update_many(new_values)

        self.startup_manager.set_enabled(new_values["run_on_startup"])

        if self.on_settings_applied:
            self.on_settings_applied()

        self.destroy()

    def _reset_settings(self) -> None:
        confirmed = messagebox.askyesno(
            tr("reset_settings", self.lang),
            tr("reset_settings", self.lang) + "?"
        )
        if confirmed:
            self.settings.reset_to_default()
            self.startup_manager.set_enabled(DEFAULT_SETTINGS["run_on_startup"])
            if self.on_settings_applied:
                self.on_settings_applied()
            self.destroy()

    def _export_settings(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title=tr("export_settings", self.lang),
        )
        if path:
            success = self.settings.export_to(path)
            if success:
                messagebox.showinfo(tr("export_settings", self.lang), "OK")
            else:
                messagebox.showerror(tr("export_settings", self.lang), "Failed")

    def _import_settings(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")],
            title=tr("import_settings", self.lang),
        )
        if path:
            success = self.settings.import_from(path)
            if success:
                if self.on_settings_applied:
                    self.on_settings_applied()
                messagebox.showinfo(tr("import_settings", self.lang), "OK")
                self.destroy()
            else:
                messagebox.showerror(tr("import_settings", self.lang), "Failed")
