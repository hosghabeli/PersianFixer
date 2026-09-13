import os
import sys
import shutil
import subprocess
import time

ANTIGRAVITY_DIR = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "antigravity")
ANTIGRAVITY_EXE = os.path.join(ANTIGRAVITY_DIR, "Antigravity.exe")
ANTIGRAVITY_RESOURCES = os.path.join(ANTIGRAVITY_DIR, "resources")
ANTIGRAVITY_ASAR = os.path.join(ANTIGRAVITY_RESOURCES, "app.asar")
ANTIGRAVITY_PATCHED = os.path.join(ANTIGRAVITY_RESOURCES, "app.asar.patched")
ANTIGRAVITY_BAK = os.path.join(ANTIGRAVITY_RESOURCES, "app.asar.bak")

CLAUDE_SOURCE_DIR = r"C:\Program Files\WindowsApps\Claude_1.40609.0.0_x64__pzs8sxrjxfjjc\app"
CLAUDE_SOURCE_ASAR = os.path.join(CLAUDE_SOURCE_DIR, "resources", "app.asar")
CLAUDE_TARGET_DIR = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Claude-Persian")
CLAUDE_TARGET_EXE = os.path.join(CLAUDE_TARGET_DIR, "claude.exe")
CLAUDE_TARGET_ASAR = os.path.join(CLAUDE_TARGET_DIR, "resources", "app.asar")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_JS_PATH = os.path.join(SCRIPT_DIR, "persian_engine.js")
ASAR_PATCHER_JS = os.path.join(SCRIPT_DIR, "asar_patcher.js")

def is_process_running(proc_name):
    """Checks if a process name is currently running."""
    try:
        output = subprocess.check_output(
            ["tasklist", "/FI", f"IMAGENAME eq {proc_name}"],
            creationflags=subprocess.CREATE_NO_WINDOW
        ).decode("latin1", errors="ignore")
        return proc_name.lower() in output.lower()
    except Exception:
        return False

def close_process(proc_name):
    """Gracefully terminates processes with given name."""
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", proc_name],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        time.sleep(1.0)
        return True
    except Exception:
        return False

def get_antigravity_status():
    """Returns status dict for Antigravity."""
    if not os.path.exists(ANTIGRAVITY_ASAR):
        return {"installed": False, "patched": False, "backup": False, "running": False}

    running = is_process_running("Antigravity.exe")
    has_backup = os.path.exists(ANTIGRAVITY_BAK)

    patched = False
    try:
        res = subprocess.check_output(
            ["node", ASAR_PATCHER_JS, "check", ANTIGRAVITY_ASAR, "dist/preload.js"],
            cwd=SCRIPT_DIR,
            creationflags=subprocess.CREATE_NO_WINDOW
        ).decode().strip()
        patched = (res == "PATCHED")
    except Exception:
        pass

    return {
        "installed": True,
        "patched": patched,
        "backup": has_backup,
        "running": running
    }

def patch_antigravity(auto_close=False):
    """Patches Antigravity using fast prebuilt swap or live build."""
    if not os.path.exists(ANTIGRAVITY_ASAR):
        return False, "مسیر فایل‌های Antigravity یافت نشد."

    if is_process_running("Antigravity.exe"):
        if auto_close:
            close_process("Antigravity.exe")
        else:
            return False, "برنامه Antigravity هم‌اکنون باز است. لطفاً آن را ببندید تا فایل‌ها قابل تغییر باشند."

    # Backup if needed
    if not os.path.exists(ANTIGRAVITY_BAK):
        try:
            shutil.copy2(ANTIGRAVITY_ASAR, ANTIGRAVITY_BAK)
        except Exception as e:
            return False, f"خطا در ایجاد فایل پشتیبان: {e}"

    # Fast swap if prebuilt exists
    if os.path.exists(ANTIGRAVITY_PATCHED):
        try:
            shutil.copy2(ANTIGRAVITY_PATCHED, ANTIGRAVITY_ASAR)
            return True, "برنامه Antigravity با موفقیت پچ شد (پشتیبانی فونت وزیرمتن و راست‌چین فعال گردید)."
        except Exception as e:
            return False, f"خطا در جایگزینی فایل پچ‌شده: {e}"

    try:
        proc = subprocess.run(
            ["node", ASAR_PATCHER_JS, "patch", ANTIGRAVITY_ASAR, ANTIGRAVITY_ASAR, "dist/preload.js", ENGINE_JS_PATH],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if proc.returncode == 0 and "SUCCESS" in proc.stdout:
            return True, "برنامه Antigravity با موفقیت پچ شد (پشتیبانی فونت وزیرمتن و راست‌چین فعال گردید)."
        else:
            return False, f"خطا در پچ کردن Antigravity: {proc.stderr or proc.stdout}"
    except Exception as e:
        return False, f"خطا در اجرای اسکریپت پچ: {e}"

def restore_antigravity(auto_close=False):
    """Restores Antigravity app.asar from app.asar.bak."""
    if not os.path.exists(ANTIGRAVITY_BAK):
        return False, "فایل پشتیبان (app.asar.bak) یافت نشد."

    if is_process_running("Antigravity.exe"):
        if auto_close:
            close_process("Antigravity.exe")
        else:
            return False, "برنامه Antigravity باز است. لطفاً آن را ببندید."

    try:
        shutil.copy2(ANTIGRAVITY_BAK, ANTIGRAVITY_ASAR)
        return True, "برنامه Antigravity به نسخه اصلی اولیه بازگردانده شد."
    except Exception as e:
        return False, f"خطا در بازگردانی: {e}"

def get_claude_status():
    """Returns status dict for Claude."""
    installed = os.path.exists(CLAUDE_SOURCE_DIR)
    target_exists = os.path.exists(CLAUDE_TARGET_ASAR)
    running = is_process_running("claude.exe")

    patched = False
    if target_exists:
        try:
            res = subprocess.check_output(
                ["node", ASAR_PATCHER_JS, "check", CLAUDE_TARGET_ASAR, ".vite/build/mainView.js"],
                cwd=SCRIPT_DIR,
                creationflags=subprocess.CREATE_NO_WINDOW
            ).decode().strip()
            patched = (res == "PATCHED")
        except Exception:
            pass

    return {
        "installed": installed,
        "target_exists": target_exists,
        "patched": patched,
        "running": running
    }

def create_desktop_shortcut(target_exe, shortcut_name, description):
    desktop = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
    shortcut_path = os.path.join(desktop, shortcut_name)

    ps_cmd = f"""
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
    $Shortcut.TargetPath = '{target_exe}'
    $Shortcut.WorkingDirectory = '{os.path.dirname(target_exe)}'
    $Shortcut.Description = '{description}'
    $Shortcut.IconLocation = '{target_exe},0'
    $Shortcut.Save()
    """
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_cmd],
        creationflags=subprocess.CREATE_NO_WINDOW
    )

def patch_claude():
    if not os.path.exists(CLAUDE_SOURCE_DIR):
        return False, "برنامه رسمی Claude در ویندوز یافت نشد."

    if is_process_running("claude.exe"):
        close_process("claude.exe")

    os.makedirs(CLAUDE_TARGET_DIR, exist_ok=True)

    if not os.path.exists(CLAUDE_TARGET_EXE):
        subprocess.run(
            ["robocopy", CLAUDE_SOURCE_DIR, CLAUDE_TARGET_DIR, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/nc", "/ns", "/np"],
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

    try:
        proc = subprocess.run(
            ["node", ASAR_PATCHER_JS, "patch", CLAUDE_SOURCE_ASAR, CLAUDE_TARGET_ASAR, ".vite/build/mainView.js", ENGINE_JS_PATH, CLAUDE_TARGET_EXE],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if proc.returncode == 0 and "SUCCESS" in proc.stdout:
            create_desktop_shortcut(
                CLAUDE_TARGET_EXE,
                "Claude-Persian.lnk",
                "اجرای Claude Desktop با فونت وزیرمتن و راست‌چین فارسی"
            )
            return True, "برنامه Claude با موفقیت پچ شد و میانبر «Claude-Persian» روی دسکتاپ ایجاد شد."
        else:
            return False, f"خطا در پچ Claude: {proc.stderr or proc.stdout}"
    except Exception as e:
        return False, f"خطای سیستمی: {e}"

def launch_claude():
    if os.path.exists(CLAUDE_TARGET_EXE):
        subprocess.Popen([CLAUDE_TARGET_EXE], cwd=CLAUDE_TARGET_DIR)
        return True, "برنامه Claude اجرا شد."
    return False, "برنامه Claude یافت نشد."

def launch_antigravity():
    if os.path.exists(ANTIGRAVITY_EXE):
        subprocess.Popen([ANTIGRAVITY_EXE], cwd=ANTIGRAVITY_DIR)
        return True, "برنامه Antigravity اجرا شد."
    return False, "فایل Antigravity.exe یافت نشد."