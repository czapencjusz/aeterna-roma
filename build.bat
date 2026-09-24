@echo off
rem Builds a single AeternaRoma.exe (Python and the game packed together) with PyInstaller.
rem Players who have Python installed can instead just run:  python aeterna_roma.py
setlocal
where python >nul 2>nul || (echo [ERROR] Python 3.9 or newer is needed: https://www.python.org/downloads/ & exit /b 1)
echo Installing build tools...
python -m pip install --upgrade -r requirements.txt pyinstaller || (echo [ERROR] Could not install the build tools. & exit /b 1)
echo Building AeternaRoma.exe...
python -m PyInstaller --noconfirm --clean --onefile --windowed --name AeternaRoma --add-data "aeterna\ui;aeterna\ui" aeterna_roma.py || (echo [ERROR] Build failed. & exit /b 1)
echo [SUCCESS] Built dist\AeternaRoma.exe
