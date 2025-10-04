@echo off
echo Starting Pokemon Faiths...
echo.
echo Working directory: %CD%
echo.

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo Changed to: %CD%
echo.

REM Run the Python script
python run_game.py

echo.
echo Game has ended.
pause