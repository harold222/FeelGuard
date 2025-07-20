# Feel Guard - Sistema Multimodal de Monitoreo de Depresión 

Sistema completo para el monitoreo de temperatura y bienestar personal, desarrollado con React (Frontend) y FastAPI (Backend).

## 🚀 Características

### Backend (FastAPI)
- 🔐 Autenticación JWT segura
- 📊 Gestión de lecturas de temperatura
- 🚨 Sistema de alertas automáticas
- 👥 Gestión de usuarios y roles
- 📈 Estadísticas en tiempo real
- 🔒 API REST documentada con Swagger

### Frontend (React + TypeScript)
- 🎨 Interfaz moderna y responsiva
- 🔐 Sistema de autenticación completo
- 📱 Diseño adaptable a dispositivos móviles
- 📊 Visualización de datos en tiempo real
- 🚨 Notificaciones de alertas
- ⚡ Desarrollo rápido con Vite

## 🛠️ Tecnologías Utilizadas

### Backend
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para base de datos
- **Pydantic** - Validación de datos
- **JWT** - Autenticación con tokens
- **SQLite** - Base de datos (configurable para PostgreSQL)
- **Uvicorn** - Servidor ASGI

### Frontend
- **React 19** - Biblioteca de interfaz de usuario
- **TypeScript** - Tipado estático
- **Vite** - Herramienta de construcción rápida
- **React Router** - Enrutamiento de la aplicación
- **CSS Modules** - Estilos modulares

## 📁 Estructura del Proyecto

```
diplomado/
├── feel-guard-back/          # Backend FastAPI
│   ├── main.py              # Punto de entrada
│   ├── run.py               # Script de ejecución
│   ├── init_db.py           # Inicialización de BD
│   ├── requirements.txt     # Dependencias Python
│   ├── env.example          # Variables de entorno
│   ├── models/              # Modelos de BD
│   ├── schemas/             # Esquemas Pydantic
│   ├── routes/              # Endpoints de la API
│   └── utils/               # Utilidades
├── feel-guard-front/        # Frontend React
│   ├── src/
│   │   ├── components/      # Componentes React
│   │   ├── pages/          # Páginas de la app
│   │   ├── services/       # Servicios de API
│   │   ├── config/         # Configuraciones
│   │   └── types/          # Tipos TypeScript
│   ├── package.json        # Dependencias Node.js
│   └── env.example         # Variables de entorno
├── start-projects.bat      # Script Windows
├── start-projects.sh       # Script Linux/Mac
└── README.md              # Este archivo
```

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- Node.js 18+
- npm o yarn

### 1. Configurar el Backend

```bash
# Navegar al directorio del backend
cd feel-guard-back

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp env.example .env
# Editar .env con tus configuraciones

# Inicializar la base de datos
python init_db.py
```

### 2. Configurar el Frontend

```bash
# Navegar al directorio del frontend
cd feel-guard-front

# Instalar dependencias
npm install

# Configurar variables de entorno
cp env.example .env
# Editar .env con tus configuraciones
```

### 3. Ejecutar los Proyectos

#### Opción 1: Scripts automáticos
```bash
# Windows
start-projects.bat

# Linux/Mac
chmod +x start-projects.sh
./start-projects.sh
```

#### Opción 2: Manual
```bash
# Terminal 1 - Backend
cd feel-guard-back
python run.py

# Terminal 2 - Frontend
cd feel-guard-front
npm run dev
```

## 🌐 Acceso a la Aplicación

Una vez ejecutados ambos proyectos:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **ReDoc API**: http://localhost:8000/redoc

## 👤 Usuarios por Defecto

Después de ejecutar `init_db.py`, se crean automáticamente:

### Administrador
- **Email**: `admin@feelguard.com`
- **Contraseña**: `admin123`

### Usuario de Prueba
- **Email**: `test@feelguard.com`
- **Contraseña**: `test123`

## 📚 Endpoints de la API

### Autenticación
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/me` - Información del usuario

### Temperatura
- `POST /api/temperature/` - Crear lectura
- `GET /api/temperature/` - Obtener lecturas
- `GET /api/temperature/stats` - Estadísticas
- `GET /api/temperature/alerts` - Alertas
- `PUT /api/temperature/alerts/{id}/resolve` - Resolver alerta
- `GET /api/temperature/recent` - Lecturas recientes

### Usuarios
- `GET /api/users/` - Listar usuarios (admin)
- `GET /api/users/{id}` - Obtener usuario
- `PUT /api/users/{id}` - Actualizar usuario
- `DELETE /api/users/{id}` - Eliminar usuario (admin)

## 🔧 Desarrollo

### Backend
```bash
cd feel-guard-back
# Ejecutar con recarga automática
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd feel-guard-front
# Ejecutar en modo desarrollo
npm run dev
```

## 🧪 Testing

### Backend
```bash
cd feel-guard-back
# Ejecutar tests (cuando se implementen)
python -m pytest
```

### Frontend
```bash
cd feel-guard-front
# Ejecutar tests (cuando se implementen)
npm test
```

## 📦 Despliegue

### Backend (Producción)
1. Cambiar `SECRET_KEY` por una clave segura
2. Usar PostgreSQL en lugar de SQLite
3. Configurar HTTPS
4. Implementar rate limiting
5. Configurar logging apropiado

### Frontend (Producción)
```bash
cd feel-guard-front
npm run build
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto es parte del diplomado Feel Guard.

## 📞 Soporte

Para soporte técnico o preguntas sobre el proyecto, contacta al equipo de desarrollo.

---

**Feel Guard** - Monitoreando tu bienestar, una temperatura a la vez 🌡️ 
