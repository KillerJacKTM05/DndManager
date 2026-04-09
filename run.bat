@echo off
REM ========================================
REM D&D Multi-Agent Bridge - Enhanced Launcher
REM Handles system Python, Anaconda, and virtual environments
REM ========================================

title D^&D Multi-Agent Bridge Launcher

echo.
echo ========================================
echo   D^&D Multi-Agent Bridge Launcher
echo ========================================
echo.

REM Change to the bridge directory
D:
cd D:\dndBridge

if not exist "dnd_bridge.py" (
    echo [ERROR] dnd_bridge.py not found in current directory!
    echo Current directory: %CD%
    echo.
    echo Please ensure you're in the correct directory.
    pause
    exit /b 1
)

REM Set the Google API Key
set GOOGLE_API_KEY=AIzaSyCps3nnYrKrWhs4yowDNs0ejroUYkHUmnY
echo [OK] API Key configured

REM ========================================
REM Python Detection - Try multiple sources
REM ========================================

echo.
echo Detecting Python installation...

REM Initialize PYTHON_CMD as empty
set PYTHON_CMD=

REM Method 1: Try standard python command
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    echo [OK] Found system Python
    goto :python_found
)

REM Method 2: Try python3 command
python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    echo [OK] Found Python3
    goto :python_found
)

REM Method 3: Try Anaconda default location
if exist "%USERPROFILE%\anaconda3\python.exe" (
    set PYTHON_CMD="%USERPROFILE%\anaconda3\python.exe"
    echo [OK] Found Anaconda Python
    goto :python_found
)

REM Method 4: Try Miniconda default location
if exist "%USERPROFILE%\miniconda3\python.exe" (
    set PYTHON_CMD="%USERPROFILE%\miniconda3\python.exe"
    echo [OK] Found Miniconda Python
    goto :python_found
)

REM Method 5: Check if we're already in an Anaconda environment
where conda >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Conda detected - trying to use current environment
    set PYTHON_CMD=python
    goto :python_found
)

REM If we get here, Python was not found
echo.
echo [ERROR] Python not found!
echo.
echo Tried:
echo   1. System Python (python / python3)
echo   2. Anaconda (%USERPROFILE%\anaconda3)
echo   3. Miniconda (%USERPROFILE%\miniconda3)
echo.
echo Solutions:
echo   A) If using Anaconda: Open "Anaconda Prompt" and run:
echo      cd /d D:\dndBridge
echo      python dnd_bridge.py
echo.
echo   B) Install Python from: https://www.python.org/downloads/
echo      Make sure to check "Add Python to PATH"
echo.
pause
exit /b 1

:python_found
REM Display Python version
echo Python command: %PYTHON_CMD%
%PYTHON_CMD% --version

REM ========================================
REM Package Check
REM ========================================
echo.
echo Checking required packages...

%PYTHON_CMD% -c "import gradio" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Gradio not installed
    echo.
    echo Would you like to install required packages now? (Y/N)
    set /p INSTALL_CHOICE="> "
    
    if /i "%INSTALL_CHOICE%"=="Y" (
        echo.
        echo Installing packages from requirements.txt...
        %PYTHON_CMD% -m pip install -r requirements.txt
        if errorlevel 1 (
            echo.
            echo [ERROR] Package installation failed
            echo.
            echo If using Anaconda, try:
            echo   conda install pip
            echo   pip install -r requirements.txt
            echo.
            pause
            exit /b 1
        )
        echo [OK] Packages installed successfully
    ) else (
        echo.
        echo [INFO] Skipping package installation
        echo Run manually: %PYTHON_CMD% -m pip install -r requirements.txt
        pause
        exit /b 1
    )
) else (
    echo [OK] Required packages found
)
) else (
    echo [OK] Required packages found
)

REM ========================================
REM Check for Google API package
REM ========================================
echo.
echo Checking Google Generative AI package...

%PYTHON_CMD% -c "import google.generativeai" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] google-generativeai package not found
    echo.
    echo Would you like to install it now? (Y/N)
    set /p INSTALL_CHOICE="> "
    
    if /i "%INSTALL_CHOICE%"=="Y" (
        echo.
        echo Installing google-generativeai...
        %PYTHON_CMD% -m pip install google-generativeai
        if errorlevel 1 (
            echo [ERROR] Failed to install google-generativeai
            pause
            exit /b 1
        )
        echo [OK] Google Generative AI package installed
    )
) else (
    echo [OK] Google Generative AI package found
)

REM ========================================
REM Launch the Bridge
REM ========================================
echo.
echo ========================================
echo   Starting D^&D Bridge...
echo ========================================
echo.
echo The interface will open at:
echo http://localhost:7860
echo.
echo Press Ctrl+C to stop the server
echo.

REM Launch using the detected Python
%PYTHON_CMD% dnd_bridge.py

REM If the script exits, pause to show any errors
if errorlevel 1 (
    echo.
    echo ========================================
    echo [ERROR] Bridge exited with error
    echo ========================================
    echo.
    echo Common issues:
    echo   1. Missing GOOGLE_API_KEY environment variable
    echo   2. API key is invalid
    echo   3. Missing required packages
    echo   4. Port 7860 already in use
    echo.
    pause
)
