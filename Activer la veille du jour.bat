@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Crée la tâche Windows « Studio Shorts - veille du jour » : chaque matin à 7 h (ou au
rem démarrage du PC s'il était éteint), studio\quotidien.py fait la veille du jour et écrit
rem un script par sujet. Pour la retirer : Planificateur de tâches > supprimer la tâche.
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$r = (Get-Location).Path;" ^
  "$a = New-ScheduledTaskAction -Execute (Join-Path $r '.venv\Scripts\pythonw.exe') -Argument ('-X utf8 \"' + (Join-Path $r 'studio\quotidien.py') + '\"') -WorkingDirectory $r;" ^
  "$t = New-ScheduledTaskTrigger -Daily -At 7:00;" ^
  "$s = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 3);" ^
  "Register-ScheduledTask -TaskName 'Studio Shorts - veille du jour' -Action $a -Trigger $t -Settings $s -Force | Out-Null;" ^
  "'Prochaine veille : ' + (Get-ScheduledTaskInfo -TaskName 'Studio Shorts - veille du jour').NextRunTime"
pause
