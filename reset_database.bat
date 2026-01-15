@echo off
chcp 65001 >nul
echo ========================================
echo   重置数据库 (清空所有数据)
echo ========================================
echo.
echo 警告: 此操作将删除所有照片数据和缩略图！
echo.

REM 检查后端是否在运行
netstat -ano | findstr ":8000" >nul 2>&1
if %errorlevel%==0 (
    echo [!] 检测到后端服务正在运行 (端口8000)
    echo [!] 请先关闭后端服务窗口，然后重新运行此脚本
    echo.
    pause
    exit /b 1
)

set /p confirm=确定继续吗？(Y/N): 
if /i "%confirm%"=="Y" (
    echo.
    echo 正在清理...
    
    if exist "%~dp0backend\data\photos.db" (
        del /f "%~dp0backend\data\photos.db"
        echo √ 已删除数据库
    ) else (
        echo - 数据库不存在
    )
    
    if exist "%~dp0backend\storage\thumbs\*" (
        del /f /q "%~dp0backend\storage\thumbs\*"
        echo √ 已清空缩略图
    ) else (
        echo - 缩略图目录为空
    )
    
    echo.
    echo ======== 重置完成！========
    echo 现在可以启动后端服务了
) else (
    echo 已取消操作
)
echo.
pause
