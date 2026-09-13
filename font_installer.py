import os
import sys
import shutil
import winreg
import ctypes
from ctypes import wintypes

HWND_BROADCAST = 0xFFFF
WM_FONTCHANGE = 0x001D
SMTO_ABORTIFHUNG = 0x0002

def is_font_installed():
    """Check if Vazirmatn is registered in HKCU or HKLM fonts registry and file exists."""
    user_fonts_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts")
    dest_path = os.path.join(user_fonts_dir, "Vazirmatn.ttf")
    if os.path.isfile(dest_path):
        return True

    for root_key in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        try:
            with winreg.OpenKey(root_key, r"Software\Microsoft\Windows NT\CurrentVersion\Fonts") as key:
                i = 0
                while True:
                    try:
                        name, _, _ = winreg.EnumValue(key, i)
                        if "vazirmatn" in name.lower() or "vazir" in name.lower():
                            return True
                        i += 1
                    except OSError:
                        break
        except OSError:
            pass
    return False

def install_vazirmatn_font(font_path=None):
    """Installs Vazirmatn TTF font for current user safely."""
    if font_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(script_dir, "fonts", "Vazirmatn.ttf")

    if not os.path.isfile(font_path):
        return False, f"فایل فونت در مسیر یافت نشد: {font_path}"

    try:
        user_fonts_dir = os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Windows", "Fonts")
        os.makedirs(user_fonts_dir, exist_ok=True)
        dest_path = os.path.join(user_fonts_dir, "Vazirmatn.ttf")

        if not os.path.exists(dest_path):
            try:
                shutil.copy2(font_path, dest_path)
            except PermissionError:
                pass

        key_path = r"Software\Microsoft\Windows NT\CurrentVersion\Fonts"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "Vazirmatn (TrueType)", 0, winreg.REG_SZ, dest_path)

        gdi32 = ctypes.WinDLL("gdi32.dll")
        gdi32.AddFontResourceW.argtypes = [wintypes.LPCWSTR]
        gdi32.AddFontResourceW.restype = ctypes.c_int
        gdi32.AddFontResourceW(dest_path)

        user32 = ctypes.WinDLL("user32.dll")
        result = wintypes.DWORD()
        user32.SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_FONTCHANGE,
            0,
            0,
            SMTO_ABORTIFHUNG,
            1000,
            ctypes.byref(result)
        )
        return True, "فونت وزیرمتن با موفقیت در ویندوز فعال شد."
    except Exception as e:
        return False, f"خطا در نصب فونت: {e}"

if __name__ == "__main__":
    ok, msg = install_vazirmatn_font()
    print("Result:", ok, msg)