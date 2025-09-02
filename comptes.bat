@echo off
title Comptes

:: setup env
set COMPTES_APP_DATA=%APPDATA%/comptes
set VENV_PATH=%COMPTES_APP_DATA%/venv
python -m venv "%VENV_PATH%"
call %VENV_PATH%\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python "%~dp0launcher.py" %COMPTES_APP_DATA%

pause