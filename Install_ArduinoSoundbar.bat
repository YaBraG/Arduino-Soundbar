@echo off
setlocal

set REPO_OWNER=YaBraG
set REPO_NAME=Arduino-Soundbar
set PS1_NAME=Install_ArduinoSoundbar.ps1
set PS1_URL=https://raw.githubusercontent.com/%REPO_OWNER%/%REPO_NAME%/main/%PS1_NAME%

echo [INFO] Downloading installer logic...
powershell -NoProfile -ExecutionPolicy Bypass ^
  -Command "Invoke-WebRequest -Uri '%PS1_URL%' -OutFile '%PS1_NAME%'"

if not exist "%PS1_NAME%" (
  echo [ERROR] Failed to download installer script.
  pause
  exit /b 1
)

echo [INFO] Running installer...
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1_NAME%"

pause
