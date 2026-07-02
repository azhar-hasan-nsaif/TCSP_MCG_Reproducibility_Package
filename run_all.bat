@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
  if errorlevel 1 goto failure
)

call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
if errorlevel 1 goto failure
pip install -r requirements.txt
if errorlevel 1 goto failure

python -m pytest -q
if errorlevel 1 goto failure

python -m src.cli run-all
if errorlevel 1 goto failure

echo SUCCESS: TCSP-MCG reproducibility package completed.
exit /b 0

:failure
echo FAILURE: TCSP-MCG reproducibility package did not complete.
exit /b 1
