import os
import sys
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pystray
from pystray import MenuItem as item

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import font_installer
import patcher

# --- COLOR PALETTE (Modern Deep Slate & Neon Accents) ---
BG_MAIN = "#0b0f19"
BG_CARD = "#131b2e"
BG_CARD_HOVER = "#18223a"
BORDER_COLOR = "#1e293b"
TEXT_PRIMARY = "#f8fafc"
TEXT_SECONDARY = "#94a3b8"
TEXT_MUTED = "#64748b"

ACCENT_CYAN = "#06b6d4"
ACCENT_BLUE = "#3b82f6"
ACCENT_PURPLE = "#8b5cf6"
STATUS_SUCCESS = "#10b981"
STATUS_WARNING = "#f59e0b"
STATUS_DANGER = "#ef4444"

BTN_PRIMARY = "#2563eb"
BTN_PRIMARY_HOVER = "#1d4ed8"
BTN_SECONDARY = "#1e293b"
BTN_SECONDARY_HOVER = "#334155"
BTN_SUCCESS = "#059669"
BTN_SUCCESS_HOVER = "#047857"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_ICO = os.path.join(SCRIPT_DIR, "icon.ico")
ICON_PNG = os.path.join(SCRIPT_DIR, "icon.png")

FONT_FAMILY = "Segoe UI"

class PersianFixerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PersianFixer v3.5 — دستیار فارسی و فونت وزیرمتن")
        self.geometry("710x840")
        self.minsize(660, 720)
        self.configure(bg=BG_MAIN)

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
        # 1. TOP HEADER
        header_frame = tk.Frame(self, bg=BG_MAIN)
        header_frame.pack(fill="x", padx=20, pady=(12, 6))

        if os.path.exists(ICON_PNG):
            try:
                pil_img = Image.open(ICON_PNG).resize((52, 52), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(pil_img)
                logo_lbl = tk.Label(header_frame, image=self.logo_img, bg=BG_MAIN)
                logo_lbl.pack(side="right", padx=(10, 0))
            except Exception:
                pass

        title_container = tk.Frame(header_frame, bg=BG_MAIN)
        title_container.pack(side="right", fill="y")

        top_row = tk.Frame(title_container, bg=BG_MAIN)
        top_row.pack(anchor="e")

        badge_lbl = tk.Label(
            top_row, text="v3.5.0 STABLE", font=(FONT_FAMILY, 8, "bold"),
            bg="#1e293b", fg=ACCENT_CYAN, padx=6, pady=2
        )
        badge_lbl.pack(side="left", padx=(0, 8))

        main_title = tk.Label(
            top_row, text="PersianFixer — دستیار هوشمند فارسی",
            font=(FONT_FAMILY, 15, "bold"), bg=BG_MAIN, fg=TEXT_PRIMARY
        )
        main_title.pack(side="left")

        subtitle = tk.Label(
            title_container,
            text="راست‌چین هوشمند و فونت رسمی گوگل وزیرمتن برای Antigravity ،Claude ،OpenCode و ChatGPT",
            font=(FONT_FAMILY, 9), bg=BG_MAIN, fg=TEXT_SECONDARY
        )
        subtitle.pack(anchor="e", pady=(2, 0))

        # 2. MASTER STATUS CARD (نشانگر وضعیت جامع سیستم)
        self.master_card = tk.Frame(self, bg="#064e3b", highlightbackground=STATUS_SUCCESS, highlightthickness=1)
        self.master_card.pack(fill="x", padx=20, pady=(4, 8))

        master_inner = tk.Frame(self.master_card, bg="#064e3b")
        master_inner.pack(fill="x", padx=14, pady=8)

        self.master_status_lbl = tk.Label(
            master_inner, text="🟢 در حال بررسی وضعیت سیستم...",
            font=(FONT_FAMILY, 10, "bold"), bg="#064e3b", fg="#a7f3d0"
        )
        self.master_status_lbl.pack(anchor="e")

        self.master_sub_lbl = tk.Label(
            master_inner, text="وضعیت اتصال و فعال بودن پشتیبانی در نرم‌افزارهای دسکتاپ",
            font=(FONT_FAMILY, 8), bg="#064e3b", fg="#6ee7b7"
        )
        self.master_sub_lbl.pack(anchor="e", pady=(2, 0))

        # 3. MASTER 1-CLICK ACTION BUTTON
        btn_master = tk.Button(
            self, text="🚀  اعمال هوشمند پچ و فونت برای تمام برنامه‌ها (۱ کلیک)",
            font=(FONT_FAMILY, 11, "bold"), bg=BTN_PRIMARY, fg="white",
            activebackground=BTN_PRIMARY_HOVER, activeforeground="white",
            relief="flat", cursor="hand2", padx=12, pady=8,
            command=self.action_patch_all
        )
        btn_master.pack(fill="x", padx=20, pady=(2, 8))

        # 4. SCROLLABLE CONTAINER FOR APP CARDS
        container = tk.Frame(self, bg=BG_MAIN)
        container.pack(fill="both", expand=True, padx=20)

        canvas = tk.Canvas(container, bg=BG_MAIN, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scroll_content = tk.Frame(canvas, bg=BG_MAIN)

        self.scroll_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scroll_content, anchor="nw", width=650)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # --- CARD 1: VAZIRMATN FONT ---
        self.card_font = self.create_app_card(
            self.scroll_content,
            title="فونت رسمی گوگل وزیرمتن (Vazirmatn Variable)",
            subtitle="نصب مستقیم وزن‌های ۱۰۰ تا ۹۰۰ در رجیستری ویندوز برای رندر روان متن‌ها"
        )
        self.lbl_font_status = self.create_status_label(self.card_font)
        f_btn_box = tk.Frame(self.card_font, bg=BG_CARD)
        f_btn_box.pack(anchor="w", padx=14, pady=(2, 10))
        self.btn_font = self.create_button(f_btn_box, "نصب مجدد فونت", self.action_install_font, style="secondary")

        # --- CARD 2: ANTIGRAVITY ---
        self.card_ag = self.create_app_card(
            self.scroll_content,
            title="Google Antigravity — ادیتور و چت کدنویسی",
            subtitle="پشتیبانی از راست‌چین پیام‌ها، چت استریم، و تفکیک کدهای LTR"
        )
        self.lbl_ag_status = self.create_status_label(self.card_ag)
        ag_btn_box = tk.Frame(self.card_ag, bg=BG_CARD)
        ag_btn_box.pack(anchor="w", padx=14, pady=(2, 10))
        self.btn_ag_patch = self.create_button(ag_btn_box, "پچ Antigravity", lambda: self.action_patch_app("antigravity"))
        self.btn_ag_restore = self.create_button(ag_btn_box, "بازگردانی اولیه", lambda: self.action_restore_app("antigravity"), style="secondary")
        self.btn_ag_run = self.create_button(ag_btn_box, "اجرای برنامه", lambda: self.action_launch_app("antigravity"), style="success")

        # --- CARD 3: CLAUDE DESKTOP ---
        self.card_claude = self.create_app_card(
            self.scroll_content,
            title="Claude Desktop — کلاینت رسمی ویندوز",
            subtitle="شکستن Electron Fuses، رفع مشکل راست‌چین و ایجاد میانبر استاندارد"
        )
        self.lbl_claude_status = self.create_status_label(self.card_claude)
        cl_btn_box = tk.Frame(self.card_claude, bg=BG_CARD)
        cl_btn_box.pack(anchor="w", padx=14, pady=(2, 10))
        self.btn_claude_patch = self.create_button(cl_btn_box, "پچ Claude", lambda: self.action_patch_app("claude"))
        self.btn_claude_restore = self.create_button(cl_btn_box, "بازگردانی اولیه", lambda: self.action_restore_app("claude"), style="secondary")
        self.btn_claude_run = self.create_button(cl_btn_box, "اجرای Claude", lambda: self.action_launch_app("claude"), style="success")

        # --- CARD 4: OPENCODE ---
        self.card_opencode = self.create_app_card(
            self.scroll_content,
            title="OpenCode — دستیار توسعه هوش مصنوعی",
            subtitle="اعمال فونت فوق‌العاده وزیرمتن و تصحیح دندانه‌ها و فاصله‌های متن فارسی"
        )
        self.lbl_opencode_status = self.create_status_label(self.card_opencode)
        op_btn_box = tk.Frame(self.card_opencode, bg=BG_CARD)
        op_btn_box.pack(anchor="w", padx=14, pady=(2, 10))
        self.btn_opencode_patch = self.create_button(op_btn_box, "پچ OpenCode", lambda: self.action_patch_app("opencode"))
        self.btn_opencode_restore = self.create_button(op_btn_box, "بازگردانی اولیه", lambda: self.action_restore_app("opencode"), style="secondary")
        self.btn_opencode_run = self.create_button(op_btn_box, "اجرای OpenCode", lambda: self.action_launch_app("opencode"), style="success")

        # --- CARD 5: CHATGPT (OPENAI CODEX) ---
        self.card_chatgpt = self.create_app_card(
            self.scroll_content,
            title="ChatGPT (OpenAI Codex) — کلاینت ویندوز",
            subtitle="پچ اختصاصی برای اضافه شدن فونت وزیرمتن و راست‌چین چت‌ها و پرامپت‌ها"
        )
        self.lbl_chatgpt_status = self.create_status_label(self.card_chatgpt)
        cg_btn_box = tk.Frame(self.card_chatgpt, bg=BG_CARD)
        cg_btn_box.pack(anchor="w", padx=14, pady=(2, 10))
        self.btn_chatgpt_patch = self.create_button(cg_btn_box, "پچ ChatGPT", lambda: self.action_patch_app("chatgpt"))
        self.btn_chatgpt_restore = self.create_button(cg_btn_box, "بازگردانی اولیه", lambda: self.action_restore_app("chatgpt"), style="secondary")
        self.btn_chatgpt_run = self.create_button(cg_btn_box, "اجرای ChatGPT", lambda: self.action_launch_app("chatgpt"), style="success")

        # 5. OPERATION LOG BOX (جعبه گزارش عملیات کاملاً راست‌چین و مدرن)
        log_header = tk.Frame(self, bg=BG_MAIN)
        log_header.pack(fill="x", padx=20, pady=(8, 2))

        btn_clear = tk.Label(
            log_header, text="پاکسازی لاگ", font=(FONT_FAMILY, 8),
            bg=BG_MAIN, fg=TEXT_MUTED, cursor="hand2"
        )
        btn_clear.pack(side="left")
        btn_clear.bind("<Button-1>", lambda e: self.clear_log())

        log_title = tk.Label(
            log_header, text="گزارش عملیات سیستم (Live Log):",
            font=(FONT_FAMILY, 9, "bold"), bg=BG_MAIN, fg=TEXT_SECONDARY
        )
        log_title.pack(side="right")

        log_container = tk.Frame(self, bg="#0d1322", highlightbackground=BORDER_COLOR, highlightthickness=1)
        log_container.pack(fill="x", padx=20, pady=(2, 10))

        self.log_text = tk.Text(
            log_container, height=5, bg="#0d1322", fg="#e2e8f0",
            font=(FONT_FAMILY, 9), relief="flat", padx=10, pady=8,
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True)

        # Tags for colored, right-aligned logging
        self.log_text.tag_configure("rtl_success", justify="right", foreground=STATUS_SUCCESS)
        self.log_text.tag_configure("rtl_info", justify="right", foreground=ACCENT_CYAN)
        self.log_text.tag_configure("rtl_warn", justify="right", foreground=STATUS_WARNING)
        self.log_text.tag_configure("rtl_error", justify="right", foreground=STATUS_DANGER)

        self.log("سیستم PersianFixer نسخه ۳.۵ با موفقیت راه‌اندازی شد و آماده به کار است.", tag="rtl_info")

    def create_app_card(self, parent, title, subtitle):
        frame = tk.Frame(parent, bg=BG_CARD, highlightbackground=BORDER_COLOR, highlightthickness=1)
        frame.pack(fill="x", pady=4)

        t_frame = tk.Frame(frame, bg=BG_CARD)
        t_frame.pack(fill="x", padx=14, pady=(8, 2))

        title_lbl = tk.Label(t_frame, text=title, font=(FONT_FAMILY, 10, "bold"), bg=BG_CARD, fg=TEXT_PRIMARY)
        title_lbl.pack(anchor="e")

        sub_lbl = tk.Label(t_frame, text=subtitle, font=(FONT_FAMILY, 8), bg=BG_CARD, fg=TEXT_MUTED)
        sub_lbl.pack(anchor="e", pady=(1, 0))

        return frame

    def create_status_label(self, parent):
        lbl = tk.Label(parent, text="در حال بررسی وضعیت...", font=(FONT_FAMILY, 9), bg=BG_CARD, fg=TEXT_SECONDARY)
        lbl.pack(anchor="e", padx=14, pady=(2, 4))
        return lbl

    def create_button(self, parent, text, command, style="primary"):
        if style == "primary":
            bg, hbg, fg = BTN_PRIMARY, BTN_PRIMARY_HOVER, "white"
        elif style == "success":
            bg, hbg, fg = BTN_SUCCESS, BTN_SUCCESS_HOVER, "white"
        else:
            bg, hbg, fg = BTN_SECONDARY, BTN_SECONDARY_HOVER, "#cbd5e1"

        btn = tk.Button(
            parent, text=text, font=(FONT_FAMILY, 8, "bold"),
            bg=bg, fg=fg, activebackground=hbg, activeforeground=fg,
            relief="flat", cursor="hand2", padx=10, pady=4,
            command=command
        )
        btn.pack(side="right", padx=(6, 0))
        return btn

    def log(self, message, tag="rtl_info"):
        now_str = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{now_str}] {message}\n"
        self.log_text.insert("end", formatted, tag)
        self.log_text.see("end")

    def clear_log(self):
        self.log_text.delete("1.0", "end")

    def refresh_statuses(self):
        def worker():
            font_installed = font_installer.is_font_installed()
            ag_st = patcher.get_antigravity_status()
            cl_st = patcher.get_claude_status()
            op_st = patcher.get_opencode_status()
            cg_st = patcher.get_chatgpt_status()

            def update():
                # 1. Font
                if font_installed:
                    self.lbl_font_status.config(text="وضعیت: فونت رسمی وزیرمتن گوگل در ویندوز فعال است ✓", fg=STATUS_SUCCESS)
                else:
                    self.lbl_font_status.config(text="وضعیت: فونت وزیرمتن نصب نیست ⚠️", fg=STATUS_WARNING)

                # 2. Antigravity
                if not ag_st["installed"]:
                    self.lbl_ag_status.config(text="وضعیت: فایل‌های برنامه یافت نشد ❌", fg=STATUS_DANGER)
                elif ag_st["patched"]:
                    run_txt = " (درحال اجرا ⚡)" if ag_st["running"] else ""
                    self.lbl_ag_status.config(text=f"وضعیت: پچ فعال است — فونت وزیرمتن و RTL متصل گردید ✓{run_txt}", fg=STATUS_SUCCESS)
                    self.btn_ag_patch.config(text="به‌روزرسانی پچ")
                else:
                    run_txt = " (درحال اجرا ⚡)" if ag_st["running"] else ""
                    self.lbl_ag_status.config(text=f"وضعیت: آماده اعمال پچ فارسی{run_txt}", fg=STATUS_WARNING)
                    self.btn_ag_patch.config(text="پچ Antigravity")

                # 3. Claude
                if not cl_st["installed"]:
                    self.lbl_claude_status.config(text="وضعیت: برنامه Claude یافت نشد ❌", fg=STATUS_DANGER)
                elif cl_st["patched"]:
                    run_txt = " (درحال اجرا ⚡)" if cl_st["running"] else ""
                    self.lbl_claude_status.config(text=f"وضعیت: پچ فعال است — شورتکات رسمی متصل است ✓{run_txt}", fg=STATUS_SUCCESS)
                    self.btn_claude_patch.config(text="به‌روزرسانی پچ")
                else:
                    self.lbl_claude_status.config(text="وضعیت: آماده پچ و اتصال میانبر رسمی", fg=STATUS_WARNING)
                    self.btn_claude_patch.config(text="پچ Claude")

                # 4. OpenCode
                if not op_st["installed"]:
                    self.lbl_opencode_status.config(text="وضعیت: برنامه OpenCode یافت نشد ❌", fg=STATUS_DANGER)
                elif op_st["patched"]:
                    run_txt = " (درحال اجرا ⚡)" if op_st["running"] else ""
                    self.lbl_opencode_status.config(text=f"وضعیت: پچ فعال است — فونت وزیرمتن اعمال گردید ✓{run_txt}", fg=STATUS_SUCCESS)
                    self.btn_opencode_patch.config(text="به‌روزرسانی پچ")
                else:
                    run_txt = " (درحال اجرا ⚡)" if op_st["running"] else ""
                    self.lbl_opencode_status.config(text=f"وضعیت: آماده اعمال فونت وزیرمتن{run_txt}", fg=STATUS_WARNING)
                    self.btn_opencode_patch.config(text="پچ OpenCode")

                # 5. ChatGPT
                if not cg_st["installed"]:
                    self.lbl_chatgpt_status.config(text="وضعیت: برنامه رسمی ChatGPT در ویندوز یافت نشد ❌", fg=STATUS_DANGER)
                elif cg_st["patched"]:
                    run_txt = " (درحال اجرا ⚡)" if cg_st["running"] else ""
                    self.lbl_chatgpt_status.config(text=f"وضعیت: پچ فعال است — فونت وزیرمتن و RTL متصل گردید ✓{run_txt}", fg=STATUS_SUCCESS)
                    self.btn_chatgpt_patch.config(text="به‌روزرسانی پچ")
                else:
                    run_txt = " (درحال اجرا ⚡)" if cg_st["running"] else ""
                    self.lbl_chatgpt_status.config(text=f"وضعیت: آماده اعمال پچ فارسی{run_txt}", fg=STATUS_WARNING)
                    self.btn_chatgpt_patch.config(text="پچ ChatGPT")

                # MASTER STATUS EVALUATION
                installed_apps = [ag_st["installed"], cl_st["installed"], op_st["installed"], cg_st["installed"]]
                patched_apps = [ag_st["patched"], cl_st["patched"], op_st["patched"], cg_st["patched"]]
                total_installed = sum(1 for x in installed_apps if x)
                total_patched = sum(1 for x in patched_apps if x)

                if total_installed > 0 and total_patched == total_installed and font_installed:
                    self.master_card.config(bg="#064e3b", highlightbackground=STATUS_SUCCESS)
                    self.master_status_lbl.config(
                        text=f"🟢 وضعیت کلی: سیستم کاملاً فعال است ({total_patched} از {total_installed} نرم‌افزار پچ و مجهز به وزیرمتن شدند)",
                        bg="#064e3b", fg="#a7f3d0"
                    )
                    self.master_sub_lbl.config(
                        text="پشتیبانی از راست‌چین و فونت استاندارد روی تمامی ابزارهای شناسایی‌شده فعال است.",
                        bg="#064e3b", fg="#6ee7b7"
                    )
                else:
                    self.master_card.config(bg="#451a03", highlightbackground=STATUS_WARNING)
                    self.master_status_lbl.config(
                        text=f"🟡 وضعیت کلی: نیاز به اعمال پچ ({total_patched} از {total_installed} نرم‌افزار فعال هستند)",
                        bg="#451a03", fg="#fde68a"
                    )
                    self.master_sub_lbl.config(
                        text="برای فعال‌سازی کامل، روی دکمه آبی‌رنگ «اعمال هوشمند پچ و فونت برای تمام برنامه‌ها» کلیک کنید.",
                        bg="#451a03", fg="#fcd34d"
                    )

            self.after(0, update)

        threading.Thread(target=worker, daemon=True).start()

    def action_install_font(self):
        self.log("در حال نصب فونت رسمی وزیرمتن در سیستم ویندوز...", "rtl_info")
        ok = font_installer.install_vazirmatn_font()
        if ok:
            self.log("فونت وزیرمتن با موفقیت در ویندوز نصب و فعال گردید. ✔", "rtl_success")
        else:
            self.log("خطا در نصب فونت وزیرمتن. ✖", "rtl_error")
        self.refresh_statuses()

    def action_patch_all(self):
        def worker():
            self.log("شروع عملیات جامع: اعمال هوشمند پچ و فونت روی تمام ابزارها...", "rtl_info")
            font_installer.install_vazirmatn_font()

            # Antigravity
            ag_st = patcher.get_antigravity_status()
            if ag_st["installed"]:
                ok, msg = patcher.patch_antigravity(auto_close=True)
                tag = "rtl_success" if ok else "rtl_error"
                self.log(f"Antigravity: {msg}", tag)

            # Claude
            cl_st = patcher.get_claude_status()
            if cl_st["installed"]:
                ok, msg = patcher.patch_claude(auto_close=True)
                tag = "rtl_success" if ok else "rtl_error"
                self.log(f"Claude Desktop: {msg}", tag)

            # OpenCode
            op_st = patcher.get_opencode_status()
            if op_st["installed"]:
                ok, msg = patcher.patch_opencode(auto_close=True)
                tag = "rtl_success" if ok else "rtl_error"
                self.log(f"OpenCode: {msg}", tag)

            # ChatGPT
            cg_st = patcher.get_chatgpt_status()
            if cg_st["installed"]:
                ok, msg = patcher.patch_chatgpt(auto_close=True)
                tag = "rtl_success" if ok else "rtl_error"
                self.log(f"ChatGPT (Codex): {msg}", tag)

            self.log("عملیات جامع پچ به پایان رسید. وضعیت سیستم به‌روزرسانی شد. ✔", "rtl_success")
            self.refresh_statuses()

        threading.Thread(target=worker, daemon=True).start()

    def action_patch_app(self, app_name):
        def worker():
            if app_name == "antigravity":
                ok, msg = patcher.patch_antigravity(auto_close=True)
            elif app_name == "claude":
                ok, msg = patcher.patch_claude(auto_close=True)
            elif app_name == "opencode":
                ok, msg = patcher.patch_opencode(auto_close=True)
            elif app_name == "chatgpt":
                ok, msg = patcher.patch_chatgpt(auto_close=True)
            else:
                return

            tag = "rtl_success" if ok else "rtl_error"
            self.log(f"{app_name.capitalize()}: {msg}", tag)
            self.refresh_statuses()

        threading.Thread(target=worker, daemon=True).start()

    def action_restore_app(self, app_name):
        def worker():
            if app_name == "antigravity":
                ok, msg = patcher.restore_antigravity(auto_close=True)
            elif app_name == "claude":
                ok, msg = patcher.restore_claude(auto_close=True)
            elif app_name == "opencode":
                ok, msg = patcher.restore_opencode(auto_close=True)
            elif app_name == "chatgpt":
                ok, msg = patcher.restore_chatgpt(auto_close=True)
            else:
                return

            tag = "rtl_info" if ok else "rtl_error"
            self.log(f"بازگردانی {app_name.capitalize()}: {msg}", tag)
            self.refresh_statuses()

        threading.Thread(target=worker, daemon=True).start()

    def action_launch_app(self, app_name):
        if app_name == "antigravity":
            ok, msg = patcher.launch_antigravity()
        elif app_name == "claude":
            ok, msg = patcher.launch_claude()
        elif app_name == "opencode":
            ok, msg = patcher.launch_opencode()
        elif app_name == "chatgpt":
            ok, msg = patcher.launch_chatgpt()
        else:
            return

        tag = "rtl_info" if ok else "rtl_error"
        self.log(f"اجرا: {msg}", tag)

    def setup_tray(self):
        try:
            if os.path.exists(ICON_PNG):
                tray_image = Image.open(ICON_PNG).resize((64, 64), Image.Resampling.LANCZOS)
            else:
                tray_image = Image.new('RGB', (64, 64), color=(0, 122, 204))

            menu = pystray.Menu(
                item('نمایش پنجره PersianFixer', self.restore_from_tray, default=True),
                pystray.Menu.SEPARATOR,
                item('اجرای Antigravity', lambda: patcher.launch_antigravity()),
                item('اجرای Claude', lambda: patcher.launch_claude()),
                item('اجرای OpenCode', lambda: patcher.launch_opencode()),
                item('اجرای ChatGPT', lambda: patcher.launch_chatgpt()),
                pystray.Menu.SEPARATOR,
                item('پچ همه برنامه‌ها', lambda: self.action_patch_all()),
                item('خروج کامل', self.quit_app)
            )

            self.tray_icon = pystray.Icon("PersianFixer", tray_image, "PersianFixer v3.5 (دستیار فارسی هوش مصنوعی)", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception as e:
            self.log(f"خطا در ایجاد System Tray: {e}", "rtl_error")

    def minimize_to_tray(self):
        self.withdraw()

    def restore_from_tray(self, icon=None, item=None):
        self.after(0, self._show_window)

    def _show_window(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def quit_app(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.after(0, self.destroy)
        os._exit(0)

if __name__ == "__main__":
    app = PersianFixerApp()
    app.mainloop()