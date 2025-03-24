@echo off
setlocal enabledelayedexpansion

:: 媒体文件重命名增强助手 - 注册表菜单项管理脚本

:: 获取当前脚本所在的完整路径
set "APP_PATH=%~dp0媒体文件重命名增强助手.exe"

:: 管理员权限检查
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if %errorlevel% neq 0 (
    echo 请以管理员权限运行此脚本
    pause
    exit /b 1
)

:: 检查程序是否存在
if not exist "%APP_PATH%" (
    echo 未找到媒体文件重命名增强助手.exe
    echo 请确保该程序与脚本位于同一目录
    pause
    exit /b 1
)

:: 用户选择菜单
:MENU
cls
echo ===============================
echo   媒体文件重命名增强助手 - 菜单
echo ===============================
echo 1. 添加右键菜单
echo 2. 删除右键菜单
echo 3. 退出
echo ===============================
set /p choice="请选择操作（1-3）："

if "%choice%"=="1" goto ADD_MENU
if "%choice%"=="2" goto REMOVE_MENU
if "%choice%"=="3" exit /b 0

:: 添加菜单
:ADD_MENU
:: 为文件夹添加右键菜单项
reg add "HKEY_CLASSES_ROOT\Directory\shell\OpenWithMediaFileRenamer" /ve /d "媒体文件重命名增强助手" /f
reg add "HKEY_CLASSES_ROOT\Directory\shell\OpenWithMediaFileRenamer" /v "Icon" /d "%APP_PATH%" /f
reg add "HKEY_CLASSES_ROOT\Directory\shell\OpenWithMediaFileRenamer\command" /ve /d "\"%APP_PATH%\" \"%%1\"" /f

:: 为所有文件添加右键菜单项
reg add "HKEY_CLASSES_ROOT\*\shell\OpenWithMediaFileRenamer" /ve /d "媒体文件重命名增强助手" /f
reg add "HKEY_CLASSES_ROOT\*\shell\OpenWithMediaFileRenamer" /v "Icon" /d "%APP_PATH%" /f
reg add "HKEY_CLASSES_ROOT\*\shell\OpenWithMediaFileRenamer\command" /ve /d "\"%APP_PATH%\" \"%%V\"" /f

echo 右键菜单已成功添加！
pause
goto MENU

:: 删除菜单
:REMOVE_MENU
:: 删除文件夹右键菜单项
reg delete "HKEY_CLASSES_ROOT\Directory\shell\OpenWithMediaFileRenamer" /f
:: 删除文件右键菜单项
reg delete "HKEY_CLASSES_ROOT\*\shell\OpenWithMediaFileRenamer" /f

echo 右键菜单已成功删除！
pause
goto MENU