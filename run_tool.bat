@echo off
title Douyin to YouTube Tool
echo.
echo ========================================
echo    Douyin to YouTube Tool
echo ========================================
echo.
echo Starting application...
echo.

REM Run the tool with py command (Windows Python Launcher)
py douyin_youtube_tool.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo Application exited with error
    pause
) else (
    echo.
    echo Application closed successfully
)

echo.
echo Press any key to exit...
pause >nul
