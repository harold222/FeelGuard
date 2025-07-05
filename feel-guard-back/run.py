#!/usr/bin/env python3
"""
Script para ejecutar el servidor de desarrollo de Feel Guard Backend
"""

import uvicorn
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

if __name__ == "__main__":
    # Configuración del servidor
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print("🚀 Iniciando Feel Guard Backend API...")
    print(f"📍 Servidor: http://{host}:{port}")
    print("📚 Documentación: http://localhost:8000/docs")
    print("🔧 Presiona Ctrl+C para detener el servidor")
    print("-" * 50)
    
    # Ejecutar servidor
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    ) 