import os
import sys
import shutil
import subprocess
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_JS_PATH = os.path.join(SCRIPT_DIR, "persian_engine.js")
ASAR_PATCHER_JS = os.path.join(SCRIPT_DIR, "asar_patcher.js")

# --- 1. ANTIGRAVITY PATHS ---
ANTIGRAVITY_DIR = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "antigravity")
ANTIGRAVITY_EXE = os.path.join(ANTIGRAVITY_DIR, "Antigravity.exe")
ANTIGRAVITY_RESOURCES = os.path.join(ANTIGRAVITY_DIR, "resources")
ANTIGRAVITY_ASAR = os.path.join(ANTIGRAVITY_RESOURCES, "app.asar")
ANTIGRAVITY_PATCHED = os.path.join(ANTIGRAVITY_RESOURCES, "app.asar.patched")
ANTIGRAVITY_BAK = os.path.join(ANTIGRAVITY_RESOURCES, "app.asar.bak")

# --- 2. CLAUDE PATHS ---
def find_claude_source_dir():
    local_app = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Claude")
    if os.path.exists(os.path.join(local_app, "claude.exe")):
        return local_app
    try:
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "(Get-AppxPackage -Name '*claude*').InstallLocation"],
            creationflags=subprocess.CREATE_NO_WINDOW
        ).decode().strip()
        if out:
            app_dir = os.path.join(out, "app")
            if os.path.exists(app_dir):
                return app_dir
            if os.path.exists(out):
                return out
    except Exception:
        pass
    hardcoded = r"C:\Program Files\WindowsApps\Claude_1.40609.0.0_x64__pzs8sxrjxfjjc\app"
    if os.path.exists(hardcoded):
        return hardcoded
    return ""

CLAUDE_SOURCE_DIR = find_claude_source_dir()
CLAUDE_SOURCE_ASAR = os.path.join(CLAUDE_SOURCE_DIR, "resources", "app.asar") if CLAUDE_SOURCE_DIR else ""
CLAUDE_TARGET_DIR = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Claude-Persian")
CLAUDE_TARGET_EXE = os.path.join(CLAUDE_TARGET_DIR, "claude.exe")
CLAUDE_TARGET_ASAR = os.path.join(CLAUDE_TARGET_DIR, "resources", "app.asar")

# --- 3. OPENCODE PATHS ---
OPENCODE_DIR = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "@opencode-aidesktop")
OPENCODE_EXE = os.path.join(OPENCODE_DIR, "OpenCode.exe")
OPENCODE_RESOURCES = os.path.join(OPENCODE_DIR, "resources")
OPENCODE_ASAR = os.path.join(OPENCODE_RESOURCES, "app.asar")
OPENCODE_BAK = os.path.join(OPENCODE_RESOURCES, "app.asar.bak")

# --- 4. CHATGPT (OPENAI CODEX) PATHS ---
def find_chatgpt_source_dir():
    local_app = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "ChatGPT")
    try:
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "(Get-AppxPackage -Name '*Codex*').InstallLocation"],
            creationflags=subprocess.CREATE_NO_WINDOW
        ).decode().strip()
        if out:
            app_dir = os.path.join(out, "app")
            if os.path.exists(app_dir):
                return app_dir
            if os.path.exists(out):
                return out
    except Exception:
        pass
    return ""

CHATGPT_SOURCE_DIR = find_chatgpt_source_dir()
CHATGPT_SOURCE_ASAR = os.path.join(CHATGPT_SOURCE_DIR, "resources", "app.asar") if CHATGPT_SOURCE_DIR else ""
CHATGPT_TARGET_DIR = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "ChatGPT")
CHATGPT_TARGET_EXE = os.path.join(CHATGPT_TARGET_DIR, "ChatGPT.exe")
CHATGPT_TARGET_ASAR = os.path.join(CHATGPT_TARGET_DIR, "resources", "app.asar")
CHATGPT_TARGET_BAK = os.path.join(CHATGPT_TARGET_DIR, "resources", "app.asar.bak")

# --- GENERAL UTILITIES ---
def is_process_running(proc_name):
    try:
        output = subprocess.check_output(
            ["tasklist", "/FI", f"IMAGENAME eq {proc_name}"],
            creationflags=subprocess.CREATE_NO_WINDOW
        ).decode("latin1", errors="ignore")
        return proc_name.lower() in output.lower()
    except Exception:
        return False

def close_process(proc_name):
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

def ensure_start_menu_shortcut(target_exe, shortcut_name, description):
    # Ensure no shortcut is placed on Desktop, and clean up any existing one
    desktop = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
    desktop_lnk = os.path.join(desktop, shortcut_name)
    if os.path.exists(desktop_lnk):
        try:
            os.remove(desktop_lnk)
        except Exception:
            pass

    start_menu = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs")
    start_lnk = os.path.join(start_menu, shortcut_name)

    ps_cmd = f"""
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut('{start_lnk}')
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

# --- 1. ANTIGRAVITY LOGIC ---
def get_antigravity_status():
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
    if not os.path.exists(ANTIGRAVITY_ASAR):
        return False, "مسیر فایل‌های Antigravity یافت نشد."

    if is_process_running("Antigravity.exe"):
        if auto_close:
            close_process("Antigravity.exe")
        else:
            return False, "برنامه Antigravity باز است. لطفاً آن را ببندید."

    if not os.path.exists(ANTIGRAVITY_BAK):
        try:
            shutil.copy2(ANTIGRAVITY_ASAR, ANTIGRAVITY_BAK)
        except Exception as e:
            return False, f"خطا در پشتیبان‌گیری: {e}"

    if os.path.exists(ANTIGRAVITY_PATCHED):
        try:
            shutil.copy2(ANTIGRAVITY_PATCHED, ANTIGRAVITY_ASAR)
            return True, "Antigravity با موفقیت پچ و فعال شد."
        except Exception as e:
            return False, f"خطا در جایگزینی فایل: {e}"

    try:
        proc = subprocess.run(
            ["node", ASAR_PATCHER_JS, "patch", ANTIGRAVITY_ASAR, ANTIGRAVITY_ASAR, "dist/preload.js", ENGINE_JS_PATH],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if proc.returncode == 0 and "SUCCESS" in proc.stdout:
            return True, "Antigravity با موفقیت پچ و فعال شد."
        return False, f"خطا در پچ: {proc.stderr or proc.stdout}"
    except Exception as e:
        return False, f"خطا در اجرا: {e}"

def restore_antigravity(auto_close=False):
    if not os.path.exists(ANTIGRAVITY_BAK):
        return False, "فایل پشتیبان یافت نشد."
    if is_process_running("Antigravity.exe"):
        if auto_close:
            close_process("Antigravity.exe")
        else:
            return False, "برنامه Antigravity باز است. لطفاً آن را ببندید."
    try:
        shutil.copy2(ANTIGRAVITY_BAK, ANTIGRAVITY_ASAR)
        return True, "Antigravity به نسخه اولیه بازگردانده شد."
    except Exception as e:
        return False, f"خطا در بازگردانی: {e}"

def launch_antigravity():
    if os.path.exists(ANTIGRAVITY_EXE):
        subprocess.Popen([ANTIGRAVITY_EXE], cwd=ANTIGRAVITY_DIR)
        return True, "برنامه Antigravity اجرا شد."
    return False, "فایل Antigravity.exe یافت نشد."

# --- 2. CLAUDE LOGIC ---
def get_claude_status():
    installed = bool(CLAUDE_SOURCE_DIR and os.path.exists(CLAUDE_SOURCE_DIR))
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

def patch_claude(auto_close=False):
    if not CLAUDE_SOURCE_DIR or not os.path.exists(CLAUDE_SOURCE_DIR):
        return False, "برنامه رسمی Claude در ویندوز یافت نشد."

    if is_process_running("claude.exe"):
        if auto_close:
            close_process("claude.exe")
        else:
            return False, "برنامه Claude باز است. لطفاً آن را ببندید."

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
            ensure_start_menu_shortcut(
                CLAUDE_TARGET_EXE,
                "Claude.lnk",
                "اجرای Claude Desktop با فونت وزیرمتن و راست‌چین فارسی"
            )
            return True, "برنامه Claude با موفقیت پچ شد."
        return False, f"خطا در پچ Claude: {proc.stderr or proc.stdout}"
    except Exception as e:
        return False, f"خطای سیستمی: {e}"

def restore_claude(auto_close=False):
    if not os.path.exists(CLAUDE_SOURCE_ASAR):
        return False, "نسخه اصلی Claude یافت نشد."
    if is_process_running("claude.exe"):
        if auto_close:
            close_process("claude.exe")
        else:
            return False, "برنامه Claude باز است. لطفاً آن را ببندید."
    try:
        shutil.copy2(CLAUDE_SOURCE_ASAR, CLAUDE_TARGET_ASAR)
        return True, "برنامه Claude به نسخه اولیه بازگردانده شد."
    except Exception as e:
        return False, f"خطا در بازگردانی Claude: {e}"

def launch_claude():
    if os.path.exists(CLAUDE_TARGET_EXE):
        subprocess.Popen([CLAUDE_TARGET_EXE], cwd=CLAUDE_TARGET_DIR)
        return True, "برنامه Claude اجرا شد."
    return False, "برنامه Claude یافت نشد."

# --- 3. OPENCODE LOGIC ---
def get_opencode_status():
    installed = os.path.exists(OPENCODE_ASAR)
    running = is_process_running("OpenCode.exe")
    has_backup = os.path.exists(OPENCODE_BAK)
    patched = False

    if installed:
        try:
            res = subprocess.check_output(
                ["node", ASAR_PATCHER_JS, "check", OPENCODE_ASAR, "out/preload/index.js"],
                cwd=SCRIPT_DIR,
                creationflags=subprocess.CREATE_NO_WINDOW
            ).decode().strip()
            patched = (res == "PATCHED")
        except Exception:
            pass

    return {
        "installed": installed,
        "patched": patched,
        "backup": has_backup,
        "running": running
    }

def patch_opencode(auto_close=False):
    if not os.path.exists(OPENCODE_ASAR):
        return False, "برنامه OpenCode در سیستم یافت نشد."

    if is_process_running("OpenCode.exe"):
        if auto_close:
            close_process("OpenCode.exe")
        else:
            return False, "برنامه OpenCode باز است. لطفاً آن را ببندید."

    if not os.path.exists(OPENCODE_BAK):
        try:
            shutil.copy2(OPENCODE_ASAR, OPENCODE_BAK)
        except Exception as e:
            return False, f"خطا در پشتیبان‌گیری: {e}"

    try:
        proc = subprocess.run(
            ["node", ASAR_PATCHER_JS, "patch", OPENCODE_ASAR, OPENCODE_ASAR, "out/preload/index.js", ENGINE_JS_PATH],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if proc.returncode == 0 and "SUCCESS" in proc.stdout:
            return True, "برنامه OpenCode با موفقیت پچ و مجهز به فونت وزیرمتن شد."
        return False, f"خطا در پچ OpenCode: {proc.stderr or proc.stdout}"
    except Exception as e:
        return False, f"خطای سیستمی: {e}"

def restore_opencode(auto_close=False):
    if not os.path.exists(OPENCODE_BAK):
        return False, "فایل پشتیبان OpenCode یافت نشد."
    if is_process_running("OpenCode.exe"):
        if auto_close:
            close_process("OpenCode.exe")
        else:
            return False, "برنامه OpenCode باز است. لطفاً آن را ببندید."
    try:
        shutil.copy2(OPENCODE_BAK, OPENCODE_ASAR)
        return True, "برنامه OpenCode به نسخه اولیه بازگردانده شد."
    except Exception as e:
        return False, f"خطا در بازگردانی OpenCode: {e}"

def launch_opencode():
    if os.path.exists(OPENCODE_EXE):
        subprocess.Popen([OPENCODE_EXE], cwd=OPENCODE_DIR)
        return True, "برنامه OpenCode اجرا شد."
    return False, "برنامه OpenCode یافت نشد."

# --- 4. CHATGPT (OPENAI CODEX) LOGIC ---
def get_chatgpt_status():
    installed = bool(CHATGPT_SOURCE_DIR and os.path.exists(CHATGPT_SOURCE_DIR))
    target_exists = os.path.exists(CHATGPT_TARGET_ASAR)
    running = is_process_running("ChatGPT.exe") or is_process_running("Codex.exe")
    patched = False

    if target_exists:
        try:
            res = subprocess.check_output(
                ["node", ASAR_PATCHER_JS, "check", CHATGPT_TARGET_ASAR, ".vite/build/preload.js"],
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

def patch_chatgpt(auto_close=False):
    if not CHATGPT_SOURCE_DIR or not os.path.exists(CHATGPT_SOURCE_DIR):
        return False, "برنامه رسمی ChatGPT (Codex) در ویندوز یافت نشد."

    if is_process_running("ChatGPT.exe") or is_process_running("Codex.exe"):
        if auto_close:
            close_process("ChatGPT.exe")
            close_process("Codex.exe")
        else:
            return False, "برنامه ChatGPT باز است. لطفاً آن را ببندید."

    os.makedirs(CHATGPT_TARGET_DIR, exist_ok=True)

    if not os.path.exists(CHATGPT_TARGET_EXE):
        subprocess.run(
            ["robocopy", CHATGPT_SOURCE_DIR, CHATGPT_TARGET_DIR, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/nc", "/ns", "/np"],
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

    try:
        proc = subprocess.run(
            ["node", ASAR_PATCHER_JS, "patch", CHATGPT_SOURCE_ASAR, CHATGPT_TARGET_ASAR, ".vite/build/preload.js", ENGINE_JS_PATH],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if proc.returncode == 0 and "SUCCESS" in proc.stdout:
            ensure_start_menu_shortcut(
                CHATGPT_TARGET_EXE,
                "ChatGPT.lnk",
                "اجرای ChatGPT (Codex) با فونت وزیرمتن و راست‌چین فارسی"
            )
            return True, "برنامه ChatGPT با موفقیت پچ شد."
        return False, f"خطا در پچ ChatGPT: {proc.stderr or proc.stdout}"
    except Exception as e:
        return False, f"خطای سیستمی: {e}"

def restore_chatgpt(auto_close=False):
    if not os.path.exists(CHATGPT_SOURCE_ASAR):
        return False, "نسخه اصلی ChatGPT یافت نشد."
    if is_process_running("ChatGPT.exe") or is_process_running("Codex.exe"):
        if auto_close:
            close_process("ChatGPT.exe")
            close_process("Codex.exe")
        else:
            return False, "برنامه ChatGPT باز است. لطفاً آن را ببندید."
    try:
        shutil.copy2(CHATGPT_SOURCE_ASAR, CHATGPT_TARGET_ASAR)
        return True, "برنامه ChatGPT به نسخه اولیه بازگردانده شد."
    except Exception as e:
        return False, f"خطا در بازگردانی ChatGPT: {e}"

def launch_chatgpt():
    if os.path.exists(CHATGPT_TARGET_EXE):
        subprocess.Popen([CHATGPT_TARGET_EXE], cwd=CHATGPT_TARGET_DIR)
        return True, "برنامه ChatGPT اجرا شد."
    return False, "برنامه ChatGPT یافت نشد."