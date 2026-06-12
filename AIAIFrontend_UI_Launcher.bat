@echo off
if "%AIAI_LAUNCHER_TEST%"=="1" exit /b 0
chcp 65001 >nul
setlocal EnableExtensions

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"
if /I "%~1"=="--test-exit" exit /b 0

title AIAIFrontend UI Launcher
color 0B

:menu
cls
echo.
echo  ================================================================
echo    AIAIFrontend UI - AI 短片创作控制台
echo  ================================================================
echo.
echo    [1] 启动 Next.js 主控制台       http://127.0.0.1:3000
echo    [2] 启动 Streamlit 中转测试台   http://127.0.0.1:8501
echo    [3] 同时启动两个界面
echo    [4] 检查并安装依赖
echo    [0] 退出
echo.
set /p "CHOICE=请选择要执行的操作: "

if "%CHOICE%"=="1" goto start_web
if "%CHOICE%"=="2" goto start_streamlit
if "%CHOICE%"=="3" goto start_all
if "%CHOICE%"=="4" goto check_all
if "%CHOICE%"=="0" goto done

echo.
echo  请输入 0-4 之间的数字。
pause
goto menu

:start_web
call :ensure_node
if errorlevel 1 goto wait_menu
echo.
echo  正在启动 Next.js 主控制台...
start "AIAIFrontend UI - Next.js" /D "%PROJECT_DIR%" cmd /k npm run dev -- --hostname 127.0.0.1 --port 3000
timeout /t 4 /nobreak >nul
start "" "http://127.0.0.1:3000"
goto launched

:start_streamlit
call :ensure_python
if errorlevel 1 goto wait_menu
echo.
echo  正在启动 Streamlit AIAI 中转测试台...
start "AIAIFrontend UI - Streamlit" /D "%PROJECT_DIR%" cmd /k python -m streamlit run aiai_seedance2_frontend.py --server.address 127.0.0.1 --server.port 8501
timeout /t 4 /nobreak >nul
start "" "http://127.0.0.1:8501"
goto launched

:start_all
call :ensure_node
if errorlevel 1 goto wait_menu
call :ensure_python
if errorlevel 1 goto wait_menu
echo.
echo  正在同时启动两个界面...
start "AIAIFrontend UI - Next.js" /D "%PROJECT_DIR%" cmd /k npm run dev -- --hostname 127.0.0.1 --port 3000
start "AIAIFrontend UI - Streamlit" /D "%PROJECT_DIR%" cmd /k python -m streamlit run aiai_seedance2_frontend.py --server.address 127.0.0.1 --server.port 8501
timeout /t 5 /nobreak >nul
start "" "http://127.0.0.1:3000"
start "" "http://127.0.0.1:8501"
goto launched

:check_all
echo.
call :ensure_node
if errorlevel 1 goto wait_menu
call :ensure_python
if errorlevel 1 goto wait_menu
echo.
echo  依赖检查完成。
goto wait_menu

:ensure_node
where node >nul 2>nul
if errorlevel 1 (
  echo.
  echo  [缺少] 未找到 Node.js。请安装 Node.js LTS 后再启动主控制台。
  exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
  echo.
  echo  [缺少] 未找到 npm。请检查 Node.js 安装。
  exit /b 1
)

if not exist "%PROJECT_DIR%node_modules" (
  echo.
  echo  未检测到 node_modules，正在执行 npm install...
  call npm install
  if errorlevel 1 (
    echo.
    echo  npm install 失败，请查看上方错误。
    exit /b 1
  )
)
exit /b 0

:ensure_python
where python >nul 2>nul
if errorlevel 1 (
  echo.
  echo  [缺少] 未找到 Python。请安装 Python 并加入 PATH 后再启动测试台。
  exit /b 1
)

python -c "import streamlit, requests" >nul 2>nul
if errorlevel 1 (
  echo.
  echo  未检测到 streamlit / requests，正在安装 requirements.txt...
  python -m pip install -r requirements.txt
  if errorlevel 1 (
    echo.
    echo  Python 依赖安装失败，请查看上方错误。
    exit /b 1
  )
)
exit /b 0

:launched
echo.
echo  已打开浏览器。如果页面还在加载，请等待服务窗口完成启动。
goto wait_menu

:wait_menu
echo.
pause
goto menu

:done
exit /b 0
