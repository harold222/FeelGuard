from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import uvicorn
from dotenv import load_dotenv
import os
from fastapi.staticfiles import StaticFiles

# Cargar variables de entorno
load_dotenv()

# Crear instancia de FastAPI
app = FastAPI(
    title="Feel Guard API",
    description="API para el sistema Feel Guard - Asistente de salud mental",
    version="2.0.0"
)

# Configurar CORS ANTES de cualquier endpoint
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Crea un endpoint para permitir las peticiones OPTIONS
@app.options("/{path:path}")
async def options_handler(path: str):
    return Response(
        status_code=200,
        headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH", "Access-Control-Allow-Headers": "*", "Access-Control-Max-Age": "86400"}
    )

# Importar routers DESPUÉS de configurar CORS
from routes import auth, users, ai, registro

host = os.getenv("HOST", "0.0.0.0")
port = int(os.getenv("PORT", 8000))

# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(registro.router, tags=["Registro"])

# Crear la carpeta uploads si no existe
os.makedirs("uploads", exist_ok=True)

# Servir archivos de audio (uploads) de forma estática
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    ) 