# Feel Guard Frontend

Frontend de la aplicación Feel Guard IA, un asistente de salud mental inteligente construido con React, TypeScript y Vite.

## 🚀 Características

### Chat Inteligente
- **Conversación en tiempo real** con IA especializada en salud mental
- **Procesamiento de texto** con análisis automático de sentimientos
- **Notas de voz** con transcripción automática usando Whisper API
- **Evaluaciones automáticas** de estrés, ansiedad, depresión y bienestar
- **Detección de crisis** con identificación de palabras clave de riesgo

### Dashboard de Salud Mental
- **Resumen de evaluaciones** con estadísticas detalladas
- **Gráficos de niveles de riesgo** (bajo, moderado, alto, crítico)
- **Análisis de tipos de evaluación** (estrés, ansiedad, depresión, bienestar, crisis)
- **Puntuación promedio de riesgo** con visualización circular
- **Recomendaciones personalizadas** basadas en el historial
- **Filtros por período** (7, 30, 90 días)

### Funcionalidades de Usuario
- **Autenticación JWT** con tokens seguros
- **Historial de conversaciones** persistente
- **Limpieza de conversaciones** con confirmación
- **Interfaz responsiva** para móviles y desktop
- **Diseño moderno** con gradientes y efectos visuales

## 🛠️ Tecnologías

- **React 18** - Biblioteca de interfaz de usuario
- **TypeScript** - Tipado estático para mayor seguridad
- **Vite** - Herramienta de construcción rápida
- **React Router** - Navegación entre páginas
- **CSS3** - Estilos modernos con gradientes y animaciones

## 📦 Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd feel-guard-front
```

2. **Instalar dependencias**
```bash
npm install
```

3. **Configurar variables de entorno**
```bash
cp .env.example .env
```

Editar `.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

4. **Ejecutar en desarrollo**
```bash
npm run dev
```

5. **Construir para producción**
```bash
npm run build
```

## 🏗️ Estructura del Proyecto

```
src/
├── components/          # Componentes reutilizables
│   ├── Formulario.tsx   # Formulario de registro/login
│   ├── Navbar.tsx       # Barra de navegación
│   └── ProtectedRoute.tsx # Ruta protegida
├── pages/              # Páginas principales
│   ├── Home.tsx        # Página de inicio
│   ├── AiChat.tsx      # Chat con IA
│   └── Dashboard.tsx   # Dashboard de salud mental
├── services/           # Servicios de API
│   ├── ai.service.ts   # Servicios de IA
│   ├── auth.service.ts # Servicios de autenticación
│   └── api.ts          # Configuración de API
├── types/              # Definiciones de tipos
│   ├── ai.ts           # Tipos para IA y evaluaciones
│   └── form.ts         # Tipos para formularios
└── assets/             # Recursos estáticos
```

## 🔌 API Endpoints

### Autenticación
- `POST /api/auth/register` - Registro de usuario
- `POST /api/auth/login` - Inicio de sesión

### IA y Chat
- `POST /api/ai/process-text` - Procesar texto
- `POST /api/ai/process-voice` - Procesar audio
- `GET /api/ai/chat-history` - Obtener historial
- `DELETE /api/ai/clear-conversation` - Limpiar conversación
- `GET /api/ai/user-assessment-summary` - Resumen de evaluaciones

## 🎨 Características de UI/UX

### Diseño Moderno
- **Gradientes** con colores suaves y profesionales
- **Efectos de cristal** (glassmorphism) para tarjetas
- **Animaciones suaves** en hover y transiciones
- **Iconos emoji** para mejor experiencia visual

### Responsive Design
- **Mobile-first** approach
- **Grid layouts** adaptativos
- **Breakpoints** optimizados para diferentes dispositivos
- **Touch-friendly** para dispositivos móviles

### Estados de Interfaz
- **Loading states** con indicadores visuales
- **Error handling** con mensajes claros
- **Success feedback** para acciones completadas
- **Empty states** para datos vacíos

## 🔒 Seguridad

- **JWT tokens** para autenticación
- **Headers de autorización** en todas las peticiones
- **Validación de formularios** en el frontend
- **Protección de rutas** para usuarios autenticados

## 📱 Funcionalidades Móviles

- **Grabación de audio** nativa del navegador
- **Interfaz táctil** optimizada
- **Navegación por gestos** intuitiva
- **Responsive design** para todas las pantallas

## 🚀 Despliegue

### Vercel (Recomendado)
```bash
npm run build
vercel --prod
```

### Netlify
```bash
npm run build
netlify deploy --prod --dir=dist
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

Para soporte técnico o preguntas:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo
- Revisar la documentación del backend

## 🔄 Actualizaciones

### v2.0.0 - Evaluaciones de Salud Mental
- ✅ Chat con IA especializada
- ✅ Evaluaciones automáticas de estrés, ansiedad, depresión
- ✅ Dashboard con estadísticas detalladas
- ✅ Detección de crisis
- ✅ Procesamiento de voz con Whisper
- ✅ Interfaz moderna y responsiva

### Próximas características
- 📊 Gráficos avanzados con Chart.js
- 🔔 Notificaciones push
- 📱 Aplicación móvil nativa
- 🤖 Más tipos de evaluaciones
- 📈 Reportes PDF
