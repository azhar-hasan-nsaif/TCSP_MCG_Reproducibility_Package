@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo TCSP-MCG Step-by-Step Reproducibility UI
echo ============================================================
echo.

if not exist ".venv\Scripts\python.exe" (
  echo 1. Creating Python virtual environment...
  python -m venv .venv
  if errorlevel 1 goto failure
) else (
  echo 1. Virtual environment already exists.
)

echo 2. Activating virtual environment...
call ".venv\Scripts\activate.bat"
if errorlevel 1 goto failure

echo 3. Installing or checking requirements...
python -m pip install --upgrade pip
if errorlevel 1 goto failure
pip install -r requirements.txt
if errorlevel 1 goto failure

echo 4. Launching Streamlit step-by-step UI...
echo.
echo The UI will open in your browser. Select "Step-by-step runner"
echo from the sidebar to run each artifact step and view output.
echo.
streamlit run ui\app.py
if errorlevel 1 goto failure

exit /b 0

:failure
echo.
echo FAILURE: Could not launch the step-by-step UI.
pause
exit /b 1
