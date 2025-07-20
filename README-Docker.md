# Feel Guard - Docker Setup

Este documento explica cómo ejecutar Feel Guard usando Docker.

## 📋 Prerrequisitos

1. **Docker Desktop** instalado en tu sistema
   - Windows: [Docker Desktop para Windows](https://www.docker.com/products/docker-desktop)
   - macOS: [Docker Desktop para Mac](https://www.docker.com/products/docker-desktop)
   - Linux: [Docker Engine](https://docs.docker.com/engine/install/)

2. **Docker Compose** (incluido con Docker Desktop)

## 🚀 Inicio Rápido

### Opción 1: Scripts Automáticos (Recomendado)

1. **Iniciar servicios:**
   ```bash
   docker-start.bat
   ```

2. **Detener servicios:**
   ```bash
   docker-stop.bat
   ```

3. **Reconstruir desde cero (si hay errores):**
   ```bash
   docker-rebuild.bat
   ```

### Opción 2: Comandos Manuales

1. **Construir e iniciar servicios:**
   ```bash
   docker-compose up -d --build
   ```

2. **Ver logs en tiempo real:**
   ```bash
   docker-compose logs -f
   ```

3. **Detener servicios:**
   ```bash
   docker-compose down
   ```

## 🌐 Acceso a los Servicios

Una vez iniciados, puedes acceder a:

- **Frontend (React):** http://localhost
- **Backend (FastAPI):** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Base de datos (PostgreSQL):** localhost:5432

## 📁 Estructura de Archivos Docker

```
diplomado/
├── docker-compose.yml          # Orquestación de servicios
├── docker-start.bat           # Script para iniciar
├── docker-stop.bat            # Script para detener
├── feel-guard-back/
│   ├── Dockerfile             # Imagen del backend
│   └── .dockerignore          # Archivos a ignorar
└── feel-guard-front/
    ├── Dockerfile             # Imagen del frontend
    ├── nginx.conf             # Configuración de nginx
    └── .dockerignore          # Archivos a ignorar
```

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` en el directorio raíz con las siguientes variables:

```env
# Base de datos
DATABASE_URL=postgresql://user:password@postgres:5432/feelguard

# Seguridad
SECRET_KEY=tu-clave-secreta-aqui

# OpenAI
OPENAI_API_KEY=tu-api-key-de-openai

# Servidor
HOST=0.0.0.0
PORT=8000

# Frontend - URL del API Backend
VITE_API_BASE_URL=http://localhost:8000
```

### Volúmenes

Los siguientes directorios están mapeados como volúmenes:

- `./feel-guard-back/uploads` → `/app/uploads` (archivos subidos)
- `postgres_data` → `/var/lib/postgresql/data` (base de datos)

### Variables de Entorno del Frontend

El frontend React usa las siguientes variables de entorno:

- `VITE_API_BASE_URL`: URL del backend (por defecto: `http://localhost:8000`)

Estas variables se configuran en el `docker-compose.yml` y se pasan durante el build de la imagen.

## 🔧 Comandos Útiles

### Gestión de Contenedores

```bash
# Ver estado de los servicios
docker-compose ps

# Ver logs de un servicio específico
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Reiniciar un servicio
docker-compose restart backend

# Ejecutar comandos dentro de un contenedor
docker-compose exec backend python main.py
docker-compose exec postgres psql -U user -d feelguard
```

### Limpieza

```bash
# Detener y eliminar contenedores
docker-compose down

# Detener y eliminar contenedores + volúmenes
docker-compose down -v

# Eliminar imágenes no utilizadas
docker image prune

# Limpieza completa del sistema Docker
docker system prune -a
```

## 🐛 Solución de Problemas

### Error: Puerto ya en uso

Si el puerto 80 o 8000 están ocupados, modifica el `docker-compose.yml`:

```yaml
ports:
  - "8080:80"    # Cambiar 80 por 8080
  - "8001:8000"  # Cambiar 8000 por 8001
```

**Importante:** Si cambias el puerto del backend, también debes actualizar la variable `VITE_API_BASE_URL`:

```yaml
environment:
  - VITE_API_BASE_URL=http://localhost:8001  # Cambiar 8000 por 8001
```

### Error: Permisos de Docker

En Windows/macOS, asegúrate de que Docker Desktop esté ejecutándose.

En Linux, agrega tu usuario al grupo docker:

```bash
sudo usermod -aG docker $USER
```

### Error: Memoria insuficiente

Si Docker se queda sin memoria, aumenta la memoria asignada en Docker Desktop:
1. Abre Docker Desktop
2. Ve a Settings → Resources
3. Aumenta la memoria asignada (recomendado: 4GB+)

### Error: Base de datos no conecta

```bash
# Verificar que PostgreSQL esté ejecutándose
docker-compose logs postgres

# Reiniciar solo la base de datos
docker-compose restart postgres
```

### Error: "tsc: not found" en el build del frontend

Este error ocurre cuando TypeScript no está disponible durante el build. Soluciones:

1. **Reconstruir desde cero:**
   ```bash
   docker-rebuild.bat
   ```

2. **Limpiar manualmente:**
   ```bash
   docker-compose down
   docker image prune -f
   docker-compose build --no-cache
   docker-compose up -d
   ```

3. **Verificar que el Dockerfile incluya todas las dependencias:**
   - El Dockerfile debe usar `npm ci` (no `npm ci --only=production`)
   - TypeScript debe estar en `devDependencies` del `package.json`

### Error: Variables no utilizadas en TypeScript

Si ves errores como `'variable' is declared but its value is never read`:

1. **Solución rápida:** Usar prefijo `_` para variables no utilizadas:
   ```typescript
   const renderAssessment = (assessment?: Assessment, _classification?: DepressionClassification) => {
   ```

2. **Solución permanente:** Modificar `tsconfig.app.json`:
   ```json
   {
     "compilerOptions": {
       "noUnusedLocals": false,
       "noUnusedParameters": false
     }
   }
   ```

3. **Reconstruir después de cambios:**
   ```bash
   docker-rebuild.bat
   ```

## 🔄 Desarrollo

### Modo Desarrollo

Para desarrollo, puedes usar los archivos originales sin Docker:

```bash
# Backend
cd feel-guard-back
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Frontend
cd feel-guard-front
npm install
npm run dev
```

### Reconstruir Imágenes

Si modificas el código, reconstruye las imágenes:

```bash
docker-compose build --no-cache
docker-compose up -d
```

## 📊 Monitoreo

### Recursos del Sistema

```bash
# Ver uso de recursos
docker stats

# Ver espacio en disco
docker system df
```

### Logs Estructurados

```bash
# Logs del backend
docker-compose logs -f backend

# Logs del frontend
docker-compose logs -f frontend

# Logs de la base de datos
docker-compose logs -f postgres
```

## 🔒 Seguridad

### Variables de Entorno Sensibles

Nunca commits archivos `.env` con claves reales. Usa `.env.example` como plantilla.

### Firewall

Los puertos expuestos son:
- `80`: Frontend (HTTP)
- `8000`: Backend (HTTP)
- `5432`: PostgreSQL (solo desarrollo)

En producción, considera usar HTTPS y limitar el acceso a la base de datos.

## 📝 Notas Adicionales

- Los archivos subidos se guardan en `./feel-guard-back/uploads`
- La base de datos PostgreSQL se inicializa automáticamente
- El frontend usa nginx para servir archivos estáticos
- Los servicios se reinician automáticamente si fallan

## 🆘 Soporte

Si encuentras problemas:

1. Verifica que Docker esté instalado y ejecutándose
2. Revisa los logs con `docker-compose logs`
3. Asegúrate de que los puertos no estén ocupados
4. Verifica que las variables de entorno estén configuradas correctamente 