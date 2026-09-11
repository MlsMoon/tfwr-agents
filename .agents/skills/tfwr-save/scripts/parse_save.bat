@echo off
setlocal EnableExtensions
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0parse_save.ps1" %*
exit /b %ERRORLEVEL%
