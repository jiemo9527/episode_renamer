@echo off
setlocal enabledelayedexpansion

:: ý���ļ���������ǿ���� - ע���˵������ű�

:: ��ȡ��ǰ�ű����ڵ�����·��
set "APP_PATH=%~dp0ý���ļ���������ǿ����.exe"

:: ����ԱȨ�޼��
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if %errorlevel% neq 0 (
    echo ���Թ���ԱȨ�����д˽ű�
    pause
    exit /b 1
)

:: �������Ƿ����
if not exist "%APP_PATH%" (
    echo δ�ҵ�ý���ļ���������ǿ����.exe
    echo ��ȷ���ó�����ű�λ��ͬһĿ¼
    pause
    exit /b 1
)

:: �û�ѡ��˵�
:MENU
cls
echo ===============================
echo   ý���ļ���������ǿ���� - �˵�
echo ===============================
echo 1. ����Ҽ��˵�
echo 2. ɾ���Ҽ��˵�
echo 3. �˳�
echo ===============================
set /p choice="��ѡ�������1-3����"

if "%choice%"=="1" goto ADD_MENU
if "%choice%"=="2" goto REMOVE_MENU
if "%choice%"=="3" exit /b 0

:: ��Ӳ˵�
:ADD_MENU
:: Ϊ�ļ�������Ҽ��˵���
reg add "HKEY_CLASSES_ROOT\Directory\shell\OpenWithMediaFileRenamer" /ve /d "ý���ļ���������ǿ����" /f
reg add "HKEY_CLASSES_ROOT\Directory\shell\OpenWithMediaFileRenamer" /v "Icon" /d "%APP_PATH%" /f
reg add "HKEY_CLASSES_ROOT\Directory\shell\OpenWithMediaFileRenamer\command" /ve /d "\"%APP_PATH%\" \"%%1\"" /f

:: Ϊ�����ļ�����Ҽ��˵���
reg add "HKEY_CLASSES_ROOT\*\shell\OpenWithMediaFileRenamer" /ve /d "ý���ļ���������ǿ����" /f
reg add "HKEY_CLASSES_ROOT\*\shell\OpenWithMediaFileRenamer" /v "Icon" /d "%APP_PATH%" /f
reg add "HKEY_CLASSES_ROOT\*\shell\OpenWithMediaFileRenamer\command" /ve /d "\"%APP_PATH%\" \"%%V\"" /f

echo �Ҽ��˵��ѳɹ���ӣ�
pause
goto MENU

:: ɾ���˵�
:REMOVE_MENU
:: ɾ���ļ����Ҽ��˵���
reg delete "HKEY_CLASSES_ROOT\Directory\shell\OpenWithMediaFileRenamer" /f
:: ɾ���ļ��Ҽ��˵���
reg delete "HKEY_CLASSES_ROOT\*\shell\OpenWithMediaFileRenamer" /f

echo �Ҽ��˵��ѳɹ�ɾ����
pause
goto MENU