@echo off
setlocal EnableExtensions
chcp 65001 >nul

echo.
echo ============================================================
echo  TFWR Agents Setup
echo ============================================================
echo.
echo  Enter the game SAVE folder, not the Steam install folder.
echo.
echo  Default (press Enter):
echo    %USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced
echo.
echo  Hints:
echo    - Launch the game once so this folder exists.
echo    - Do not use steamapps\common\The Farmer Was Replaced
echo      That is the install folder.
echo    - You can paste the path from File Explorer's address bar.
echo    - After Enter, this repo is copied in and init runs by itself.
echo      No second command.
echo.

set "GAMEROOT="
set /p GAMEROOT=Save path: 
if "%GAMEROOT%"=="" set "GAMEROOT=%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced"

echo.
echo Target: %GAMEROOT%
echo Copying and initializing...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" -GameRoot "%GAMEROOT%" %*
set "ERR=%ERRORLEVEL%"
echo.
if not "%ERR%"=="0" (
    echo [fail] Init did not finish. Check the path above and run setup.bat again.
) else (
    echo [done] Copied into the save folder and finished init.
    echo.
    echo Next:
    echo   1. Open that save folder in Cursor.
    echo   2. In the game, set file watcher = enabled.
    echo   3. python .agents\skills\tfwr-control\scripts\tfwr_control.py run-main
)
echo.
pause
exit /b %ERR%
