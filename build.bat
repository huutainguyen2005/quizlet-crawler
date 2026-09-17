@echo off
setlocal

cd /d "%~dp0"

echo ================================================
echo Quizlet Crawler - Build
echo ================================================

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] .venv not found.
    echo Run: py -3.14 -m venv .venv
    exit /b 1
)

call ".venv\Scripts\activate.bat"

set "PLAYWRIGHT_BROWSERS_PATH=0"

echo [INFO] Installing Python dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo [INFO] Installing Playwright Chromium locally...
python -m playwright install chromium
if errorlevel 1 exit /b 1

echo [INFO] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

if exist QuizletCrawler.spec.tmp del /q QuizletCrawler.spec.tmp

echo [INFO] Building QuizletCrawler.exe...
python -m PyInstaller --noconfirm --clean QuizletCrawler.spec
if errorlevel 1 exit /b 1

echo.
echo ================================================
echo [SUCCESS] Build completed.
echo Output: dist\QuizletCrawler\QuizletCrawler.exe
echo ================================================
endlocal
