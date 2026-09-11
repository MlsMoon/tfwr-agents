@echo off
setlocal EnableExtensions
chcp 65001 >nul

echo.
echo ============================================================
echo  TFWR Agents Setup
echo ============================================================
echo.
echo  Language (Enter = en)
echo.
echo    en      English
echo    zh-CN   简体中文
echo    zh-TW   繁體中文
echo    ja      日本語
echo    ko      한국어
echo    de      Deutsch
echo    fr      Français
echo    es      Español
echo    pt-BR   Português
echo    ru      Русский
echo    vi      Tiếng Việt
echo    id      Bahasa Indonesia
echo.

set "LANG="
set /p LANG=Language: 

echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" -Lang "%LANG%" %*
set "ERR=%ERRORLEVEL%"
echo.
pause
exit /b %ERR%
