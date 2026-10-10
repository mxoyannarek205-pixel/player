@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Запускаю сайт: http://localhost:8765/
echo Чтобы остановить, закрой это окно.
start "" http://localhost:8765/
where py >nul 2>nul
if %errorlevel%==0 ( py serve.py & goto :eof )
where python >nul 2>nul
if %errorlevel%==0 ( python serve.py & goto :eof )
echo.
echo Python не найден. Установи его с python.org и запусти start.bat снова.
pause
