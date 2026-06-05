@echo off
title Douyin to YouTube Tool
echo.
echo ========================================
echo    Douyin to YouTube Tool
echo ========================================
echo.
echo Starting application...
echo.

pushd "%~dp0"

REM Prefer the project environment so yt-dlp and yt-dlp-ejs stay in sync.
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" douyin_youtube_tool.py
) else (
    py douyin_youtube_tool.py
)

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
popd
