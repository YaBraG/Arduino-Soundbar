@echo off
setlocal
cd /d "%~dp0"

set PY=software\python-3.12.10-embed-amd64\python.exe

%PY% -m pip install --upgrade pip
%PY% -m pip install pyinstaller
%PY% -m pip install pyserial

%PY% -m PyInstaller --onefile --noconsole --name Soundbar main.py

echo.
echo Build complete: dist\Soundbar.exe
pause
