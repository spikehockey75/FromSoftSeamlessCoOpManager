@echo off 
title FromSoft Co-op Settings Manager 
cd /d "%~dp0" 
if not exist ".venv\Scripts\activate.bat" ( 
    call Setup_FromSoft_Coop_Manager.bat 
    exit /b 
) 

REM Start the server using pythonw from venv (runs without console window)
start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0server.py" 
