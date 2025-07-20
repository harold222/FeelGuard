// Configuración del API
export const API_CONFIG = {
  // URL base del API - Backend FastAPI
  BASE_URL: 'https://feel-guard-backend-v1-0-0.onrender.com',
  
  // Timeout para las peticiones (en milisegundos)
  TIMEOUT: 10000,
  
  // Headers por defecto
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  
  // Endpoints del backend FastAPI
  ENDPOINTS: {
    AUTH: {
      REGISTER: '/api/auth/register',
      LOGIN: '/api/auth/login',
      ME: '/api/auth/me',
    },
    USERS: {
      GET_ALL: '/api/users',
      GET_BY_ID: '/api/users/{id}',
      UPDATE: '/api/users/{id}',
      DELETE: '/api/users/{id}',
    },
    REGISTRO: {
      CREATE: '/registro',
      GET_BY_EMAIL: '/registro/email/{email}',
    }
  }
} as const;

// Tipos para la configuración
export type ApiEndpoint = typeof API_CONFIG.ENDPOINTS; 