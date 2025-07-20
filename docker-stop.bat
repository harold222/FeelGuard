@echo off
echo ========================================
echo    Deteniendo Feel Guard con Docker
echo ========================================
echo.

REM Verificar si Docker está instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker no está instalado o no está en el PATH
    pause
    exit /b 1
)

echo [1/2] Deteniendo servicios...
docker-compose down

echo.
echo [2/2] Limpiando recursos no utilizados...
docker system prune -f

echo.
echo ========================================
echo    Servicios detenidos correctamente
echo ========================================
echo.
echo Para iniciar nuevamente:
echo   docker-start.bat
echo.
pause 