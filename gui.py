import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pystray
from pystray import MenuItem as item

# Ensure UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import font_installer
import patcher

BG_COLOR = "#181825"
CARD_BG = "#1e1e2e"
TEXT_COLOR = "#cdd6f4"
ACCENT_COLOR = "#89b4fa"
SUCCESS_COLOR = "#a6e3a1"
WARNING_COLOR = "#f9e2af"
DANGER_COLOR = "#f38ba8"
BUTTON_BG = "#313244"
BUTTON_HOVER = "#45475a"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_ICO = os.path.join(SCRIPT_DIR, "icon.ico")
ICON_PNG = os.path.join(SCRIPT_DIR, "icon.png")

class PersianFixerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PersianFixer — اصلاح راست‌چین و فونت وزیرمتن")
        self.geometry("690x750")
        self.minsize(620, 680)
        self.configure(bg=BG_COLOR)

        # Set Window Icon
        if os.path.exists(ICON_ICO):
            try:
                self.iconbitmap(ICON_ICO)
            except Exception:
                pass

        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self.tray_icon = None

        self.setup_ui()
        self.setup_tray()
        self.refresh_statuses()

    def setup_ui(self):
        # Header with Logo
        header_frame = tk.Frame(self, bg=BG_COLOR)
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        # Logo thumbnail
        if os.path.exists(ICON_PNG):
            try:
                pil_logo = Image.open(ICON_PNG).resize((52, 52), Image.Resampling.LANCZOS)
                self.logo_tk = ImageTk.PhotoImage(pil_logo)
                logo_lbl = tk.Label(header_frame, image=self.logo_tk, bg=BG_COLOR)
                logo_lbl.pack(side="right", padx=(12, 0))
            except Exception:
                pass

        header_text_frame = tk.Frame(header_frame, bg=BG_COLOR)
        header_text_frame.pack(side="right", fill="both", expand=True)

        title_lbl = tk.Label(
            header_text_frame,
            text="PersianFixer — دستیار فارسی Antigravity و Claude",
            font=("Vazirmatn", 13, "bold"),
            bg=BG_COLOR,
            fg=ACCENT_COLOR,
            anchor="e"
        )
        title_lbl.pack(fill="x")

        subtitle_lbl = tk.Label(
            header_text_frame,
            text="پشتیبانی کامل از راست‌چین (RTL) خودکار و فونت استاندارد Google Vazirmatn",
            font=("Vazirmatn", 9),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            anchor="e"
        )
        subtitle_lbl.pack(fill="x", pady=2)

        # 1-Click Action Button
        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(fill="x", padx=20, pady=(4, 10))

        self.btn_fix_all = tk.Button(
            btn_frame,
            text="🚀 اعمال هوشمند همه‌جانبه (نصب فونت + پچ Antigravity + پچ Claude)",
            font=("Vazirmatn", 11, "bold"),
            bg="#007acc",
            fg="white",
            activebackground="#005999",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=9,
            command=self.action_fix_all
        )
        self.btn_fix_all.pack(fill="x")

        # Cards Container
        cards_container = tk.Frame(self, bg=BG_COLOR)
        cards_container.pack(fill="x", padx=20, pady=2)

        # Card 1: Font
        self.card_font = self.create_card(cards_container, "🔤 فونت رسمی گوگل وزیرمتن (Vazirmatn)")
        self.font_status_lbl = tk.Label(self.card_font, text="در حال بررسی وضعیت...", font=("Vazirmatn", 9), bg=CARD_BG, fg=TEXT_COLOR)
        self.font_status_lbl.pack(anchor="e", padx=15, pady=(2, 6))

        btn_box_font = tk.Frame(self.card_font, bg=CARD_BG)
        btn_box_font.pack(anchor="e", padx=15, pady=(0, 8))
        self.btn_install_font = tk.Button(
            btn_box_font, text="نصب / فعال‌سازی فونت", font=("Vazirmatn", 9), bg=BUTTON_BG, fg=TEXT_COLOR, relief="flat", cursor="hand2", padx=10, pady=3,
            command=self.action_install_font
        )
        self.btn_install_font.pack(side="right", padx=5)

        # Card 2: Antigravity
        self.card_ag = self.create_card(cards_container, "⚡ برنامه Antigravity (ادیتور و چت)")
        self.ag_status_lbl = tk.Label(self.card_ag, text="در حال بررسی وضعیت...", font=("Vazirmatn", 9), bg=CARD_BG, fg=TEXT_COLOR)
        self.ag_status_lbl.pack(anchor="e", padx=15, pady=(2, 6))

        btn_box_ag = tk.Frame(self.card_ag, bg=CARD_BG)
        btn_box_ag.pack(anchor="e", padx=15, pady=(0, 8))

        self.btn_restore_ag = tk.Button(
            btn_box_ag, text="بازگردانی به نسخه اولیه (Restore)", font=("Vazirmatn", 9), bg=BUTTON_BG, fg=DANGER_COLOR, relief="flat", cursor="hand2", padx=8, pady=3,
            command=self.action_restore_ag
        )
        self.btn_restore_ag.pack(side="left", padx=5)

        self.btn_launch_ag = tk.Button(
            btn_box_ag, text="اجرای Antigravity", font=("Vazirmatn", 9), bg=BUTTON_BG, fg=ACCENT_COLOR, relief="flat", cursor="hand2", padx=8, pady=3,
            command=self.action_launch_ag
        )
        self.btn_launch_ag.pack(side="left", padx=5)

        self.btn_patch_ag = tk.Button(
            btn_box_ag, text="اعمال پچ فارسی و فونت", font=("Vazirmatn", 9, "bold"), bg=BUTTON_BG, fg=SUCCESS_COLOR, relief="flat", cursor="hand2", padx=10, pady=3,
            command=self.action_patch_ag
        )
        self.btn_patch_ag.pack(side="right", padx=5)

        # Card 3: Claude Desktop
        self.card_claude = self.create_card(cards_container, "💬 برنامه Claude Desktop ویندوز")
        self.claude_status_lbl = tk.Label(self.card_claude, text="در حال بررسی وضعیت...", font=("Vazirmatn", 9), bg=CARD_BG, fg=TEXT_COLOR)
        self.claude_status_lbl.pack(anchor="e", padx=15, pady=(2, 6))

        btn_box_claude = tk.Frame(self.card_claude, bg=CARD_BG)
        btn_box_claude.pack(anchor="e", padx=15, pady=(0, 8))

        self.btn_launch_claude = tk.Button(
            btn_box_claude, text="اجرای Claude فارسی", font=("Vazirmatn", 9), bg=BUTTON_BG, fg=ACCENT_COLOR, relief="flat", cursor="hand2", padx=8, pady=3,
            command=self.action_launch_claude
        )
        self.btn_launch_claude.pack(side="left", padx=5)

        self.btn_patch_claude = tk.Button(
            btn_box_claude, text="اعمال پچ و ساخت میانبر دسکتاپ", font=("Vazirmatn", 9, "bold"), bg=BUTTON_BG, fg=SUCCESS_COLOR, relief="flat", cursor="hand2", padx=10, pady=3,
            command=self.action_patch_claude
        )
        self.btn_patch_claude.pack(side="right", padx=5)

        # Tray reminder note
        tray_note = tk.Label(
            self,
            text="💡 هنگام بستن پنجره، برنامه به سینی ویندوز (System Tray کنار ساعت) منتقل می‌شود.",
            font=("Vazirmatn", 8),
            bg=BG_COLOR,
            fg="#6c7086"
        )
        tray_note.pack(pady=(2, 4))

        # Log Frame
        log_frame = tk.Frame(self, bg=BG_COLOR)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(2, 12))

        log_lbl = tk.Label(log_frame, text="گزارش عملیات:", font=("Vazirmatn", 9, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        log_lbl.pack(anchor="e", pady=(0, 2))

        self.log_text = tk.Text(
            log_frame,
            font=("Consolas", 9),
            bg="#11111b",
            fg="#a6adc8",
            relief="flat",
            wrap="word",
            height=6
        )
        self.log_text.pack(fill="both", expand=True)

        self.log("برنامه با موفقیت راه‌اندازی شد و آماده است.")

    def create_card(self, parent, title):
        frame = tk.Frame(parent, bg=CARD_BG, highlightbackground="#313244", highlightthickness=1)
        frame.pack(fill="x", pady=4)
        title_lbl = tk.Label(frame, text=title, font=("Vazirmatn", 10, "bold"), bg=CARD_BG, fg=ACCENT_COLOR)
        title_lbl.pack(anchor="e", padx=15, pady=(6, 2))
        return frame

    def log(self, message):
        self.log_text.insert("end", f"> {message}\n")
        self.log_text.see("end")

    def setup_tray(self):
        """Initializes the System Tray icon in background."""
        try:
            if os.path.exists(ICON_PNG):
                tray_image = Image.open(ICON_PNG).resize((64, 64), Image.Resampling.LANCZOS)
            else:
                tray_image = Image.new('RGB', (64, 64), color=(0, 122, 204))

            menu = pystray.Menu(
                item('نمایش پنجره اصلی', self.restore_from_tray, default=True),
                pystray.Menu.SEPARATOR,
                item('اجرای Claude فارسی', lambda: patcher.launch_claude()),
                item('اجرای Antigravity', lambda: patcher.launch_antigravity()),
                pystray.Menu.SEPARATOR,
                item('خروج کامل', self.quit_app)
            )

            self.tray_icon = pystray.Icon("PersianFixer", tray_image, "PersianFixer (راست‌چین و فونت وزیرمتن)", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception as e:
            self.log(f"خطا در ایجاد System Tray: {e}")

    def minimize_to_tray(self):
        """Hides the window and leaves the icon in the tray."""
        self.withdraw()

    def restore_from_tray(self, icon=None, item=None):
        """Restores the main window from tray."""
        self.after(0, self._show_window)

    def _show_window(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def quit_app(self, icon=None, item=None):
        """Completely exits the app."""
        if self.tray_icon:
            self.tray_icon.stop()
        self.after(0, self.destroy)
        os._exit(0)

    def refresh_statuses(self):
        def worker():
            font_installed = font_installer.is_font_installed()
            ag_status = patcher.get_antigravity_status()
            claude_status = patcher.get_claude_status()

            def update():
                if font_installed:
                    self.font_status_lbl.config(text="وضعیت: فونت وزیرمتن در سیستم ویندوز نصب و فعال است ✓", fg=SUCCESS_COLOR)
                    self.btn_install_font.config(text="نصب مجدد فونت")
                else:
                    self.font_status_lbl.config(text="وضعیت: فونت وزیرمتن نصب نیست ⚠️", fg=WARNING_COLOR)
                    self.btn_install_font.config(text="نصب فونت وزیرمتن")

                if not ag_status["installed"]:
                    self.ag_status_lbl.config(text="وضعیت: فایل‌های Antigravity یافت نشد ❌", fg=DANGER_COLOR)
                elif ag_status["patched"]:
                    run_txt = " (درحال اجرا)" if ag_status["running"] else ""
                    self.ag_status_lbl.config(text=f"وضعیت: پچ شده با فونت وزیرمتن و راست‌چین فعال است ✓{run_txt}", fg=SUCCESS_COLOR)
                    self.btn_patch_ag.config(text="به‌روزرسانی پچ")
                else:
                    run_txt = " (درحال اجرا)" if ag_status["running"] else ""
                    self.ag_status_lbl.config(text=f"وضعیت: آماده اعمال پچ فارسی{run_txt}", fg=WARNING_COLOR)
                    self.btn_patch_ag.config(text="اعمال پچ فارسی")

                self.btn_restore_ag.config(state="normal" if ag_status["backup"] else "disabled")

                if not claude_status["installed"]:
                    self.claude_status_lbl.config(text="وضعیت: برنامه رسمی Claude در ویندوز یافت نشد ❌", fg=DANGER_COLOR)
                elif claude_status["patched"]:
                    run_txt = " (درحال اجرا)" if claude_status["running"] else ""
                    self.claude_status_lbl.config(text=f"وضعیت: نسخه فارسی Claude آماده در دسکتاپ ✓{run_txt}", fg=SUCCESS_COLOR)
                    self.btn_launch_claude.config(state="normal")
                else:
                    self.claude_status_lbl.config(text="وضعیت: آماده راه‌اندازی نسخه فارسی و شورتکات دسکتاپ", fg=WARNING_COLOR)

            self.after(0, update)

        threading.Thread(target=worker, daemon=True).start()

    def action_install_font(self):
        self.log("درحال نصب فونت وزیرمتن در ویندوز...")
        ok, msg = font_installer.install_vazirmatn_font()
        self.log(msg)
        self.refresh_statuses()
        if ok:
            messagebox.showinfo("موفقیت", "فونت وزیرمتن با موفقیت بر روی سیستم شما نصب و فعال شد.")

    def action_patch_ag(self):
        ag_status = patcher.get_antigravity_status()
        if ag_status["running"]:
            if messagebox.askyesno("بستن برنامه", "برنامه Antigravity هم‌اکنون باز است.\nبرای اعمال پچ لازم است برنامه موقتاً بسته شود. آیا تایید می‌کنید؟"):
                patcher.close_process("Antigravity.exe")
            else:
                self.log("عملیات لغو شد. لطفاً ابتدا Antigravity را ببندید.")
                return

        self.log("درحال اعمال پچ روی فایل‌های Antigravity...")
        ok, msg = patcher.patch_antigravity(auto_close=True)
        self.log(msg)
        self.refresh_statuses()
        if ok:
            if messagebox.askyesno("اتمام موفقیت‌آمیز", "Antigravity با موفقیت پچ شد!\nآیا مایلید هم‌اکنون برنامه باز شود؟"):
                patcher.launch_antigravity()

    def action_launch_ag(self):
        ok, msg = patcher.launch_antigravity()
        self.log(msg)

    def action_restore_ag(self):
        if messagebox.askyesno("تایید بازگردانی", "آیا مطمئنید که می‌خواهید Antigravity را به نسخه بدون پچ اولیه بازگردانید؟"):
            self.log("درحال بازگردانی Antigravity از نسخه پشتیبان...")
            ok, msg = patcher.restore_antigravity(auto_close=True)
            self.log(msg)
            self.refresh_statuses()
            messagebox.showinfo("نتیجه", msg)

    def action_patch_claude(self):
        self.log("درحال آماده‌سازی و پچ نسخه Claude...")
        ok, msg = patcher.patch_claude()
        self.log(msg)
        self.refresh_statuses()
        if ok:
            messagebox.showinfo("موفقیت", "برنامه Claude با فونت وزیرمتن و راست‌چین پچ شد و شورتکات «Claude-Persian» روی دسکتاپ ایجاد گردید.")

    def action_launch_claude(self):
        ok, msg = patcher.launch_claude()
        self.log(msg)

    def action_fix_all(self):
        self.log("شروع فرآیند اصلاح هوشمند همه‌جانبه...")

        def run_all():
            self.log("۱. بررسی و نصب فونت وزیرمتن...")
            ok_font, msg_font = font_installer.install_vazirmatn_font()
            self.log(f"   {msg_font}")

            self.log("۲. آماده‌سازی و پچ Claude Desktop...")
            ok_claude, msg_claude = patcher.patch_claude()
            self.log(f"   {msg_claude}")

            ag_stat = patcher.get_antigravity_status()
            if ag_stat["running"]:
                self.log("۳. برنامه Antigravity باز است. برای جایگزینی فایل، دکمه «اعمال پچ فارسی» را کلیک کنید.")
            else:
                self.log("۳. درحال پچ Antigravity...")
                ok_ag, msg_ag = patcher.patch_antigravity(auto_close=False)
                self.log(f"   {msg_ag}")

            self.log("عملیات با موفقیت پایان یافت ✓")
            self.refresh_statuses()
            messagebox.showinfo(
                "پایان عملیات",
                "عملیات هوشمند پایان یافت!\n\n• فونت وزیرمتن نصب و فعال شد.\n• نسخه ویژه Claude با فونت و راست‌چین روی دسکتاپ ایجاد شد.\n• وضعیت Antigravity به‌روزرسانی گردید."
            )

        threading.Thread(target=run_all, daemon=True).start()

if __name__ == "__main__":
    app = PersianFixerApp()
    app.mainloop()