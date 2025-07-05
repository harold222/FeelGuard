# Servicio API - Feel Guard

Este directorio contiene los servicios para manejar las peticiones HTTP a la API.

## Estructura

```
services/
├── api.ts          # Servicio principal para peticiones HTTP
└── README.md       # Esta documentación

config/
└── api.config.ts   # Configuración del API
```

## Configuración

### Variables de Entorno

Puedes configurar la URL base del API usando variables de entorno:

```bash
# .env
VITE_API_BASE_URL=https://tu-api-backend.com/v1
```

### Configuración por Defecto

Si no se especifica una variable de entorno, se usa la URL por defecto:
- **URL Base**: `https://api.feelguard.com/v1`
- **Timeout**: 10 segundos
- **Headers**: `Content-Type: application/json`, `Accept: application/json`

## Uso del Servicio

### Importar el Servicio

```typescript
import { formService } from '../services/api';
```

### Enviar Formulario

```typescript
const formData = {
  email: 'usuario@ejemplo.com',
  nombre: 'Juan Pérez',
  edad: '25',
  sexo: 'masculino',
  observaciones: 'Observaciones del usuario...'
};

try {
  const response = await formService.submitForm(formData);
  if (response.success) {
    console.log('Formulario enviado:', response.message);
  } else {
    console.error('Error:', response.error);
  }
} catch (error) {
  console.error('Error de conexión:', error);
}
```

### Otros Métodos Disponibles

```typescript
// Obtener todos los usuarios
const users = await formService.getUsers();

// Validar email
const emailValidation = await formService.validateEmail('usuario@ejemplo.com');
```

## Manejo de Errores

El servicio incluye manejo de errores robusto:

```typescript
import { ApiError } from '../services/api';

try {
  const response = await formService.submitForm(formData);
} catch (error) {
  if (error instanceof ApiError) {
    console.error(`Error ${error.status}:`, error.message);
  } else {
    console.error('Error de conexión:', error);
  }
}
```

## Desarrollo

### Simulación de Respuestas

En desarrollo, si no hay conexión al servidor, el servicio simula respuestas exitosas para facilitar las pruebas.

### Delay Simulado

```typescript
import { simulateApiDelay } from '../services/api';

// Simular delay de 2 segundos
await simulateApiDelay(2000);
```

## Endpoints Configurados

- `POST /users/register` - Registrar nuevo usuario
- `GET /users` - Obtener todos los usuarios
- `POST /users/validate-email` - Validar email
- `POST /auth/login` - Iniciar sesión
- `POST /auth/logout` - Cerrar sesión

## Personalización

Para agregar nuevos endpoints, edita `src/config/api.config.ts`:

```typescript
export const API_CONFIG = {
  // ... configuración existente
  ENDPOINTS: {
    USERS: {
      // ... endpoints existentes
      UPDATE: '/users/update',
      DELETE: '/users/delete',
    },
    // Nuevos grupos de endpoints
    REPORTS: {
      GENERATE: '/reports/generate',
      DOWNLOAD: '/reports/download',
    }
  }
};
``` 