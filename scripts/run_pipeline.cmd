@echo off
setlocal
if "%~2"=="" (
  echo Usage: run_pipeline.cmd PROJECT_DIR STORYBOARD_JSON
  exit /b 2
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_pipeline.ps1" -ProjectDir "%~1" -Storyboard "%~2"
exit /b %ERRORLEVEL%
