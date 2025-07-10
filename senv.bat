@echo off

for %%i in ("%~dp0") do SET "PRJ_DIR=%%~fi"
set "PRJ_DIR=%PRJ_DIR:~0,-1%"
for %%i in ("%PRJ_DIR%") do SET "PRJ_DIR_NAME=%%~nxi"

if defined NO_MORE_SENV_%PRJ_DIR_NAME% (
  exit /b 0
  goto:eof
)

doskey r="%PRJ_DIR%\run.bat" $*
doskey fsenv=set "NO_MORE_SENV_%PRJ_DIR_NAME%=" ^& "%PRJ_DIR%\senv.bat"

if not exist "%PRJ_DIR%\batcolors\echos.bat" (
  echo Error: The 'echos.bat' script is missing in the project tools directory.
  exit /b 1
)
call  "%PRJ_DIR%\batcolors\echos_macros.bat" export
%_task% "Must access CAFF project in '%PRJ_DIR%'"
pushd "%PRJ_DIR%"
if errorlevel 1 (
  %_fatal% "Unable to access project directory: %PRJ_DIR%" 2
)
%_ok% "Accessed project directory: '%PRJ_DIR%'"
%_task% "Must set venv for Python scripts in '%PRJ_DIR%'"
call switchpy 3.13.0 local
if errorlevel 1 (
  %_fatal% "Unable to switch to local Python environment." 3
)
call  "%PRJ_DIR%\batcolors\echos_macros.bat" export
%_ok% "Switched to local Python environment."
%_task% "Must restore previous folder"
popd
if errorlevel 1 (
  %_fatal% "Unable to return to previous directory." 4
)
%_ok% "Returned to previous directory."

REM Set project-specific flag when done
set "NO_MORE_SENV_%PRJ_DIR_NAME%=true"
goto:eof

:call_echos_stack
if not defined ECHOS_STACK ( set "CURRENT_SCRIPT=%~nx0" & goto:eof ) else ( call "%project_dir%\tools\batcolors\echos.bat" :stack %~nx0 )
goto:eof
