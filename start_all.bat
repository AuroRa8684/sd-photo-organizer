@echo off
chcp 65001 >nul
echo ========================================
echo   SD Photo Organizer 一键启动
echo ========================================
echo.
echo 正在启动后端服务...
start "后端服务" cmd /k "cd /d %~dp0backend && .venv\Scripts\activate && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 2 >nul

echo 正在启动前端服务...
start "前端服务" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo   服务已启动！
echo   后端: http://127.0.0.1:8000
echo   前端: http://127.0.0.1:5173
echo ========================================
echo.
timeout /t 3
