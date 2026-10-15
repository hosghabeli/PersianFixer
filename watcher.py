import os
import time
import threading
import patcher
import font_installer
import config

class AutoPatchWatcher:
    """
    Background worker that monitors installed AI apps and automatically
    applies PersianFixer patches and Vazirmatn font when an app is updated.
    """
    def __init__(self, app=None, tray_icon=None, on_status_change=None):
        self.app = app
        self.tray_icon = tray_icon
        self.on_status_change = on_status_change
        self.running = False
        self.thread = None
        self.pending_apps = set()
        self._lock = threading.Lock()

    def set_tray_icon(self, tray_icon):
        self.tray_icon = tray_icon

    def log(self, text, tag="rtl_info"):
        if self.app and hasattr(self.app, "log"):
            try:
                self.app.after(0, lambda: self.app.log(text, tag))
            except Exception:
                pass

    def notify(self, title, message):
        if not config.get_setting("notify", True):
            return
        if self.tray_icon and hasattr(self.tray_icon, "notify"):
            try:
                self.tray_icon.notify(message, f"PersianFixer: {title}")
                return
            except Exception:
                pass

    def start(self):
        with self._lock:
            if self.running:
                return
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()

    def stop(self):
        with self._lock:
            self.running = False

    def trigger_check(self):
        """Manually trigger one check cycle in a background thread."""
        threading.Thread(target=self.check_and_patch_once, daemon=True).start()

    def check_and_patch_once(self):
        """Checks all tools and applies patches silently if unpatched and not running."""
        # 1. Check Font
        try:
            if not font_installer.is_font_installed():
                if font_installer.install_vazirmatn_font():
                    self.log("دیده‌بان خودکار: فونت رسمی وزیرمتن با موفقیت در ویندوز نصب شد. ✓", "rtl_ok")
                    self.notify("فونت وزیرمتن", "فونت رسمی گوگل وزیرمتن با موفقیت ثبت و نصب گردید.")
        except Exception:
            pass

        # 2. Check all AI apps
        apps = [
            ("antigravity", "Google Antigravity", patcher.get_antigravity_status, patcher.patch_antigravity),
            ("claude", "Claude Desktop", patcher.get_claude_status, patcher.patch_claude),
            ("opencode", "OpenCode", patcher.get_opencode_status, patcher.patch_opencode),
            ("chatgpt", "ChatGPT (Codex)", patcher.get_chatgpt_status, patcher.patch_chatgpt),
            ("vscode", "Visual Studio Code", patcher.get_vscode_status, patcher.patch_vscode),
        ]

        any_patched = False

        for app_id, name, get_status_fn, patch_fn in apps:
            try:
                st = get_status_fn()
                if not st.get("installed", False):
                    self.pending_apps.discard(app_id)
                    continue

                if not st.get("patched", False):
                    # App is installed but not patched (e.g. after vendor update)
                    if st.get("running", False):
                        if app_id not in self.pending_apps:
                            self.pending_apps.add(app_id)
                            self.log(f"دیده‌بان خودکار: {name} به‌روزرسانی شده و به محض بسته شدن، پچ اعمال خواهد شد.", "rtl_warn")
                            self.notify(name, f"برنامه به‌روزرسانی شده است؛ پچ فارسی پس از بسته شدن برنامه به صورت خودکار اعمال خواهد شد.")
                    else:
                        # App is NOT running -> Apply silent patch immediately!
                        ok, msg = patch_fn(auto_close=False)
                        if ok:
                            self.pending_apps.discard(app_id)
                            any_patched = True
                            self.log(f"دیده‌بان خودکار: پچ فارسی {name} با موفقیت اعمال شد. ✓", "rtl_ok")
                            self.notify(name, f"پچ فارسی و فونت وزیرمتن با موفقیت به صورت خودکار اعمال گردید. ✓")
                        else:
                            self.log(f"دیده‌بان خودکار: تلاش برای پچ {name}: {msg}", "rtl_err")
                else:
                    # App is already patched
                    self.pending_apps.discard(app_id)
            except Exception:
                pass

        if any_patched and self.on_status_change:
            try:
                self.on_status_change()
            except Exception:
                pass

    def _run_loop(self):
        # Initial brief pause to allow application startup
        time.sleep(4)
        while self.running:
            try:
                if config.get_setting("auto_patch", True):
                    self.check_and_patch_once()
            except Exception:
                pass

            # Fast polling if apps are pending close, else standard interval
            interval = 10 if self.pending_apps else config.get_setting("check_interval", 45)
            for _ in range(int(interval)):
                if not self.running:
                    break
                time.sleep(1)
