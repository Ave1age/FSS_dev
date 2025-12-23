@echo off
title 局域网文件共享服务
echo 正在启动文件共享服务...
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到 Python，请先安装 Python 并添加到环境变量。
    pause
    exit
)

:: Install dependencies
echo 正在检查依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 依赖安装失败。
    pause
    exit
)

echo.
echo ==========================================
echo       服务启动成功！
echo ==========================================
echo.

:: Run the app
echo.
echo 提示: 如果其他设备无法连接，请尝试临时关闭防火墙或允许 python.exe 联网。
echo.
python app.py

pause
