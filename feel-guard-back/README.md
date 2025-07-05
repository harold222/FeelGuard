# Feel Guard Backend API

API REST para el sistema Feel Guard - Monitoreo de temperatura y bienestar personal.

## Características

- 🔐 Autenticación JWT
- 📊 Gestión de lecturas de temperatura
- 🚨 Sistema de alertas automáticas
- 👥 Gestión de usuarios
- 📈 Estadísticas en tiempo real
- 🔒 Seguridad con contraseñas hasheadas

## Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para base de datos
- **Pydantic** - Validación de datos
- **JWT** - Autenticación con tokens
- **SQLite** - Base de datos (configurable para PostgreSQL)

## Instalación

1. **Clonar el repositorio**
```bash
cd feel-guard-back
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp env.example .env
# Editar .env con tus configuraciones
```

5. **Inicializar la base de datos**
```bash
python init_db.py
```

6. **Ejecutar el servidor**
```bash
python main.py
```

## Endpoints de la API

### Autenticación
- `POST /api/auth/register` - Registrar nuevo usuario
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/me` - Obtener información del usuario actual

### Temperatura
- `POST /api/temperature/` - Crear nueva lectura de temperatura
- `GET /api/temperature/` - Obtener lecturas de temperatura
- `GET /api/temperature/stats` - Obtener estadísticas
- `GET /api/temperature/alerts` - Obtener alertas
- `PUT /api/temperature/alerts/{alert_id}/resolve` - Resolver alerta
- `GET /api/temperature/recent` - Obtener lecturas recientes

### Usuarios
- `GET /api/users/` - Listar usuarios (solo admin)
- `GET /api/users/{user_id}` - Obtener usuario específico
- `PUT /api/users/{user_id}` - Actualizar usuario
- `DELETE /api/users/{user_id}` - Eliminar usuario (solo admin)

## Documentación de la API

Una vez que el servidor esté ejecutándose, puedes acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Usuarios por defecto

Después de ejecutar `init_db.py`, se crean automáticamente:

### Administrador
- Email: `admin@feelguard.com`
- Contraseña: `admin123`

### Usuario de prueba
- Email: `test@feelguard.com`
- Contraseña: `test123`

## Estructura del proyecto

```
feel-guard-back/
├── main.py                 # Punto de entrada de la aplicación
├── init_db.py             # Script de inicialización de BD
├── requirements.txt       # Dependencias de Python
├── env.example           # Variables de entorno de ejemplo
├── models/               # Modelos de base de datos
│   ├── __init__.py
│   ├── database.py       # Configuración de BD
│   ├── user.py          # Modelo de usuario
│   └── temperature.py   # Modelos de temperatura
├── schemas/              # Esquemas Pydantic
│   ├── __init__.py
│   ├── user.py          # Esquemas de usuario
│   └── temperature.py   # Esquemas de temperatura
├── routes/               # Routers de la API
│   ├── __init__.py
│   ├── auth.py          # Endpoints de autenticación
│   ├── temperature.py   # Endpoints de temperatura
│   └── users.py         # Endpoints de usuarios
└── utils/                # Utilidades
    ├── __init__.py
    └── auth.py          # Utilidades de autenticación
```

## Configuración de producción

Para producción, se recomienda:

1. Cambiar `SECRET_KEY` por una clave segura
2. Usar PostgreSQL en lugar de SQLite
3. Configurar HTTPS
4. Implementar rate limiting
5. Configurar logging apropiado

## Desarrollo

Para desarrollo local:

```bash
# Ejecutar con recarga automática
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Licencia

Este proyecto es parte del diplomado Feel Guard. 