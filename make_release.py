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

def get_current_version():
    pkg_path = os.path.join(SCRIPT_DIR, "package.json")
    if os.path.exists(pkg_path):
        with open(pkg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("version", "1.0.0")
    return "1.0.0"

def bump_patch(version_str):
    parts = version_str.split(".")
    if len(parts) == 3 and parts[2].isdigit():
        parts[2] = str(int(parts[2]) + 1)
        return ".".join(parts)
    return version_str + ".1"

def update_file_version(filepath, pattern, replacement):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = re.sub(pattern, replacement, content)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

def main():
    print("=" * 60)
    print("🚀  ابزار خودکارسازی انتشار نسخه جدید PersianFixer")
    print("=" * 60)

    cur_ver = get_current_version()
    suggested_ver = bump_patch(cur_ver)

    print(f"\n📌 نسخه فعلی پروژه: {cur_ver}")
    print(f"👉 نسخه پیشنهادی جدید: {suggested_ver}")

    ver_input = input(f"\nشماره نسخه جدید را وارد کنید [پیش‌فرض: {suggested_ver}]: ").strip()
    new_ver = ver_input if ver_input else suggested_ver
    new_ver = new_ver.lstrip("v")
    tag_name = f"v{new_ver}"

    print(f"\nتگ جدید: {tag_name}")

    rel_title = input(f"عنوان انتشار [پیش‌فرض: انتشار نسخه {new_ver}]: ").strip()
    if not rel_title:
        rel_title = f"PersianFixer v{new_ver} - انتشار نسخه جدید"

    rel_notes = input("توضیح کوتاه تغییرات (اختیاری): ").strip()
    if not rel_notes:
        rel_notes = f"به‌روزرسانی و بهبود عملکرد در نسخه {new_ver}."

    print("\n⏳ در حال به‌روزرسانی فایل‌های پروژه...")

    # 1. Update package.json
    pkg_path = os.path.join(SCRIPT_DIR, "package.json")
    if os.path.exists(pkg_path):
        with open(pkg_path, "r", encoding="utf-8") as f:
            pkg_data = json.load(f)
        pkg_data["version"] = new_ver
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump(pkg_data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("  ✓ فایل package.json به‌روزرسانی شد.")

    # 2. Update README.md badge
    readme_path = os.path.join(SCRIPT_DIR, "README.md")
    update_file_version(
        readme_path,
        r'version-v[0-9.]+-blue\.svg',
        f'version-v{new_ver}-blue.svg'
    )
    print("  ✓ مدال نسخه در README.md به‌روزرسانی شد.")

    # 3. Update gui.py version badge & title
    gui_path = os.path.join(SCRIPT_DIR, "gui.py")
    update_file_version(
        gui_path,
        r'v[0-9.]+(?:\.[0-9]+)? STABLE',
        f'v{new_ver} STABLE'
    )
    update_file_version(
        gui_path,
        r'text="v[0-9.]+"',
        f'text="v{new_ver}"'
    )
    update_file_version(
        gui_path,
        r'PersianFixer v[0-9.]+',
        f'PersianFixer v{new_ver}'
    )
    print("  ✓ نسخه نمایش داده شده در gui.py به‌روزرسانی شد.")

    # 4. Update installer.iss version
    iss_path = os.path.join(SCRIPT_DIR, "installer.iss")
    update_file_version(
        iss_path,
        r'#define MyAppVersion "[0-9.]+"',
        f'#define MyAppVersion "{new_ver}"'
    )
    print("  ✓ نسخه در installer.iss به‌روزرسانی شد.")

    # 5. Git commit and tag
    print("\n⏳ در حال ثبت در Git و ساخت تگ...")
    try:
        subprocess.run(["git", "add", "."], cwd=SCRIPT_DIR, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"chore: release {tag_name} - {rel_title}"],
            cwd=SCRIPT_DIR, check=True
        )
        subprocess.run(
            ["git", "tag", "-a", tag_name, "-m", f"{rel_title}\n\n{rel_notes}"],
            cwd=SCRIPT_DIR, check=True
        )
        print("  ✓ کامیت و تگ رسمی با موفقیت ثبت شد.")
    except Exception as e:
        print(f"❌ خطا در عملیات Git: {e}")
        input("\nبرای خروج Enter بزنید...")
        return

    # 5. Push to GitHub
    print("\n⏳ در حال ارسال به گیت‌هاب (Pushing to origin main and tags)...")
    try:
        subprocess.run(["git", "push", "origin", "main", "--tags"], cwd=SCRIPT_DIR, check=True)
        print("  ✓ کدهای جدید و تگ به گیت‌هاب ارسال شدند!")
    except Exception as e:
        print(f"❌ خطا در ارسال به گیت‌هاب: {e}")
        input("\nبرای خروج Enter بزنید...")
        return

    # 6. Local ZIP creation & Direct GitHub API Release
    print("\n⏳ در حال ساخت بسته فشرده ZIP پرتابل...")
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

    fonts_src = os.path.join(SCRIPT_DIR, "fonts")
    if os.path.exists(fonts_src):
        shutil.copytree(fonts_src, os.path.join(stage_dir, "fonts"), dirs_exist_ok=True)

    nm_src = os.path.join(SCRIPT_DIR, "node_modules")
    if os.path.exists(nm_src):
        shutil.copytree(nm_src, os.path.join(stage_dir, "node_modules"), dirs_exist_ok=True)

    if os.path.exists(zip_path):
        os.remove(zip_path)

    shutil.make_archive(zip_path.replace(".zip", ""), "zip", stage_dir)
    shutil.rmtree(stage_dir, ignore_errors=True)
    print(f"  ✓ فایل فشرده پرتابل با موفقیت ساخته شد: PersianFixer-{tag_name}-windows.zip")

    # 7. Local Inno Setup Installer creation
    iscc_candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Inno Setup 6", "ISCC.exe"),
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe"
    ]
    iscc_exe = next((p for p in iscc_candidates if os.path.exists(p)), None)
    setup_path = os.path.join(SCRIPT_DIR, f"PersianFixer-{tag_name}-Setup.exe")

    if iscc_exe:
        print(f"\n⏳ در حال ساخت فایل نصبی با Inno Setup...")
        try:
            subprocess.run([iscc_exe, f"/DMyAppVersion={new_ver}", "installer.iss"], cwd=SCRIPT_DIR, check=True)
            print(f"  ✓ فایل نصبی با موفقیت ساخته شد: PersianFixer-{tag_name}-Setup.exe")
        except Exception as e:
            print(f"  ⚠️ خطا در ساخت فایل نصبی: {e}")

    # 8. Create GitHub Release via API if token available
    try:
        token = subprocess.check_output(
            ["powershell", "-NoProfile", "(git credential fill | Select-String 'password=') -replace 'password=',''"],
            cwd=SCRIPT_DIR, creationflags=subprocess.CREATE_NO_WINDOW
        ).decode().strip()
    except Exception:
        token = ""

    if token:
        print("\n⏳ در حال ثبت Release در صفحه گیت‌هاب...")
        try:
            has_setup = os.path.exists(setup_path)
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

            $rel = Invoke-RestMethod -Uri 'https://api.github.com/repos/hosghabeli/PersianFixer/releases' -Method Post -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) -ContentType 'application/json; charset=utf-8'
            
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

            # Upload Setup EXE if exists
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
            }}
            """
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], cwd=SCRIPT_DIR, check=True)
            print("  ✓ ریلیز رسمی در گیت‌هاب با موفقیت منتشر شد و هر دو فایل نصبی و پرتابل پیوست گردیدند!")
        except Exception as e:
            print(f"  ⚠️ هشدار: ثبت API با خطا مواجه شد ({e})، اما به لطف GitHub Actions تگ ارسال شد و گیت‌هاب خودش ریلیز را می‌سازد.")
    else:
        print("  ✓ تگ جدید ارسال شد؛ GitHub Actions سرور گیت‌هاب به طور خودکار ریلیز را منتشر خواهد کرد.")

    print("\n" + "=" * 60)
    print(f"🎉 انتشار نسخه {tag_name} با موفقیت کامل انجام شد!")
    print(f"🔗 آدرس انتشارهای گیت‌هاب: https://github.com/hosghabeli/PersianFixer/releases")
    print("=" * 60)
    input("\nبرای پایان Enter را بزنید...")

if __name__ == "__main__":
    main()
