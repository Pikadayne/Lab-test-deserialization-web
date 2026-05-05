@echo off
REM run.bat - Create venv, install requirements, activate and run the Flask app

setlocal

if not exist "venv\Scripts\activate.bat" (
  echo Creating virtual environment...
  python -m venv venv
  if errorlevel 1 (
    echo Failed to create virtualenv. Ensure Python is on PATH.
    pause
    exit /b 1
  )
  echo Activating virtual environment...
  call venv\Scripts\activate.bat
  echo Upgrading pip and installing requirements...
  python -m pip install --upgrade pip
  pip install -r requirements.txt
) else (
  echo Activating virtual environment...
  call venv\Scripts\activate.bat
)

echo Starting Flask app on http://127.0.0.1:5000
python app.py

endlocal
pause
