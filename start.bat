@echo off
title SmartSign by Harsh Manglam
color 0A
cls
echo.
echo ==========================================
echo  SmartSign - by Harsh Manglam
echo  CRPF Public School Rohini - Class 12D
echo ==========================================
echo.
echo [~] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 goto no_python
echo [OK] Python found.
goto python_ok
:no_python
echo [!] Python not found. Downloading...
curl -L -o "%TEMP%\py_setup.exe" "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
if %errorlevel% neq 0 goto dl_fail
"%TEMP%\py_setup.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
echo [OK] Python installed. Close this and run start.bat again.
pause
exit /b 0
:dl_fail
echo [ERROR] Cannot download Python. Check internet.
pause
exit /b 1
:python_ok
echo.
echo [~] Installing packages (2-3 mins first time)...
python -m pip install --upgrade pip --quiet
python -m pip install flask --quiet
python -m pip install flask-cors --quiet
python -m pip install pillow --quiet
python -m pip install google-generativeai --quiet
python -m pip install mss --quiet
python -m pip install requests --quiet
echo [~] Verifying flask...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 goto flask_fail
echo [OK] All packages ready.
goto flask_ok
:flask_fail
echo [!] Flask failed. Trying user install...
python -m pip install flask --user --quiet
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 goto flask_fail2
echo [OK] Flask ready via user install.
goto flask_ok
:flask_fail2
echo [ERROR] Flask could not install.
echo SOLUTION: Right-click start.bat and Run as Administrator
pause
exit /b 1
:flask_ok
echo.
echo [~] Checking Tesseract OCR...
if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" goto tess_found
if exist "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe" goto tess_found
echo [!] Tesseract not found. Trying winget...
winget install --id UB-Mannheim.TesseractOCR -e --silent --accept-source-agreements --accept-package-agreements >nul 2>&1
if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" goto tess_found
echo [!] Tesseract skipped. Running in Vision-Only mode. Still works!
goto tess_done
:tess_found
echo [OK] Tesseract ready.
set "PATH=%PATH%;C:\Program Files\Tesseract-OCR;C:\Program Files (x86)\Tesseract-OCR"
python -m pip install pytesseract --quiet
:tess_done
echo.
echo [~] Checking API key in config.json...
findstr /C:"PASTE_YOUR_GEMINI_KEY" config.json >nul 2>&1
if %errorlevel% equ 0 (
echo.
echo ============================================================
echo  WARNING - Gemini API key missing!
echo  Open config.json in Notepad and add your key.
echo  Get free key: aistudio.google.com/app/apikey
echo ============================================================
echo.
pause
)
echo [~] Stopping old Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo [~] Starting SmartSign Brain...
start /B python brain.py
echo [~] Waiting for server...
timeout /t 6 /nobreak >nul
:ping_loop
curl -s "http://localhost:5050/ping" >nul 2>&1
if %errorlevel% neq 0 (
timeout /t 2 /nobreak >nul
goto ping_loop
)
echo [OK] Brain is running!
echo [~] Opening browser...
start msedge "http://localhost:5050" >nul 2>&1
if %errorlevel% neq 0 start chrome "http://localhost:5050" >nul 2>&1
if %errorlevel% neq 0 start "" "http://localhost:5050"
echo.
echo ==========================================
echo  SmartSign is RUNNING!
echo  Keep this window open. Minimize it.
echo  Press Ctrl+C when school is over.
echo ==========================================
echo.
:keepalive
timeout /t 20 /nobreak >nul
curl -s "http://localhost:5050/ping" >nul 2>&1
if %errorlevel% neq 0 (
echo [!] Brain stopped. Restarting...
start /B python brain.py
timeout /t 5 /nobreak >nul
)
goto keepalive
