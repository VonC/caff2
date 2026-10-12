@echo off
setlocal
call "%~dp0senv.bat"
if errorlevel 1 (
  echo Unable to set up the environment.
  exit /b 1
)
pushd "%~dp0."
if errorlevel 1 exit /b 5
"%~dp0.venv\Scripts\python.exe" "%~dp0caff2.py" %*
set "caff2_exit=%errorlevel%"
popd
if "%caff2_exit%"=="2" echo Another instance is already running.
if not "%caff2_exit%"=="0" if not "%caff2_exit%"=="2" echo Unable to run caff2.py.
exit /b %caff2_exit%
