@echo off
setlocal EnableExtensions
chcp 65001 >nul

echo.
echo ============================================================
echo  TFWR Agents 初始化 / Setup
echo ============================================================
echo.
echo  请输入游戏【存档】目录，不是 Steam 安装目录。
echo  Enter the game SAVE folder, not the Steam install folder.
echo.
echo  默认路径 Default (直接回车 / press Enter):
echo    %USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced
echo.
echo  提示 Hints:
echo    - 先启动一次游戏，这个文件夹才会出现。
echo      Launch the game once so this folder exists.
echo    - 不是 steamapps\common\The Farmer Was Replaced
echo      That is the install folder. Do not use it.
echo    - 可以从资源管理器地址栏复制路径后粘贴。
echo      Paste the path from File Explorer's address bar.
echo    - 回车后会自动拷贝本仓库并完成初始化，不用再跑第二步。
echo      After Enter, this folder is copied in and init runs by itself.
echo.

set "GAMEROOT="
set /p GAMEROOT=存档路径 Save path: 
if "%GAMEROOT%"=="" set "GAMEROOT=%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced"

echo.
echo 目标 Target: %GAMEROOT%
echo 正在拷贝并自动初始化... Copying and initializing...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" -GameRoot "%GAMEROOT%" %*
set "ERR=%ERRORLEVEL%"
echo.
if not "%ERR%"=="0" (
    echo [失败] 初始化没有完成。Failed. Check the path above and run setup.bat again.
) else (
    echo [完成] 已拷贝到存档目录，并自动做完初始化。
    echo [done] Copied into the save folder and finished init.
    echo.
    echo 下一步 Next:
    echo   1. 用 Cursor 打开刚才那个存档目录。
    echo      Open that save folder in Cursor.
    echo   2. 游戏里打开 file watcher = enabled。
    echo   3. python .agents\skills\tfwr-control\scripts\tfwr_control.py run-main
)
echo.
pause
exit /b %ERR%
