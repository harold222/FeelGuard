import type { FormData } from '../types/form';
import { API_CONFIG } from '../config/api.config';

let loaderCallback: ((active: boolean) => void) | null = null;
export const setLoaderCallback = (cb: (active: boolean) => void) => { loaderCallback = cb; };

function getToken() {
  return localStorage.getItem('auth_token');
}

// Interfaz para la respuesta del API
interface ApiResponse {
  success: boolean;
  message: string;
  data?: unknown;
  error?: string;
  token?: string;
}

// Clase para manejar errores del API
class ApiError extends Error {
  public status: number;
  public response?: unknown;

  constructor(
    message: string,
    status: number,
    response?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.response = response;
  }
}

// Interceptor global para fetch
async function interceptedFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  if (loaderCallback) loaderCallback(true);
  const url = `${API_CONFIG.BASE_URL}${endpoint}`;
  const token = getToken();
  const defaultOptions: RequestInit = {
    headers: {
      ...API_CONFIG.DEFAULT_HEADERS,
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    
    if (!response.ok) {
      throw new ApiError(
        `HTTP error! status: ${response.status}`,
        response.status,
        await response.json().catch(() => null)
      );
    }

    return await response.json();
  } finally {
    if (loaderCallback) loaderCallback(false);
  }
}

// Servicio para el formulario
export const formService = {
  // Enviar datos del formulario
  async submitForm(formData: FormData): Promise<ApiResponse> {
    const endpoint = '/registro';
    return interceptedFetch<ApiResponse>(endpoint, {
      method: 'POST',
      body: JSON.stringify({
        email: formData.email,
        nombre: formData.nombre,
        edad: parseInt(formData.edad),
        sexo: formData.sexo,
        fechaRegistro: new Date().toISOString()
      })
    });
  },

  // Obtener usuarios (ejemplo adicional)
  async getUsers(): Promise<ApiResponse> {
    const endpoint = API_CONFIG.ENDPOINTS.USERS.GET_ALL;
    return interceptedFetch<ApiResponse>(endpoint, {
      method: 'GET'
    });
  },

  // Consultar registro por email
  async getRegistroByEmail(email: string): Promise<{ id: number; email: string; nombre: string; edad: number; sexo: string; fecha_registro: string }> {
    const endpoint = `/registro/email/${encodeURIComponent(email)}`;
    return interceptedFetch<{ id: number; email: string; nombre: string; edad: number; sexo: string; fecha_registro: string }>(endpoint, { method: 'GET' });
  }
};

// Función para simular delay (útil para desarrollo)
export const simulateApiDelay = (ms: number = 1000): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

// Exportar la clase de error para uso externo
export { ApiError }; 