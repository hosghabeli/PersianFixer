import os
import sys
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pystray
from pystray import MenuItem as item

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import font_installer
import patcher
import autostart

# --- COLOR PALETTE (Modern Ultra-Clean Dark Slate) ---
BG_MAIN = "#0d1117"        # Deep slate background
BG_HEADER = "#161b22"      # Header surface
BG_CARD = "#161b22"        # Card surface
BG_CARD_ALT = "#1f242c"    # Card hover / active
BORDER_COLOR = "#30363d"   # Subtle clean border
BORDER_SUBTLE = "#21262d"

TEXT_WHITE = "#f0f6fc"
TEXT_MUTED = "#8b949e"
TEXT_DIM = "#6e7681"

ACCENT_BLUE = "#2f81f7"
ACCENT_BLUE_HOVER = "#388bfd"
ACCENT_CYAN = "#38bdf8"
ACCENT_PURPLE = "#a855f7"

STATUS_OK_BG = "#0d2818"
STATUS_OK_BORDER = "#238636"
STATUS_OK_TEXT = "#3fb950"

STATUS_WARN_BG = "#271c0c"
STATUS_WARN_BORDER = "#9e6a03"
STATUS_WARN_TEXT = "#d29922"

STATUS_ERR_TEXT = "#f85149"

BTN_DARK = "#21262d"
BTN_DARK_HOVER = "#30363d"
BTN_PRIMARY = "#238636"
BTN_PRIMARY_HOVER = "#2ea043"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_ICO = os.path.join(SCRIPT_DIR, "icon.ico")
ICON_PNG = os.path.join(SCRIPT_DIR, "icon.png")

FONT_NAME = "Segoe UI"

class PersianFixerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PersianFixer")
        
        # Fixed compact, elegant geometry (no stretching, perfectly centered)
        win_w, win_h = 580, 710
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        pos_x = max(0, int((screen_w - win_w) / 2))
        pos_y = max(0, int((screen_h - win_h) / 2) - 30)
        self.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.resizable(False, False)
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

        if "--tray" in sys.argv or "--minimized" in sys.argv:
            self.withdraw()

    def setup_ui(self):
        # 1. HEADER (Compact, Modern, Brand)
        header = tk.Frame(self, bg=BG_HEADER, height=65)
        header.pack(fill="x")
        header.pack_propagate(False)

        h_inner = tk.Frame(header, bg=BG_HEADER)
        h_inner.pack(fill="both", expand=True, padx=16)

        # Right side: Logo + Title
        brand_frame = tk.Frame(h_inner, bg=BG_HEADER)
        brand_frame.pack(side="right", fill="y")

        if os.path.exists(ICON_PNG):
            try:
                pil = Image.open(ICON_PNG).resize((40, 40), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(pil)
                logo_lbl = tk.Label(brand_frame, image=self.logo_img, bg=BG_HEADER)
                logo_lbl.pack(side="right", padx=(10, 0))
            except Exception:
                pass

        title_box = tk.Frame(brand_frame, bg=BG_HEADER)
        title_box.pack(side="right", fill="y")

        t_row = tk.Frame(title_box, bg=BG_HEADER)
        t_row.pack(anchor="e", pady=(8, 0))

        v_badge = tk.Label(
            t_row, text="v3.7", font=(FONT_NAME, 8, "bold"),
            bg="#21262d", fg=ACCENT_CYAN, padx=5, pady=1
        )
        v_badge.pack(side="left", padx=(0, 6))

        t_lbl = tk.Label(
            t_row, text="PersianFixer", font=(FONT_NAME, 13, "bold"),
            bg=BG_HEADER, fg=TEXT_WHITE
        )
        t_lbl.pack(side="left")

        sub_lbl = tk.Label(
            title_box, text="دستیار فارسی و فونت وزیرمتن برای ابزارهای هوش مصنوعی",
            font=(FONT_NAME, 8), bg=BG_HEADER, fg=TEXT_MUTED
        )
        sub_lbl.pack(anchor="e")

        # Left side: Quick reload button
        btn_reload = tk.Button(
            h_inner, text="بروزرسانی وضعیت ⟳", font=(FONT_NAME, 8),
            bg="#21262d", fg=TEXT_MUTED, activebackground="#30363d", activeforeground=TEXT_WHITE,
            relief="flat", cursor="hand2", padx=8, pady=3,
            command=self.refresh_statuses
        )
        btn_reload.pack(side="left", pady=16)

        # 2. MASTER STATUS PILL (Full Width Glowing Banner)
        self.master_box = tk.Frame(self, bg=STATUS_OK_BG, highlightbackground=STATUS_OK_BORDER, highlightthickness=1)
        self.master_box.pack(fill="x", padx=16, pady=(12, 6))

        m_inner = tk.Frame(self.master_box, bg=STATUS_OK_BG)
        m_inner.pack(fill="x", padx=12, pady=8)

        self.master_title = tk.Label(
            m_inner, text="● در حال بررسی وضعیت ابزارها...",
            font=(FONT_NAME, 9, "bold"), bg=STATUS_OK_BG, fg=STATUS_OK_TEXT
        )
        self.master_title.pack(anchor="e")

        self.master_desc = tk.Label(
            m_inner, text="لطفاً شکیبا باشید...",
            font=(FONT_NAME, 8), bg=STATUS_OK_BG, fg=TEXT_MUTED
        )
        self.master_desc.pack(anchor="e")

        # 3. MASTER 1-CLICK ACTION BUTTON (Full Width)
        btn_master = tk.Button(
            self, text="⚡  فعال‌سازی هوشمند تمام ابزارها (۱ کلیک)",
            font=(FONT_NAME, 10, "bold"), bg=ACCENT_BLUE, fg="white",
            activebackground=ACCENT_BLUE_HOVER, activeforeground="white",
            relief="flat", cursor="hand2", pady=8,
            command=self.action_patch_all
        )
        btn_master.pack(fill="x", padx=16, pady=(2, 10))

        # 4. APP ROWS (Compact, Clean, Unified List)
        cards_container = tk.Frame(self, bg=BG_MAIN)
        cards_container.pack(fill="x", padx=16)

        # Row 1: Vazirmatn Font
        self.row_font = self.create_app_row(
            cards_container,
            app_id="font",
            icon_char="🔤",
            name="فونت رسمی گوگل وزیرمتن",
            subtitle="نصب مستقیم وزن‌های ۱۰۰ تا ۹۰۰ در سیستم ویندوز",
            on_patch=self.action_install_font,
            patch_btn_text="نصب مجدد",
            on_run=None
        )

        # Row 2: Antigravity
        self.row_ag = self.create_app_row(
            cards_container,
            app_id="antigravity",
            icon_char="⚡",
            name="Google Antigravity",
            subtitle="ادیتور و چت کدنویسی پیشرفته",
            on_patch=lambda: self.action_patch_app("antigravity"),
            patch_btn_text="پچ",
            on_run=lambda: self.action_launch_app("antigravity"),
            on_restore=lambda: self.action_restore_app("antigravity")
        )

        # Row 3: Claude Desktop
        self.row_claude = self.create_app_row(
            cards_container,
            app_id="claude",
            icon_char="💬",
            name="Claude Desktop",
            subtitle="کلاینت رسمی کلاد برای ویندوز",
            on_patch=lambda: self.action_patch_app("claude"),
            patch_btn_text="پچ",
            on_run=lambda: self.action_launch_app("claude"),
            on_restore=lambda: self.action_restore_app("claude")
        )

        # Row 4: OpenCode
        self.row_opencode = self.create_app_row(
            cards_container,
            app_id="opencode",
            icon_char="💻",
            name="OpenCode",
            subtitle="دستیار برنامه‌نویسی هوش مصنوعی",
            on_patch=lambda: self.action_patch_app("opencode"),
            patch_btn_text="پچ",
            on_run=lambda: self.action_launch_app("opencode"),
            on_restore=lambda: self.action_restore_app("opencode")
        )

        # Row 5: ChatGPT (OpenAI Codex)
        self.row_chatgpt = self.create_app_row(
            cards_container,
            app_id="chatgpt",
            icon_char="🤖",
            name="ChatGPT (Codex)",
            subtitle="کلاینت رسمی ویندوز چت‌جی‌پی‌تی",
            on_patch=lambda: self.action_patch_app("chatgpt"),
            patch_btn_text="پچ",
            on_run=lambda: self.action_launch_app("chatgpt"),
            on_restore=lambda: self.action_restore_app("chatgpt")
        )

        # 5. COMPACT LOG BOX (Clean Terminal Window)
        log_frame = tk.Frame(self, bg=BG_MAIN)
        log_frame.pack(fill="both", expand=True, padx=16, pady=(10, 8))

        log_top = tk.Frame(log_frame, bg=BG_MAIN)
        log_top.pack(fill="x", pady=(0, 3))

        lbl_log_title = tk.Label(
            log_top, text="گزارش لحظه‌ای عملیات (Log):",
            font=(FONT_NAME, 8, "bold"), bg=BG_MAIN, fg=TEXT_MUTED
        )
        lbl_log_title.pack(side="right")

        btn_clear = tk.Label(
            log_top, text="پاکسازی", font=(FONT_NAME, 7),
            bg=BG_MAIN, fg=TEXT_DIM, cursor="hand2"
        )
        btn_clear.pack(side="left")
        btn_clear.bind("<Button-1>", lambda e: self.clear_log())

        log_box = tk.Frame(log_frame, bg="#07090e", highlightbackground=BORDER_SUBTLE, highlightthickness=1)
        log_box.pack(fill="both", expand=True)

        self.log_text = tk.Text(
            log_box, height=4, bg="#07090e", fg="#cbd5e1",
            font=(FONT_NAME, 8), relief="flat", padx=8, pady=6,
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True)

        # RTL tag with proper Unicode Right-to-Left formatting
        self.log_text.tag_configure("rtl_ok", justify="right", foreground=STATUS_OK_TEXT)
        self.log_text.tag_configure("rtl_info", justify="right", foreground=ACCENT_CYAN)
        self.log_text.tag_configure("rtl_warn", justify="right", foreground=STATUS_WARN_TEXT)
        self.log_text.tag_configure("rtl_err", justify="right", foreground=STATUS_ERR_TEXT)

        # Bottom controls (Autostart toggle + Tray note)
        bottom_frame = tk.Frame(self, bg=BG_MAIN)
        bottom_frame.pack(side="bottom", fill="x", padx=16, pady=(0, 6))

        self.autostart_var = tk.BooleanVar(value=autostart.is_autostart_enabled())
        chk_autostart = tk.Checkbutton(
            bottom_frame,
            text="اجرای خودکار همراه با روشن شدن ویندوز (Startup)",
            variable=self.autostart_var,
            command=self.on_toggle_autostart_gui,
            font=(FONT_NAME, 8),
            bg=BG_MAIN,
            fg=TEXT_MUTED,
            selectcolor="#161b22",
            activebackground=BG_MAIN,
            activeforeground=TEXT_WHITE,
            cursor="hand2"
        )
        chk_autostart.pack(side="right")

        footer = tk.Label(
            bottom_frame, text="• با بستن پنجره، برنامه در System Tray فعال می‌ماند",
            font=(FONT_NAME, 7), bg=BG_MAIN, fg=TEXT_DIM
        )
        footer.pack(side="left")

        self.log("سیستم با موفقیت آماده به کار شد.", "rtl_info")

    def create_app_row(self, parent, app_id, icon_char, name, subtitle, on_patch, patch_btn_text, on_run=None, on_restore=None):
        row = tk.Frame(parent, bg=BG_CARD, highlightbackground=BORDER_SUBTLE, highlightthickness=1)
        row.pack(fill="x", pady=2)

        inner = tk.Frame(row, bg=BG_CARD)
        inner.pack(fill="x", padx=10, pady=5)

        # Left side: Action Buttons (Patch, Run, Restore)
        btn_box = tk.Frame(inner, bg=BG_CARD)
        btn_box.pack(side="left")

        if on_run:
            b_run = tk.Button(
                btn_box, text="اجرا ↗", font=(FONT_NAME, 8),
                bg=BTN_DARK, fg=TEXT_WHITE, activebackground=BTN_DARK_HOVER, activeforeground="white",
                relief="flat", cursor="hand2", padx=8, pady=2,
                command=on_run
            )
            b_run.pack(side="left", padx=(0, 4))
        else:
            b_run = None

        if on_restore:
            b_restore = tk.Button(
                btn_box, text="بازگردانی", font=(FONT_NAME, 7),
                bg=BG_CARD, fg=TEXT_DIM, activebackground=BTN_DARK, activeforeground=TEXT_MUTED,
                relief="flat", cursor="hand2", padx=4, pady=2,
                command=on_restore
            )
            b_restore.pack(side="left", padx=(0, 4))
        else:
            b_restore = None

        b_patch = tk.Button(
            btn_box, text=patch_btn_text, font=(FONT_NAME, 8, "bold"),
            bg=BTN_PRIMARY, fg="white", activebackground=BTN_PRIMARY_HOVER, activeforeground="white",
            relief="flat", cursor="hand2", padx=8, pady=2,
            command=on_patch
        )
        b_patch.pack(side="left")

        # Right side: App details & Status
        info_box = tk.Frame(inner, bg=BG_CARD)
        info_box.pack(side="right", fill="y")

        top_line = tk.Frame(info_box, bg=BG_CARD)
        top_line.pack(anchor="e")

        # Status badge (pill)
        status_badge = tk.Label(
            top_line, text="بررسی...", font=(FONT_NAME, 7, "bold"),
            bg="#21262d", fg=TEXT_MUTED, padx=5, pady=0
        )
        status_badge.pack(side="left", padx=(0, 8))

        name_lbl = tk.Label(
            top_line, text=name, font=(FONT_NAME, 9, "bold"),
            bg=BG_CARD, fg=TEXT_WHITE
        )
        name_lbl.pack(side="left")

        icon_lbl = tk.Label(
            top_line, text=icon_char, font=(FONT_NAME, 9),
            bg=BG_CARD, fg=TEXT_MUTED
        )
        icon_lbl.pack(side="left", padx=(4, 0))

        sub_line = tk.Label(
            info_box, text=subtitle, font=(FONT_NAME, 7),
            bg=BG_CARD, fg=TEXT_DIM
        )
        sub_line.pack(anchor="e")

        return {
            "frame": row,
            "badge": status_badge,
            "btn_patch": b_patch,
            "btn_run": b_run,
            "btn_restore": b_restore
        }

    def log(self, text, tag="rtl_info"):
        now_str = datetime.now().strftime("%H:%M:%S")
        # Prepend Right-To-Left Mark (\u200F) so punctuation and timestamps flow naturally
        clean_text = f"\u200F[{now_str}]  {text}\n"
        self.log_text.insert("end", clean_text, tag)
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
                    self.row_font["badge"].config(text="✓ فعال", bg="#0d2818", fg=STATUS_OK_TEXT)
                    self.row_font["btn_patch"].config(text="نصب مجدد", bg=BTN_DARK)
                else:
                    self.row_font["badge"].config(text="نیاز به نصب", bg=STATUS_WARN_BG, fg=STATUS_WARN_TEXT)
                    self.row_font["btn_patch"].config(text="نصب فونت", bg=BTN_PRIMARY)

                # 2. Antigravity
                if not ag_st["installed"]:
                    self.row_ag["badge"].config(text="یافت نشد", bg="#21262d", fg=TEXT_DIM)
                    self.row_ag["btn_patch"].config(state="disabled")
                    if self.row_ag["btn_run"]: self.row_ag["btn_run"].config(state="disabled")
                elif ag_st["patched"]:
                    run_t = " • در حال اجرا" if ag_st["running"] else ""
                    self.row_ag["badge"].config(text=f"✓ پچ فعال{run_t}", bg="#0d2818", fg=STATUS_OK_TEXT)
                    self.row_ag["btn_patch"].config(text="بروزرسانی", state="normal", bg=BTN_DARK)
                    if self.row_ag["btn_run"]: self.row_ag["btn_run"].config(state="normal")
                else:
                    self.row_ag["badge"].config(text="آماده پچ", bg=STATUS_WARN_BG, fg=STATUS_WARN_TEXT)
                    self.row_ag["btn_patch"].config(text="پچ", state="normal", bg=BTN_PRIMARY)
                    if self.row_ag["btn_run"]: self.row_ag["btn_run"].config(state="normal")

                # 3. Claude
                if not cl_st["installed"]:
                    self.row_claude["badge"].config(text="یافت نشد", bg="#21262d", fg=TEXT_DIM)
                    self.row_claude["btn_patch"].config(state="disabled")
                    if self.row_claude["btn_run"]: self.row_claude["btn_run"].config(state="disabled")
                elif cl_st["patched"]:
                    run_t = " • در حال اجرا" if cl_st["running"] else ""
                    self.row_claude["badge"].config(text=f"✓ پچ فعال{run_t}", bg="#0d2818", fg=STATUS_OK_TEXT)
                    self.row_claude["btn_patch"].config(text="بروزرسانی", state="normal", bg=BTN_DARK)
                    if self.row_claude["btn_run"]: self.row_claude["btn_run"].config(state="normal")
                else:
                    self.row_claude["badge"].config(text="آماده پچ", bg=STATUS_WARN_BG, fg=STATUS_WARN_TEXT)
                    self.row_claude["btn_patch"].config(text="پچ", state="normal", bg=BTN_PRIMARY)
                    if self.row_claude["btn_run"]: self.row_claude["btn_run"].config(state="normal")

                # 4. OpenCode
                if not op_st["installed"]:
                    self.row_opencode["badge"].config(text="یافت نشد", bg="#21262d", fg=TEXT_DIM)
                    self.row_opencode["btn_patch"].config(state="disabled")
                    if self.row_opencode["btn_run"]: self.row_opencode["btn_run"].config(state="disabled")
                elif op_st["patched"]:
                    run_t = " • در حال اجرا" if op_st["running"] else ""
                    self.row_opencode["badge"].config(text=f"✓ پچ فعال{run_t}", bg="#0d2818", fg=STATUS_OK_TEXT)
                    self.row_opencode["btn_patch"].config(text="بروزرسانی", state="normal", bg=BTN_DARK)
                    if self.row_opencode["btn_run"]: self.row_opencode["btn_run"].config(state="normal")
                else:
                    self.row_opencode["badge"].config(text="آماده پچ", bg=STATUS_WARN_BG, fg=STATUS_WARN_TEXT)
                    self.row_opencode["btn_patch"].config(text="پچ", state="normal", bg=BTN_PRIMARY)
                    if self.row_opencode["btn_run"]: self.row_opencode["btn_run"].config(state="normal")

                # 5. ChatGPT
                if not cg_st["installed"]:
                    self.row_chatgpt["badge"].config(text="یافت نشد", bg="#21262d", fg=TEXT_DIM)
                    self.row_chatgpt["btn_patch"].config(state="disabled")
                    if self.row_chatgpt["btn_run"]: self.row_chatgpt["btn_run"].config(state="disabled")
                elif cg_st["patched"]:
                    run_t = " • در حال اجرا" if cg_st["running"] else ""
                    self.row_chatgpt["badge"].config(text=f"✓ پچ فعال{run_t}", bg="#0d2818", fg=STATUS_OK_TEXT)
                    self.row_chatgpt["btn_patch"].config(text="بروزرسانی", state="normal", bg=BTN_DARK)
                    if self.row_chatgpt["btn_run"]: self.row_chatgpt["btn_run"].config(state="normal")
                else:
                    self.row_chatgpt["badge"].config(text="آماده پچ", bg=STATUS_WARN_BG, fg=STATUS_WARN_TEXT)
                    self.row_chatgpt["btn_patch"].config(text="پچ", state="normal", bg=BTN_PRIMARY)
                    if self.row_chatgpt["btn_run"]: self.row_chatgpt["btn_run"].config(state="normal")

                # Master Status
                installed = [ag_st["installed"], cl_st["installed"], op_st["installed"], cg_st["installed"]]
                patched = [ag_st["patched"], cl_st["patched"], op_st["patched"], cg_st["patched"]]
                tot_i = sum(1 for x in installed if x)
                tot_p = sum(1 for x in patched if x)

                if tot_i > 0 and tot_p == tot_i and font_installed:
                    self.master_box.config(bg=STATUS_OK_BG, highlightbackground=STATUS_OK_BORDER)
                    self.master_title.config(
                        text=f"🟢  وضعیت سیستم: کاملاً فعال است ({tot_p} از {tot_i} ابزار مجهز به وزیرمتن و راست‌چین هستند)",
                        bg=STATUS_OK_BG, fg=STATUS_OK_TEXT
                    )
                    self.master_desc.config(
                        text="پشتیبانی از زبان فارسی روی تمامی برنامه‌های شناسایی‌شده در ویندوز فعال می‌باشد.",
                        bg=STATUS_OK_BG, fg="#7ee787"
                    )
                else:
                    self.master_box.config(bg=STATUS_WARN_BG, highlightbackground=STATUS_WARN_BORDER)
                    self.master_title.config(
                        text=f"🟡  وضعیت سیستم: نیاز به فعال‌سازی ({tot_p} از {tot_i} ابزار فعال شده‌اند)",
                        bg=STATUS_WARN_BG, fg=STATUS_WARN_TEXT
                    )
                    self.master_desc.config(
                        text="برای فعال‌سازی کامل، روی دکمه آبی‌رنگ «فعال‌سازی هوشمند تمام ابزارها» کلیک کنید.",
                        bg=STATUS_WARN_BG, fg="#e3b341"
                    )

            self.after(0, update)

        threading.Thread(target=worker, daemon=True).start()

    def action_install_font(self):
        self.log("در حال ثبت فونت وزیرمتن در رجیستری ویندوز...", "rtl_info")
        ok = font_installer.install_vazirmatn_font()
        if ok:
            self.log("فونت رسمی گوگل وزیرمتن با موفقیت ثبت شد. ✓", "rtl_ok")
        else:
            self.log("خطا در ثبت فونت در ویندوز. ✖", "rtl_err")
        self.refresh_statuses()

    def action_patch_all(self):
        def worker():
            self.log("عملیات ۱-کلیک: شروع پچ همه‌جانبه تمام برنامه‌ها...", "rtl_info")
            font_installer.install_vazirmatn_font()

            # Antigravity
            ag = patcher.get_antigravity_status()
            if ag["installed"]:
                ok, msg = patcher.patch_antigravity(auto_close=True)
                self.log(f"برنامه Antigravity: {msg}", "rtl_ok" if ok else "rtl_err")

            # Claude
            cl = patcher.get_claude_status()
            if cl["installed"]:
                ok, msg = patcher.patch_claude(auto_close=True)
                self.log(f"برنامه Claude: {msg}", "rtl_ok" if ok else "rtl_err")

            # OpenCode
            op = patcher.get_opencode_status()
            if op["installed"]:
                ok, msg = patcher.patch_opencode(auto_close=True)
                self.log(f"برنامه OpenCode: {msg}", "rtl_ok" if ok else "rtl_err")

            # ChatGPT
            cg = patcher.get_chatgpt_status()
            if cg["installed"]:
                ok, msg = patcher.patch_chatgpt(auto_close=True)
                self.log(f"برنامه ChatGPT: {msg}", "rtl_ok" if ok else "rtl_err")

            self.log("تمامی ابزارهای شناسایی‌شده با موفقیت پچ و فعال گردیدند. ✓", "rtl_ok")
            self.refresh_statuses()

        threading.Thread(target=worker, daemon=True).start()

    def action_patch_app(self, app_name):
        def worker():
            names_fa = {"antigravity": "Antigravity", "claude": "Claude", "opencode": "OpenCode", "chatgpt": "ChatGPT"}
            fa = names_fa.get(app_name, app_name)
            self.log(f"در حال اعمال پچ فارسی روی {fa}...", "rtl_info")
            
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

            self.log(f"{fa}: {msg}", "rtl_ok" if ok else "rtl_err")
            self.refresh_statuses()

        threading.Thread(target=worker, daemon=True).start()

    def action_restore_app(self, app_name):
        def worker():
            names_fa = {"antigravity": "Antigravity", "claude": "Claude", "opencode": "OpenCode", "chatgpt": "ChatGPT"}
            fa = names_fa.get(app_name, app_name)
            self.log(f"در حال بازگردانی {fa} به فایل اصلی...", "rtl_info")

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

            self.log(f"بازگردانی {fa}: {msg}", "rtl_info" if ok else "rtl_err")
            self.refresh_statuses()

        threading.Thread(target=worker, daemon=True).start()

    def action_launch_app(self, app_name):
        names_fa = {"antigravity": "Antigravity", "claude": "Claude", "opencode": "OpenCode", "chatgpt": "ChatGPT"}
        fa = names_fa.get(app_name, app_name)
        
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

        self.log(f"اجرای {fa}: {msg}", "rtl_info" if ok else "rtl_err")

    def setup_tray(self):
        try:
            if os.path.exists(ICON_PNG):
                tray_image = Image.open(ICON_PNG).resize((64, 64), Image.Resampling.LANCZOS)
            else:
                tray_image = Image.new('RGB', (64, 64), color=(0, 122, 204))

            menu = pystray.Menu(
                item('نمایش پنجره PersianFixer', self.restore_from_tray, default=True),
                pystray.Menu.SEPARATOR,
                item('اجرا همراه با ویندوز', self.toggle_autostart_tray, checked=lambda item: autostart.is_autostart_enabled()),
                pystray.Menu.SEPARATOR,
                item('اجرای Antigravity', lambda: patcher.launch_antigravity()),
                item('اجرای Claude', lambda: patcher.launch_claude()),
                item('اجرای OpenCode', lambda: patcher.launch_opencode()),
                item('اجرای ChatGPT', lambda: patcher.launch_chatgpt()),
                pystray.Menu.SEPARATOR,
                item('فعال‌سازی همه برنامه‌ها', lambda: self.action_patch_all()),
                item('خروج کامل', self.quit_app)
            )

            self.tray_icon = pystray.Icon("PersianFixer", tray_image, "PersianFixer (راست‌چین و فونت وزیرمتن)", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception as e:
            pass

    def on_toggle_autostart_gui(self):
        val = self.autostart_var.get()
        ok, msg = autostart.set_autostart(val)
        self.log(msg, "rtl_ok" if ok else "rtl_err")

    def toggle_autostart_tray(self, icon=None, item=None):
        current = autostart.is_autostart_enabled()
        new_val = not current
        ok, msg = autostart.set_autostart(new_val)
        if hasattr(self, "autostart_var"):
            self.autostart_var.set(new_val)
        self.log(msg, "rtl_ok" if ok else "rtl_err")

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