@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo == Studio Shorts : installation (5-10 min, ~2 Go) ==
where uv >nul 2>&1
if errorlevel 1 (
  echo -^> installation de uv...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
  set "PATH=%USERPROFILE%\.local\bin;%PATH%"
)
where git >nul 2>&1
if errorlevel 1 (
  echo -^> installation de Git for Windows ^(requis par Claude Code^)...
  winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements
)
where claude >nul 2>&1
if errorlevel 1 (
  echo -^> installation de Claude Code...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://claude.ai/install.ps1 | iex"
)
if not exist studio\_jobs mkdir studio\_jobs
if not exist shorts\_veille mkdir shorts\_veille

echo -^> environnement de MONTAGE ^(.venv^)
uv venv --python 3.12 .venv || goto :erreur
uv pip install --python .venv\Scripts\python.exe -r requirements.txt || goto :erreur
for /f "delims=" %%i in ('.venv\Scripts\python.exe -c "import site;print(site.getsitepackages()[-1])"') do set SP=%%i
if exist "%SP%\pyJianYingDraft" rmdir /s /q "%SP%\pyJianYingDraft"
xcopy /e /i /q vendor\pyJianYingDraft "%SP%\pyJianYingDraft" >nul

echo -^> environnement de TELECHARGEMENT ^(.venv312^)
uv venv --python 3.12 .venv312 || goto :erreur
uv pip install --python .venv312\Scripts\python.exe -U yt-dlp imageio-ffmpeg || goto :erreur

echo -^> ffmpeg
.venv\Scripts\python.exe -c "import imageio_ffmpeg,shutil;shutil.copy(imageio_ffmpeg.get_ffmpeg_exe(),'_bin/ffmpeg.exe')" || goto :erreur

echo.
echo == Installation terminee ==
echo Reste a faire ^(voir LISEZ-MOI.md^) :
echo   1. Ouvre un NOUVEAU terminal et tape :  claude auth login
echo   2. (voix ElevenLabs deja configuree)
echo   3. CapCut installe, avec au moins UN projet cree et enregistre
echo Ensuite : double-clic sur "Studio Shorts.bat".
pause
exit /b 0
:erreur
echo.
echo ECHEC de l'installation : envoie une capture de ce message.
pause
exit /b 1
