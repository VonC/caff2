@echo off
REM This script deliberately leaves the project virtualenv active in cmd.exe.
for %%i in ("%~dp0.") do set "PRJ_DIR=%%~fi"
for %%i in ("%PRJ_DIR%") do set "PRJ_DIR_NAME=%%~nxi"

doskey r="%PRJ_DIR%\run.bat" $*
doskey fsenv=set "CAFF2_ENV_READY=" ^& "%PRJ_DIR%\senv.bat" $*

REM Re-activate even when a child console inherits the setup guard.
if "%CAFF2_ENV_READY%"=="%PRJ_DIR%" if exist "%PRJ_DIR%\.venv\Scripts\activate.bat" (
  call "%PRJ_DIR%\.venv\Scripts\activate.bat"
  exit /b 0
)

REM Optional private package index and certificate settings stay untracked.
if exist "%PRJ_DIR%\senv.local.bat" (
  call "%PRJ_DIR%\senv.local.bat"
  if errorlevel 1 exit /b 5
)
if not defined UV_INDEX_URL if defined PYPI_HOST set "UV_INDEX_URL=https://%PYPI_HOST%"
if defined UV_INDEX_URL if not defined PIP_INDEX_URL set "PIP_INDEX_URL=%UV_INDEX_URL%"
if defined UV_EXTRA_INDEX_URL if not defined PIP_EXTRA_INDEX_URL set "PIP_EXTRA_INDEX_URL=%UV_EXTRA_INDEX_URL%"
if defined UV_CERT if not exist "%UV_CERT%" set "UV_CERT="
if defined UV_CERT if not defined PIP_CERT set "PIP_CERT=%UV_CERT%"
if defined UV_CERT if not defined SSL_CERT_FILE set "SSL_CERT_FILE=%UV_CERT%"

if exist "%PRJ_DIR%\.venv\Scripts\activate.bat" goto :activate
python -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>&1
if errorlevel 1 (
  echo ERROR: Install Python 3.10 or newer with venv and pip, and add python to PATH.
  exit /b 3
)
echo Creating the project Python environment...
python -m venv "%PRJ_DIR%\.venv"
if errorlevel 1 exit /b 3

:activate
call "%PRJ_DIR%\.venv\Scripts\activate.bat"
if errorlevel 1 exit /b 3
"%PRJ_DIR%\.venv\Scripts\python.exe" -c "import sys; sys.exit(sys.version_info < (3, 10))"
if errorlevel 1 (
  echo ERROR: Recreate .venv with Python 3.10 or newer.
  exit /b 3
)
"%PRJ_DIR%\.venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r "%PRJ_DIR%\requirements.txt"
if errorlevel 1 exit /b 3

REM Optional maintainer integration; uses llm-shared's own Python for hooks.
"%PRJ_DIR%\.venv\Scripts\python.exe" "%PRJ_DIR%\tools\install_sensitive_hooks.py"
if errorlevel 1 exit /b 6

set "NO_MORE_SENV_%PRJ_DIR_NAME%=true"
set "CAFF2_ENV_READY=%PRJ_DIR%"
echo Caff2 environment ready.
exit /b 0
