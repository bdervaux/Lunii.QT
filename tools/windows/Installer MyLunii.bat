@echo off
rem Double-cliquez sur ce fichier pour installer et ouvrir MyLunii.
rem (Python n'est pas necessaire : tout est deja dans le dossier MyLunii.)
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0installer-mylunii.ps1"
echo.
pause
