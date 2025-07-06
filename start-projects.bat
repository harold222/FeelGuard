@echo off

REM [0/3] Instalar dependencias Backend (Python)
echo Instalando dependencias de Python (feel-guard-back/requirements.txt)...
cd feel-guard-back
python -m venv venv
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

REM [1/3] Iniciando Backend (FastAPI)...
echo Iniciando Backend (FastAPI)...
cd feel-guard-back
start "Feel Guard Backend" cmd /k "call venv\Scripts\activate && python main.py"
cd ..

REM [2/3] Esperando 3 segundos para que el backend inicie...
timeout /t 3 /nobreak > nul

REM [3/3] Iniciando Frontend (React)...
echo Iniciando Frontend (React)...
cd feel-guard-front
start "Feel Guard Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo    Proyectos iniciados correctamente
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo Docs API: http://localhost:8000/docs