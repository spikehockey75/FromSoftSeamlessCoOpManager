@echo off
title FromSoft Co-op Settings Manager
color 0B

echo.
echo  ──────────────────────────────────────────
echo   FromSoft Co-op Settings Manager
echo  ──────────────────────────────────────────
echo.

cd /d "%~dp0"

REM ─── Check if installed ─────────────────────────────────────────
if not exist ".venv\Scripts\activate.bat" (
    echo  First time? Running installer...
    echo.
    call install.bat
    exit /b
)

REM ─── Activate virtual environment ───────────────────────────────
call .venv\Scripts\activate.bat

REM ─── Start the app ──────────────────────────────────────────────
echo  Starting server...
echo  Your browser will open automatically.
echo.
echo  To stop the app, close this window or press Ctrl+C.
echo  ──────────────────────────────────────────
echo.

python server.py

echo.
echo  Server stopped.
pause
