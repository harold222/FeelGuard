@echo off
echo ========================================
echo    Reconstruyendo Feel Guard con Docker
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

echo [1/6] Deteniendo servicios existentes...
docker-compose down

echo.
echo [2/6] Eliminando contenedores y volúmenes...
docker-compose down -v

echo.
echo [3/6] Limpiando imágenes no utilizadas...
docker image prune -f

echo.
echo [4/6] Eliminando imágenes específicas del proyecto...
docker rmi feel-guard-backend feel-guard-frontend 2>nul
docker rmi diplomado-backend diplomado-frontend 2>nul

echo.
echo [5/6] Construyendo imágenes desde cero...
docker-compose build --no-cache
if errorlevel 1 (
    echo ERROR: Fallo en la construcción de las imágenes
    echo Revisa los logs anteriores para más detalles
    pause
    exit /b 1
)

echo.
echo [6/6] Iniciando servicios...
docker-compose up -d
if errorlevel 1 (
    echo ERROR: Fallo al iniciar los servicios
    echo Revisa los logs anteriores para más detalles
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Reconstrucción completada exitosamente
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