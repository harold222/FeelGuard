export interface AIResponse {
  output: string;
  session_id: string;
}

export interface ChatHistoryItem {
  id: number;
  message: string;
  response: string;
  created_at: string;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const aiService = {
  async processText(text: string, sessionId?: string): Promise<AIResponse> {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`${API_BASE}/api/ai/process-text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ text, session_id: sessionId }),
    });
    if (!response.ok) {
      throw new Error('Error al procesar el texto');
    }
    return response.json();
  },

  async processVoice(audioFile: File, sessionId?: string): Promise<AIResponse> {
    const formData = new FormData();
    formData.append('audio', audioFile);
    if (sessionId) formData.append('session_id', sessionId);
    const response = await fetch(`${API_BASE}/api/ai/process-voice`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      throw new Error('Error al procesar el audio');
    }
    return response.json();
  },

  async getChatHistory(): Promise<ChatHistoryItem[]> {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`${API_BASE}/api/ai/chat-history`, {
      headers: {
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      },
    });
    if (!response.ok) {
      throw new Error('No se pudo obtener el historial de chat');
    }
    return response.json();
  },
}; 