import customtkinter as ctk
from PIL import Image, ImageTk  # استيراد مكتبة التعامل مع الصور
import os

from utils.animations import WindowAnimator


class FloatingButton(ctk.CTkToplevel):

    def __init__(self, master, settings_storage, on_click_callback, on_move_callback):
        super().__init__(master)
        self.settings = settings_storage
        self.on_click_callback = on_click_callback
        self.on_move_callback = on_move_callback

        self.overrideredirect(True)         
        self.attributes("-topmost", True)    
        self.attributes("-alpha", self.settings.get("button_opacity", 0.9))
        self.config(bg="#000001")           
        self.attributes("-transparentcolor", "#000001")

        self._size = self.settings.get("button_size", 60)
        self._drag_data = {"x": 0, "y": 0, "dragging": False}
        self._animator = WindowAnimator(self, duration=self.settings.get("animation_speed", 0.15))
        
        # متغير لمنع اختفاء الصورة من الذاكرة (Garbage Collection)
        self.button_image_tk = None 

        self._build_canvas()
        self._bind_events()
        self._restore_position()

    def _build_canvas(self) -> None:
        self.canvas = ctk.CTkCanvas(
            self,
            width=self._size,
            height=self._size,
            highlightthickness=0,
            bg="#000001",
        )
        self.canvas.pack()
        self._draw_button_image()  # استدعاء دالة رسم الصورة الجديدة بدلاً من الدائرة
        self.geometry(f"{self._size}x{self._size}")

    def _draw_button_image(self) -> None:
        """تقوم هذه الدالة بمسح الكانفاس ورسم صورة venom.png بداخلها بحجم متناسق"""
        self.canvas.delete("all")
        
        # اسم ملف الصورة (تأكد من وجوده في نفس مجلد ملف main.py)
        image_path = "venom.png" 
        
        if os.path.exists(image_path):
            try:
                # فتح الصورة وتعديل حجمها ديناميكياً بناءً على حجم الزر في الإعدادات
                pil_img = Image.open(image_path)
                pil_img = pil_img.resize((self._size, self._size), Image.Resampling.LANCZOS)
                
                # تحويل الصورة لصيغة متوافقة مع تفاعلات الـ Canvas
                self.button_image_tk = ImageTk.PhotoImage(pil_img)
                
                # وضع الصورة داخل الكانفاس من الحافة العلوية اليسرى (0, 0)
                self.canvas.create_image(0, 0, anchor="nw", image=self.button_image_tk)
            except Exception as e:
                print(f"Error loading image: {e}")
                # حل احتياطي في حال حدوث خطأ أثناء تحميل الصورة
                self._draw_fallback_circle("#3B8ED0")
        else:
            # حل احتياطي إذا لم يجد البرنامج ملف الصورة لكي لا يتوقف عن العمل
            self._draw_fallback_circle("#3B8ED0")

    def _draw_fallback_circle(self, color: str) -> None:
        """رسم دائرة احتياطية في حال عدم العثور على ملف الصورة"""
        padding = 2
        self.canvas.create_oval(
            padding, padding, self._size - padding, self._size - padding,
            fill=color, outline="#FFFFFF", width=2
        )

    def _bind_events(self) -> None:
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

    def _on_press(self, event) -> None:
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self._drag_data["dragging"] = False

    def _on_drag(self, event) -> None:
        self._drag_data["dragging"] = True
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]

        new_x = self.winfo_x() + dx
        new_y = self.winfo_y() + dy

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        new_x = max(0, min(screen_w - self._size, new_x))
        new_y = max(0, min(screen_h - self._size, new_y))

        self.geometry(f"+{new_x}+{new_y}")

    def _on_release(self, event) -> None:
        if self._drag_data["dragging"]:
            self._save_position()
            if self.on_move_callback:
                self.on_move_callback(self.winfo_x(), self.winfo_y())
        else:
            if self.on_click_callback:
                self.on_click_callback(self.winfo_x(), self.winfo_y(), self._size)
        self._drag_data["dragging"] = False

    def _restore_position(self) -> None:
        x = self.settings.get("position_x", 100)
        y = self.settings.get("position_y", 100)

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(0, min(screen_w - self._size, x))
        y = max(0, min(screen_h - self._size, y))

        self.geometry(f"{self._size}x{self._size}+{x}+{y}")

    def _save_position(self) -> None:
        self.settings.update_many({
            "position_x": self.winfo_x(),
            "position_y": self.winfo_y(),
        })

    def apply_settings(self) -> None:
        new_size = self.settings.get("button_size", 60)
        if new_size != self._size:
            self._size = new_size
            self.canvas.config(width=self._size, height=self._size)
            self.geometry(f"{self._size}x{self._size}")

        self._draw_button_image()  # إعادة رسم وتكبير/تصغير الصورة بناءً على الحجم الجديد
        self.attributes("-alpha", self.settings.get("button_opacity", 0.9))
        self._animator.duration = self.settings.get("animation_speed", 0.15)

    def pulse_animation(self) -> None:
        # تم إيقاف تأثير الـ pulse القديم لأنه يعتمد على الألوان الفيكتور وليس الصور
        pass