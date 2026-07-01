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
echo This will rebuild database "%MYSQL_DATABASE%".
echo Existing data in the same database will be overwritten by mysql\schema.sql.
choice /C YN /M "Continue"
if errorlevel 2 (
  echo Cancelled.
  pause
  exit /b 1
)

set "MYSQL_AUTH=--host=%MYSQL_HOST% --port=%MYSQL_PORT% --user=%MYSQL_USER% --default-character-set=utf8mb4"
if not "%MYSQL_PASSWORD%"=="" set "MYSQL_AUTH=%MYSQL_AUTH% --password=%MYSQL_PASSWORD%"

echo.
echo [1/2] Running mysql\schema.sql ...
mysql %MYSQL_AUTH% < "mysql\schema.sql"
if errorlevel 1 goto fail

echo.
echo [2/2] Running mysql\seed_data.sql ...
mysql %MYSQL_AUTH% "%MYSQL_DATABASE%" < "mysql\seed_data.sql"
if errorlevel 1 goto fail

echo.
echo Database initialized successfully.
echo Next step: double-click start_mysql_app.bat to open the platform.
pause
exit /b 0

:fail
echo.
echo Database initialization failed.
echo Please check:
echo 1. MySQL service is running.
echo 2. mysql command is available in PATH.
echo 3. Username and password are correct.
pause
exit /b 1
