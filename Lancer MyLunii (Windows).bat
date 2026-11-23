@echo off
chcp 65001 >nul
rem Double-cliquez sur ce fichier pour lancer MyLunii sous Windows.
rem La premiere fois, il prepare tout (2 a 5 minutes, connexion Internet necessaire).
rem Ensuite, l'application s'ouvre en quelques secondes.

cd /d "%~dp0"
set "VENV=%~dp0.venv"
set "READY=%VENV%\.lunii-ready"

rem 1. Trouver Python (3.12 / 3.11 en priorite, ce sont les plus surs)
set "PY="
for %%V in (3.12 3.11 3.10 3.13) do (
  if not defined PY (
    py -%%V -c "import sys" >nul 2>nul && set "PY=py -%%V"
  )
)
if not defined PY (
  python -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>nul && set "PY=python"
)
if not defined PY (
  echo.
  echo  Python n'est pas installe sur cet ordinateur.
  echo  La page de telechargement va s'ouvrir : installez Python 3.12
  echo  en cochant bien "Add python.exe to PATH", puis relancez ce fichier.
  echo.
  start "" "https://www.python.org/downloads/windows/"
  pause
  exit /b 1
)

rem 2. Premiere fois : preparer l'environnement
if not exist "%READY%" (
  echo Preparation de MyLunii - premiere fois uniquement...
  if exist "%VENV%" rmdir /s /q "%VENV%"
  %PY% -m venv "%VENV%" || goto :error
  "%VENV%\Scripts\python.exe" -m pip install --upgrade pip >nul
  "%VENV%\Scripts\python.exe" -m pip install -r requirements-launcher.txt || goto :error
  rem traductions francaises + ressources de l'application
  "%VENV%\Scripts\pyside6-lrelease.exe" locales\fr_FR.ts -qm locales\fr_FR.qm >nul 2>nul
  "%VENV%\Scripts\pyside6-rcc.exe" resources.qrc -o resources_rc.py >nul 2>nul
  echo ok> "%READY%"
)

rem 3. Lancer l'application (sans fenetre noire)
start "" "%VENV%\Scripts\pythonw.exe" lunii-qt.py
exit /b 0

:error
echo.
echo  L'installation a echoue. Verifiez votre connexion Internet et reessayez.
echo.
pause
exit /b 1
