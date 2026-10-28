@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONUTF8=1
set "PATH=%USERPROFILE%\.local\bin;%PATH%"
if not exist .venv\Scripts\pythonw.exe (
  echo Lance d'abord "1 - Installer.bat"
  pause
  exit /b 1
)
if not exist studio\_jobs mkdir studio\_jobs
if not exist shorts\_veille mkdir shorts\_veille
rem Application de bureau (fenêtre native, sans console). Ancien mode navigateur : studio\serveur.py
start "" .venv\Scripts\pythonw.exe studio\app.py
