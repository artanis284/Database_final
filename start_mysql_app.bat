@echo off
setlocal

cd /d "%~dp0"

set "MYSQL_HOST=127.0.0.1"
set "MYSQL_PORT=3306"
set "MYSQL_DATABASE=literature_management"

set /p "MYSQL_USER=MySQL user, default root: "
if "%MYSQL_USER%"=="" set "MYSQL_USER=root"

set /p "MYSQL_PASSWORD=MySQL password, press Enter if empty: "

echo.
echo Starting Literature Management Platform...
echo MySQL: %MYSQL_USER%@%MYSQL_HOST%:%MYSQL_PORT%/%MYSQL_DATABASE%
echo.

set "PYTHON_EXE=python"
where python >nul 2>nul
if errorlevel 1 (
  where py >nul 2>nul
  if errorlevel 1 (
    echo Python was not found. Please install Python 3.10 or above.
    pause
    exit /b 1
  )
  set "PYTHON_EXE=py -3"
)

echo Python: %PYTHON_EXE%
%PYTHON_EXE% -c "import pdfplumber, PyPDF2" >nul 2>nul
if errorlevel 1 (
  echo.
  echo Missing Python dependencies.
  echo Please run:
  echo   %PYTHON_EXE% -m pip install -r requirements.txt
  echo.
  pause
  exit /b 1
)

%PYTHON_EXE% app_mysql.py
pause
