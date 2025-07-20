@echo off
echo ========================================
echo    Iniciando Feel Guard con Docker
echo ========================================
echo.

REM Verificar si Docker está instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker no está instalado o no está en el PATH
    echo Por favor instala Docker Desktop desde: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Verificar si Docker está ejecutándose
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker no está ejecutándose
    echo Por favor inicia Docker Desktop
    pause
    exit /b 1
)

echo [1/4] Construyendo imágenes de Docker...
docker-compose build --no-cache
if errorlevel 1 (
    echo ERROR: Fallo en la construcción de las imágenes
    echo Revisa los logs anteriores para más detalles
    pause
    exit /b 1
)

echo.
echo [2/4] Iniciando servicios...
docker-compose up -d
if errorlevel 1 (
    echo ERROR: Fallo al iniciar los servicios
    echo Revisa los logs anteriores para más detalles
    pause
    exit /b 1
)

echo.
echo [3/4] Esperando que los servicios estén listos...
timeout /t 10 /nobreak > nul

echo.
echo [4/4] Verificando estado de los servicios...
docker-compose ps

echo.
echo ========================================
echo    Servicios iniciados correctamente
echo ========================================
echo.
echo Frontend:  http://localhost
echo Backend:   http://localhost:8000
echo API Docs:  http://localhost:8000/docs
echo Database:  localhost:5432
echo.
echo Para ver los logs:
echo   docker-compose logs -f
echo.
echo Para detener los servicios:
echo   docker-compose down
echo.
pause 