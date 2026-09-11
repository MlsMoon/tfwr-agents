@echo off
setlocal EnableExtensions
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
python "%~dp0tfwr_control.py" %*
exit /b %ERRORLEVEL%
