import os
import sys
import winreg

REG_SUBKEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "PersianFixer"

def get_autostart_command():
    """
    Returns the command to run PersianFixer minimized in tray on Windows startup.
    Prefers PersianFixer.vbs if present, otherwise uses pythonw.exe gui.py --tray.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    vbs_path = os.path.join(script_dir, "PersianFixer.vbs")
    
    if os.path.exists(vbs_path):
        return f'wscript.exe "{vbs_path}" --tray'
    
    pythonw = sys.executable.replace("python.exe", "pythonw.exe")
    gui_py = os.path.join(script_dir, "gui.py")
    return f'"{pythonw}" "{gui_py}" --tray'

def is_autostart_enabled():
    """Checks whether PersianFixer is registered in HKCU Run registry."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_SUBKEY, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, APP_NAME)
            return bool(val)
    except (FileNotFoundError, OSError):
        return False

def set_autostart(enable: bool):
    """Enables or disables auto-starting PersianFixer on Windows startup."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_SUBKEY, 0, winreg.KEY_ALL_ACCESS) as key:
            if enable:
                cmd = get_autostart_command()
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
                return True, "اجرای خودکار همراه با ویندوز فعال شد."
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
                return True, "اجرای خودکار همراه با ویندوز غیرفعال شد."
    except Exception as e:
        return False, f"خطا در تنظیم رجیستری: {e}"

if __name__ == "__main__":
    print(f"Autostart enabled: {is_autostart_enabled()}")
    print(f"Command: {get_autostart_command()}")
