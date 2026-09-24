@echo off
chcp 65001 >nul
echo بستن Antigravity و اعمال پچ فارسی...
taskkill /F /T /IM Antigravity.exe >nul 2>&1
timeout /t 2 /nobreak >nul
set "RES=%LOCALAPPDATA%\Programs\antigravity\resources"
if not exist "%RES%\app.asar.bak" (
    copy /y "%RES%\app.asar" "%RES%\app.asar.bak" >nul
)
copy /y "%RES%\app.asar.patched" "%RES%\app.asar" >nul
echo پچ با موفقیت اعمال شد! در حال اجرای مجدد Antigravity...
start "" "%LOCALAPPDATA%\Programs\antigravity\Antigravity.exe"
