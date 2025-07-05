import { API_CONFIG } from '../config/api.config';

// Interfaces para autenticación
export interface LoginData {
  username: string; // FastAPI usa 'username' para el email
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  full_name: string;
  password: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

// Clase para manejar errores de autenticación
class AuthError extends Error {
  public status: number;
  public response?: unknown;

  constructor(message: string, status: number, response?: unknown) {
    super(message);
    this.name = 'AuthError';
    this.status = status;
    this.response = response;
  }
}

// Función para hacer peticiones HTTP con manejo de errores
async function makeAuthRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_CONFIG.BASE_URL}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    headers: {
      ...API_CONFIG.DEFAULT_HEADERS,
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new AuthError(
        errorData.detail || `HTTP error! status: ${response.status}`,
        response.status,
        errorData
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof AuthError) {
      throw error;
    }
    throw new AuthError('Network error', 0, error);
  }
}

// Función para obtener el token del localStorage
export const getAuthToken = (): string | null => {
  return localStorage.getItem('auth_token');
};

// Función para guardar el token en localStorage
export const setAuthToken = (token: string): void => {
  localStorage.setItem('auth_token', token);
};

// Función para eliminar el token del localStorage
export const removeAuthToken = (): void => {
  localStorage.removeItem('auth_token');
};

// Función para verificar si el usuario está autenticado
export const isAuthenticated = (): boolean => {
  return getAuthToken() !== null;
};

// Servicio de autenticación
export const authService = {
  // Registrar nuevo usuario
  async register(userData: RegisterData): Promise<User> {
    return makeAuthRequest<User>(API_CONFIG.ENDPOINTS.AUTH.REGISTER, {
      method: 'POST',
      body: JSON.stringify(userData)
    });
  },

  // Iniciar sesión
  async login(loginData: LoginData): Promise<AuthResponse> {
    // FastAPI requiere los datos en formato FormData para OAuth2
    const formData = new FormData();
    formData.append('username', loginData.username);
    formData.append('password', loginData.password);

    const response = await makeAuthRequest<AuthResponse>(
      API_CONFIG.ENDPOINTS.AUTH.LOGIN,
      {
        method: 'POST',
        headers: {
          // No incluir Content-Type para FormData
        },
        body: formData
      }
    );

    // Guardar token en localStorage
    setAuthToken(response.access_token);
    return response;
  },

  // Cerrar sesión
  logout(): void {
    removeAuthToken();
  },

  // Obtener información del usuario actual
  async getCurrentUser(): Promise<User> {
    const token = getAuthToken();
    if (!token) {
      throw new AuthError('No authentication token', 401);
    }

    return makeAuthRequest<User>(API_CONFIG.ENDPOINTS.AUTH.ME, {
      method: 'GET',
      headers: {
        ...API_CONFIG.DEFAULT_HEADERS,
        'Authorization': `Bearer ${token}`
      }
    });
  },

  // Verificar si el token es válido
  async validateToken(): Promise<boolean> {
    try {
      await this.getCurrentUser();
      return true;
    } catch (error) {
      if (error instanceof AuthError && error.status === 401) {
        removeAuthToken();
        return false;
      }
      throw error;
    }
  }
};

// Exportar la clase de error
export { AuthError }; 