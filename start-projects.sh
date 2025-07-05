#!/bin/bash

echo "========================================"
echo "   Feel Guard - Iniciando Proyectos"
echo "========================================"
echo

echo "[1/3] Iniciando Backend (FastAPI)..."
cd feel-guard-back
gnome-terminal --title="Feel Guard Backend" -- bash -c "python run.py; exec bash" &
cd ..

echo "[2/3] Esperando 3 segundos para que el backend inicie..."
sleep 3

echo "[3/3] Iniciando Frontend (React)..."
cd feel-guard-front
gnome-terminal --title="Feel Guard Frontend" -- bash -c "npm run dev; exec bash" &
cd ..

echo
echo "========================================"
echo "   Proyectos iniciados correctamente"
echo "========================================"
echo
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "Docs API: http://localhost:8000/docs"
echo
echo "Presiona Enter para cerrar..."
read 