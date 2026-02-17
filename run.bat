@echo off 
title FromSoft Co-op Settings Manager 
cd /d "%~dp0" 
if not exist ".venv\Scripts\activate.bat" ( 
    call Setup_FromSoft_Coop_Manager.bat 
    exit /b 
) 
call .venv\Scripts\activate.bat 
where pythonw >nul 2>&1 
if %errorlevel%==0 ( 
    start "" pythonw server.py 
) else ( 
    python server.py 
) 
