@echo off
rem This batch file runs the audio transcription program.

rem --- Configuration ---
rem IMPORTANT: Replace "YOUR_API_KEY_HERE" with your actual Google API key.
set GOOGLE_API_KEY=AIzaSyDEvV0DoZPRp3lDdKDaq7EBQFxfFBpPhtk

rem Change directory to where the script is located.
rem Use /d for changing both drive and directory.
cd /d G:\audio_transcriber

rem --- Execution ---
echo.
echo Activating the Python virtual environment...
rem Activate the venv. The 'call' command is used to ensure control returns to the batch file.
call .\venv\Scripts\activate.bat

echo.
echo Running the audio transcription script...
rem Run the Python script.
python audio_transcriber.py

echo.
echo Script finished. Press any key to exit...
pause > nul