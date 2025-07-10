@echo off

for %%i in ("%~dp0") do SET "run_dir=%%~fi"
set "run_dir=%run_dir:~0,-1%"

REM ========================================
REM INITIALIZATION
REM ========================================
set "SKIP_LOCAL=1"
call "%run_dir%\senv.bat"
if errorlevel 1 (
  echo Unable to set up the environment.
  exit /b 1
)

%_task% "Must access CAFF project in '%PRJ_DIR%'"
pushd "%PRJ_DIR%"
if errorlevel 1 (
  %_fatal% "Unable to access project directory: '%PRJ_DIR%'" 5
)
%_task% "Must run CAFF script in '%PRJ_DIR%'"
call python caff2.py
set "err=%errorlevel%"
if "%err%"=="2" (
  %_error% "Another instance is already running."
  goto :eof
)
if not "%err%"=="0" (
  %_fatal% "Unable to run caff2.py" %err%
)
%_ok% "CAFF script executed successfully."
popd
if errorlevel 1 (
  %_fatal% "Unable to return to previous directory." 7
)


goto:eof

:call_echos_stack
if not defined ECHOS_STACK ( set "CURRENT_SCRIPT=%~nx0" & goto:eof ) else ( call "%project_dir%\tools\batcolors\echos.bat" :stack %~nx0 )
goto:eof
