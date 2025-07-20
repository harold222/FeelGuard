@echo off
echo ========================================
echo    Subiendo Feel Guard a Docker Hub
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

echo [1/4] Construyendo imágenes con nombres específicos...
docker-compose build --no-cache
if errorlevel 1 (
    echo ERROR: Fallo en la construcción de las imágenes
    pause
    exit /b 1
)

echo.
echo [2/4] Verificando que las imágenes se construyeron correctamente...
docker images | findstr "2harold2/feel-guard"
if errorlevel 1 (
    echo ERROR: No se encontraron las imágenes esperadas
    echo Verificando todas las imágenes...
    docker images
    pause
    exit /b 1
)

echo.
echo [3/4] Iniciando sesión en Docker Hub...
echo Por favor ingresa tus credenciales de Docker Hub cuando se solicite:
docker login
if errorlevel 1 (
    echo ERROR: Fallo en el login de Docker Hub
    echo Verifica tus credenciales e intenta nuevamente
    pause
    exit /b 1
)

echo.
echo [4/4] Subiendo imágenes a Docker Hub...
echo Subiendo backend...
docker push 2harold2/feel-guard-backend:v1.0.0
if errorlevel 1 (
    echo ERROR: Fallo al subir la imagen del backend
    pause
    exit /b 1
)

echo Subiendo frontend...
docker push 2harold2/feel-guard-frontend:v1.0.0
if errorlevel 1 (
    echo ERROR: Fallo al subir la imagen del frontend
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Imágenes subidas exitosamente
echo ========================================
echo.
echo Backend:  2harold2/feel-guard-backend:v1.0.0
echo Frontend: 2harold2/feel-guard-frontend:v1.0.0
echo.
echo Para usar las imágenes desde Docker Hub:
echo   docker pull 2harold2/feel-guard-backend:v1.0.0
echo   docker pull 2harold2/feel-guard-frontend:v1.0.0
echo.
pause 