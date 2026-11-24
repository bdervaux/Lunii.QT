@echo off
rem Double-cliquez sur ce fichier pour desinstaller MyLunii.
rem Votre bibliotheque d'histoires est conservee.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0installer-mylunii.ps1" -Desinstaller
echo.
pause
