@echo off
taskkill /IM CapCut.exe >nul 2>&1
timeout /t 5 >nul
taskkill /F /T /IM CapCut.exe >nul 2>&1
echo CapCut ferme
