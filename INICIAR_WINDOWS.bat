@echo off
cd /d "%~dp0"
echo ======================================
echo        ALGORA - Interprete web
echo ======================================
echo Abra http://localhost:8000 en su navegador.
echo.
where py >nul 2>nul
if %errorlevel%==0 (
    py app.py
) else (
    python app.py
)
pause
