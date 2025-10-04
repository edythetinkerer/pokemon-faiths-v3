@echo off
title Pokemon Faiths
echo ========================================
echo    Pokemon Faiths - Game Launcher
echo ========================================
echo.

REM Get the directory where this batch file is located
set "GAME_DIR=%~dp0"
echo Game directory: %GAME_DIR%

REM Change to the game directory
cd /d "%GAME_DIR%"
echo Current directory: %CD%
echo.

REM Check if run_game.py exists
if not exist "run_game.py" (
    echo ERROR: run_game.py not found!
    echo Please make sure you're running this from the game folder.
    echo.
    pause
    exit /b 1
)

REM Check if src directory exists
if not exist "src" (
    echo ERROR: src directory not found!
    echo Please make sure you're running this from the game folder.
    echo.
    pause
    exit /b 1
)

echo Starting game...
echo.
python run_game.py

echo.
echo Game has ended.
pause
