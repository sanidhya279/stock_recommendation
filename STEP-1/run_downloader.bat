@echo off
echo Activating virtual environment...

REM Change to the directory where this batch file is located
cd /d "%~dp0"

IF %ERRORLEVEL% NEQ 0 (
    echo Error: Could not change directory.
    goto :eof
)

echo Current directory: %cd%
echo Listing files in current directory:
dir /b

REM Activate the virtual environment
call venv\Scripts\activate.bat

IF %ERRORLEVEL% NEQ 0 (
    echo Error: Could not activate virtual environment. Make sure 'venv' folder exists and is correctly set up.
    goto :eof
)

echo Running Python script...
python audio_download.py

IF %ERRORLEVEL% NEQ 0 (
    echo Error: Python script encountered an issue.
)

echo Script finished.
pause
