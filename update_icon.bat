@echo off
chcp 65001 >nul
echo Updating icon from icon.png...
"C:\Python314\python.exe" "%~dp0update_icon.py"
echo.
pause