@echo off
rem Starts the game with your installed Python (installs pywebview the first time).
python -c "import webview" 2>nul || python -m pip install -r requirements.txt
python aeterna_roma.py %*
