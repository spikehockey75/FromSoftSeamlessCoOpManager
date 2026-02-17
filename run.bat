@echo off 
title FromSoft Co-op Settings Manager 
cd /d "%~dp0" 
if not exist ".venv\Scripts\activate.bat" ( 
    call Setup_FromSoft_Coop_Manager.bat 
    exit /b 
) 
call .venv\Scripts\activate.bat 
if exist ".venv\Scripts\pythonw.exe" ( 
    start "" ".venv\Scripts\pythonw.exe" server.py 
) else ( 
    start "" python server.py 
) 
