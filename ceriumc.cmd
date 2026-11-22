@echo off
setlocal
set "CERIUM_ROOT=%~dp0"
set "PYTHONPATH=%CERIUM_ROOT%src;%PYTHONPATH%"

where python >nul 2>nul
if errorlevel 1 (
  py -m ceriumc %*
) else (
  python -m ceriumc %*
)
