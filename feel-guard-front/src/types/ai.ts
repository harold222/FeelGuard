// Tipos para las evaluaciones de salud mental
export interface Assessment {
  session_id: string;
  type: 'depression' | 'neutral';
  risk_level: 'low' | 'moderate' | 'high' | 'critical';
  timestamp: string;
  text_sample: string;
  depression_assessment?: DepressionAssessment;
}

export interface DepressionAssessment {
  level: 'Bajo' | 'Moderado' | 'Alto';
  score: number;
  is_depression: boolean;
  probability_neutral: number;
  probability_depression: number;
  timestamp: string;
}

// Nueva interfaz para la clasificación del modelo
export interface DepressionClassification {
  is_depression: boolean;
  confidence: number;
  probability: [number, number]; // [neutral, depression]
  processed_text?: string;
  error?: string;
}

// Tipos para las respuestas de la API
export interface AIResponse {
  output: string;
  session_id: string;
  assessment?: Assessment;
  risk_level?: string;
  depression_classification?: DepressionClassification;
}

export interface ChatHistoryItem {
  id: number;
  message: string;
  response: string;
  created_at: string;
  audio_path?: string;
  message_type?: 'text' | 'audio';
}

export interface UserAssessmentSummary {
  user_id: number;
  total_conversations: number;
  total_assessments: number;
  period_days: number;
  risk_levels_summary: {
    bajo: number;
    moderado: number;
    alto: number;
    critico: number;
  };
  assessment_types_summary: {
    depression: number;
    neutral: number;
  };
  average_risk_score: number;
  most_common_concern: string;
  recommendations: string[];
}

// Tipos para el estado del chat
export interface ChatMessage {
  id: number;
  message: string;
  response: string;
  created_at: string;
  assessment?: Assessment;
  risk_level?: string;
  depression_classification?: DepressionClassification;
  audio_path?: string;
  image_path?: string; // NUEVO para imágenes
  message_type?: 'text' | 'audio' | 'image'; // NUEVO para imágenes
}

// Tipos para el dashboard
export interface DashboardData {
  summary: UserAssessmentSummary;
  recentMessages: ChatMessage[];
  riskTrend: 'increasing' | 'decreasing' | 'stable';
} 