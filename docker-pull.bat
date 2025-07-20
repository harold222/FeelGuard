@echo off
echo ========================================
echo    Descargando Feel Guard desde Docker Hub
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

echo [1/3] Descargando imagen del backend...
docker pull 2harold2/feel-guard-backend:v1.0.0
if errorlevel 1 (
    echo ERROR: Fallo al descargar la imagen del backend
    pause
    exit /b 1
)

echo.
echo [2/3] Descargando imagen del frontend...
docker pull 2harold2/feel-guard-frontend:v1.0.0
if errorlevel 1 (
    echo ERROR: Fallo al descargar la imagen del frontend
    pause
    exit /b 1
)

echo.
echo [3/3] Iniciando servicios con imágenes descargadas...
docker-compose up -d
if errorlevel 1 (
    echo ERROR: Fallo al iniciar los servicios
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Servicios iniciados exitosamente
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