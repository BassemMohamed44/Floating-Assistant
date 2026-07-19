import sys
import ctypes
import customtkinter as ctk
from PIL import Image, ImageTk

from config import DEFAULT_SETTINGS
from utils.storage import SettingsStorage
from ui.floating_button import FloatingButton
from ui.popup_menu import PopupMenu
from ui.settings_window import SettingsWindow
from core.shortcuts import ShortcutManager
from core.screenshot import ScreenshotController
from core.notifications import NotificationManager
from config import tr


class FloatingAssistantApp:

    def __init__(self):

        self.settings = SettingsStorage()

        ctk.set_appearance_mode(self.settings.get("theme", "dark"))
        ctk.set_default_color_theme("blue")

        # إجبار الويندوز على فصل الأيقونة في شريط المهام عن بايثون
        try:
            myappid = 'venom.floating.assistant.v1'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

        self.root = ctk.CTk()
        self.root.withdraw()

        # 🔥 الحل الذكي: تأخير تعيين الأيقونة 250 مللي ثانية ليتم تطبيقها بعد استقرار واجهة CustomTkinter
        self.root.after(250, self._apply_app_icon)

        self.notifier = NotificationManager()
        self.shortcut_manager = ShortcutManager()

        self.floating_button = FloatingButton(
            self.root,
            self.settings,
            on_click_callback=self._on_button_clicked,
            on_move_callback=self._on_button_moved,
        )

        self.popup_menu = PopupMenu(self.root, self.settings)
        self.popup_menu.on_open_settings = self._open_settings_window

        self._register_hotkeys()

        self.root.protocol("WM_DELETE_WINDOW", self._on_exit)

    def _apply_app_icon(self) -> None:
        """دالة مخصصة لتعيين الأيقونة بعد تشغيل التطبيق لضمان عدم تخطيها"""
        try:
            # محاولة تعيين ملف الـ ICO أولاً لأنه المفضل للويندوز
            self.root.iconbitmap("venom8.ico")
        except Exception:
            try:
                # حل احتياطي بالـ PNG المتاح بالفولدر عندك لو الـ ICO فيه مشكلة
                img = Image.open("venom8.png")
                self.app_icon = ImageTk.PhotoImage(img)
                self.root.iconphoto(True, self.app_icon)
            except Exception as e:
                print(f"خطأ في تحميل الأيقونة: {e}")

    # -------------------------------------------------------------------
    def _on_button_clicked(self, x: int, y: int, size: int) -> None:
        self.floating_button.pulse_animation()
        self.popup_menu.toggle_at(x, y, size)

    def _on_button_moved(self, x: int, y: int) -> None:
        pass

    def _open_settings_window(self) -> None:
        settings_win = SettingsWindow(
            self.root,
            self.settings,
            on_settings_applied=self._apply_settings_changes,
        )
        settings_win.grab_set()

    def _apply_settings_changes(self) -> None:
        self.floating_button.apply_settings()
        self.popup_menu.refresh_language()
        self.popup_menu.screenshot.set_save_directory(self.settings.get("screenshot_save_path"))
        self._register_hotkeys()

    # -------------------------------------------------------------------
    def _register_hotkeys(self) -> None:
        toggle_key = self.settings.get("hotkey_toggle_menu", "ctrl+alt+w")
        screenshot_key = self.settings.get("hotkey_screenshot", "ctrl+alt+s")

        self.shortcut_manager.update("toggle_menu", toggle_key, self._hotkey_toggle_menu)
        self.shortcut_manager.update("screenshot", screenshot_key, self._hotkey_take_screenshot)

    def _hotkey_toggle_menu(self) -> None:
        x = self.floating_button.winfo_x()
        y = self.floating_button.winfo_y()
        size = self.floating_button._size
        self.root.after(0, lambda: self.popup_menu.toggle_at(x, y, size))

    def _hotkey_take_screenshot(self) -> None:
        def notify_result():
            path = self.popup_menu.screenshot.capture()
            if path:
                self.notifier.notify(
                    tr("screenshot", self.settings.get("language", "ar")),
                    tr("screenshot_saved", self.settings.get("language", "ar")),
                )
        import threading
        threading.Thread(target=notify_result, daemon=True).start()

    def _on_exit(self) -> None:
        self.shortcut_manager.unregister_all()
        self.root.destroy()
        sys.exit(0)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = FloatingAssistantApp()
    app.run()


if __name__ == "__main__":
    main()