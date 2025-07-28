@echo off
REM --- Configure your settings here ---
set GOOGLE_API_KEY=AIzaSyDEvV0DoZPRp3lDdKDaq7EBQFxfFBpPhtk
set TRANSCRIPT_DIR=G:\raw_code\audio_transcriber\transcripts
set PYTHON_SCRIPT=stock_analysis.py
REM -----------------------------------

REM Set the environment variable for this session
set GOOGLE_API_KEY=%GOOGLE_API_KEY%

echo.
echo --- Starting Batch Analysis ---
echo.

if not exist %TRANSCRIPT_DIR% (
    echo Error: Transcript directory "%TRANSCRIPT_DIR%" not found.
    goto :end
)

REM Loop through all .txt files in the specified directory
for %%f in ("%TRANSCRIPT_DIR%\*.txt") do (
    echo Processing file: "%%~f"
    python "%PYTHON_SCRIPT%" "%%~f"
    echo.
)

echo --- Batch processing complete. ---
:end
pause