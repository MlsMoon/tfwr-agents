@echo off
setlocal EnableExtensions
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ensure-agent-links.ps1" %*
exit /b %ERRORLEVEL%
