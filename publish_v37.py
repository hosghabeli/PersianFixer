import os
import sys
import json
import re
import subprocess
import shutil

# Ensure UTF-8 console output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

new_ver = "3.7.0"
tag_name = f"v{new_ver}"
rel_title = f"PersianFixer v{new_ver} - انتشار نسخه نصبی و اجرای خودکار"
rel_notes = """### قابلیت‌های جدید در نسخه v3.7.0:
- **فایل نصبی رسمی ویندوز (Setup.exe):** ارائه اینستالر رسمی ساخته‌شده با Inno Setup و ثبت تمیز در Installed Apps ویندوز.
- **اجرای خودکار همراه با ویندوز (Auto-start):** امکان فعال‌سازی شروع خودکار در System Tray از داخل برنامه و منوی کنار ساعت.
- **حفظ تمیزی دسکتاپ:** شورتکات‌ها فقط در منوی استارت ویندوز قرار می‌گیرند و هیچ فایلی روی دسکتاپ ریخته نمی‌شود.
- **پایداری کامل پس از ریستارت ویندوز.**
"""

print(f"=== Publishing {tag_name} ===")

# 1. Update package.json
with open("package.json", "r", encoding="utf-8") as f:
    pkg = json.load(f)
pkg["version"] = new_ver
with open("package.json", "w", encoding="utf-8") as f:
    json.dump(pkg, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("1. Updated package.json")

# 2. Update README.md
with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()
readme = re.sub(r'version-v[0-9.]+-blue\.svg', f'version-v{new_ver}-blue.svg', readme)
with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)
print("2. Updated README.md")

# 3. Update gui.py
with open("gui.py", "r", encoding="utf-8") as f:
    gui = f.read()
gui = re.sub(r'text="v[0-9.]+"', 'text="v3.7"', gui)
with open("gui.py", "w", encoding="utf-8") as f:
    f.write(gui)
print("3. Updated gui.py")

# 4. Update installer.iss
with open("installer.iss", "r", encoding="utf-8") as f:
    iss = f.read()
iss = re.sub(r'#define MyAppVersion "[0-9.]+"', f'#define MyAppVersion "{new_ver}"', iss)
with open("installer.iss", "w", encoding="utf-8") as f:
    f.write(iss)
print("4. Updated installer.iss")

# 5. Build Setup.exe with ISCC
iscc = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe")
setup_path = os.path.join(SCRIPT_DIR, f"PersianFixer-{tag_name}-Setup.exe")
if os.path.exists(iscc):
    print("5. Compiling Setup.exe with ISCC...")
    subprocess.run([iscc, f"/DMyAppVersion={new_ver}", "installer.iss"], check=True)
    print(f"  ✓ Created: {setup_path}")
else:
    print("ISCC not found locally, will rely on GitHub Actions.")

# 6. Build portable ZIP
stage_dir = os.path.join(SCRIPT_DIR, f"release_stage_{new_ver}")
zip_path = os.path.join(SCRIPT_DIR, f"PersianFixer-{tag_name}-windows.zip")
if os.path.exists(stage_dir):
    shutil.rmtree(stage_dir, ignore_errors=True)
os.makedirs(stage_dir, exist_ok=True)

files_to_copy = [
    "PersianFixer.vbs", "run.bat", "update_icon.bat", "update_icon.py",
    "make_release.bat", "make_release.py", "installer.iss",
    "gui.py", "patcher.py", "font_installer.py", "autostart.py", "persian_engine.js",
    "asar_patcher.js", "requirements.txt", "package.json",
    "icon.ico", "icon.png", "README.md", "LICENSE"
]
for f in files_to_copy:
    src = os.path.join(SCRIPT_DIR, f)
    if os.path.exists(src):
        shutil.copy2(src, stage_dir)
if os.path.exists("fonts"):
    shutil.copytree("fonts", os.path.join(stage_dir, "fonts"), dirs_exist_ok=True)
if os.path.exists("node_modules"):
    shutil.copytree("node_modules", os.path.join(stage_dir, "node_modules"), dirs_exist_ok=True)

if os.path.exists(zip_path):
    os.remove(zip_path)
shutil.make_archive(zip_path.replace(".zip", ""), "zip", stage_dir)
shutil.rmtree(stage_dir, ignore_errors=True)
print(f"6. Created portable ZIP: {zip_path}")

# 7. Git commit, tag, push
print("7. Git commit, tag, and push...")
subprocess.run(["git", "add", "."], check=True)
subprocess.run(["git", "commit", "-m", f"chore: release {tag_name} - {rel_title}"], check=True)
subprocess.run(["git", "tag", "-a", tag_name, "-m", f"{rel_title}\n\n{rel_notes}"], check=True)
subprocess.run(["git", "push", "origin", "main", "--tags"], check=True)
print("  ✓ Pushed commit and tag to GitHub!")

# 8. Direct GitHub Release API upload
try:
    token = subprocess.check_output(
        ["powershell", "-NoProfile", "(git credential fill | Select-String 'password=') -replace 'password=',''"],
        cwd=SCRIPT_DIR, creationflags=subprocess.CREATE_NO_WINDOW
    ).decode().strip()
except Exception:
    token = ""

if token:
    print("8. Uploading assets to GitHub Release via API...")
    try:
        ps_script = f"""
        $headers = @{{
            'Authorization' = 'token {token}'
            'User-Agent' = 'PowerShell'
            'Accept' = 'application/vnd.github.v3+json'
        }}
        $body = @{{
            tag_name = '{tag_name}'
            target_commitish = 'main'
            name = '{rel_title}'
            body = '{rel_notes}'
            draft = $false
            prerelease = $false
        }} | ConvertTo-Json -Compress

        $rel = Invoke-RestMethod -Uri 'https://api.github.com/repos/hosgh/PersianFixer/releases' -Method Post -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) -ContentType 'application/json; charset=utf-8'

        # Upload ZIP
        $uploadUrlZip = $rel.upload_url.Replace('{{?name,label}}', '?name=PersianFixer-{tag_name}-windows.zip')
        $bytesZip = [System.IO.File]::ReadAllBytes('{zip_path}')
        $assetHeadersZip = @{{
            'Authorization' = 'token {token}'
            'User-Agent' = 'PowerShell'
            'Accept' = 'application/vnd.github.v3+json'
            'Content-Type' = 'application/zip'
        }}
        Invoke-RestMethod -Uri $uploadUrlZip -Method Post -Headers $assetHeadersZip -Body $bytesZip | Out-Null
        Write-Output "ZIP asset uploaded successfully."

        # Upload Setup EXE
        if (Test-Path '{setup_path}') {{
            $uploadUrlExe = $rel.upload_url.Replace('{{?name,label}}', '?name=PersianFixer-{tag_name}-Setup.exe')
            $bytesExe = [System.IO.File]::ReadAllBytes('{setup_path}')
            $assetHeadersExe = @{{
                'Authorization' = 'token {token}'
                'User-Agent' = 'PowerShell'
                'Accept' = 'application/vnd.github.v3+json'
                'Content-Type' = 'application/octet-stream'
            }}
            Invoke-RestMethod -Uri $uploadUrlExe -Method Post -Headers $assetHeadersExe -Body $bytesExe | Out-Null
            Write-Output "Setup EXE asset uploaded successfully."
        }}
        """
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], cwd=SCRIPT_DIR, check=True)
        print("  ✓ Release and both assets uploaded to GitHub!")
    except Exception as e:
        print(f"  Note on API upload: {e}")
else:
    print("  GitHub Actions will publish the release with assets automatically from tag.")

print(f"\n🎉 Successfully finished release for {tag_name}!")
