import os
import sys
import time
import subprocess
import ctypes
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PNG_PATH = os.path.join(SCRIPT_DIR, "icon.png")
DESKTOP_LNK = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop", "PersianFixer.lnk")

def update_icon():
    if not os.path.exists(PNG_PATH):
        print(f"Error: {PNG_PATH} not found!")
        return False

    print("1. Reading edited icon.png...")
    img = Image.open(PNG_PATH).convert("RGBA")

    # Ensure square
    w, h = img.size
    if w != h:
        dim = max(w, h)
        square = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
        square.paste(img, ((dim - w) // 2, (dim - h) // 2))
        img = square

    timestamp = int(time.time())
    new_ico = os.path.join(SCRIPT_DIR, f"app_icon_{timestamp}.ico")
    default_ico = os.path.join(SCRIPT_DIR, "icon.ico")

    # Save both default and versioned ico (versioned forces Windows cache bypass)
    print("2. Generating multi-resolution icon.ico...")
    for p in (new_ico, default_ico):
        img.save(p, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

    # Delete older app_icon_*.ico files
    for f in os.listdir(SCRIPT_DIR):
        if f.startswith("app_icon_") and f.endswith(".ico") and f != f"app_icon_{timestamp}.ico":
            try:
                os.remove(os.path.join(SCRIPT_DIR, f))
            except Exception:
                pass

    # Update Desktop shortcut
    if os.path.exists(DESKTOP_LNK):
        print("3. Updating Desktop shortcut target...")
        ps_code = f"""
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut('{DESKTOP_LNK}')
        $Shortcut.IconLocation = '{new_ico},0'
        $Shortcut.Save()
        """
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_code], creationflags=subprocess.CREATE_NO_WINDOW)

    # Broadcast shell change notify to immediately refresh Windows Desktop icons
    print("4. Refreshing Windows icon cache...")
    try:
        SHCNE_ASSOCCHANGED = 0x08000000
        SHCNF_IDLIST = 0x0000
        ctypes.windll.shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, 0, 0)
    except Exception:
        pass

    print("\n[SUCCESS] آیکون جدید با موفقیت اعمال و کش ویندوز به‌روزرسانی شد!")
    return True

if __name__ == "__main__":
    update_icon()