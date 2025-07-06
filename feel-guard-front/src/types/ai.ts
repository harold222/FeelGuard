// Tipos para las evaluaciones de salud mental
export interface Assessment {
  session_id: string;
  type: 'stress' | 'anxiety' | 'depression' | 'crisis';
  risk_level: 'low' | 'moderate' | 'high' | 'critical';
  timestamp: string;
  text_sample: string;
  stress_assessment?: StressAssessment;
  anxiety_assessment?: AnxietyAssessment;
  depression_assessment?: DepressionAssessment;
  crisis_indicators?: CrisisIndicators;
}

export interface StressAssessment {
  level: 'Bajo' | 'Moderado' | 'Alto';
  score: number;
  categories: {
    físicos: number;
    emocionales: number;
    cognitivos: number;
    conductuales: number;
  };
  timestamp: string;
}

export interface AnxietyAssessment {
  level: 'Bajo' | 'Moderado' | 'Alto';
  score: number;
  categories: {
    preocupación: number;
    físicos: number;
    cognitivos: number;
    conductuales: number;
  };
  timestamp: string;
}

export interface DepressionAssessment {
  level: 'Bajo' | 'Moderado' | 'Alto';
  score: number;
  categories: {
    estado_animo: number;
    interés: number;
    sueño: number;
    apetito: number;
    pensamientos: number;
  };
  timestamp: string;
}

export interface CrisisIndicators {
  suicidal_ideation: boolean;
  self_harm: boolean;
  panic_attack: boolean;
}

// Tipos para las respuestas de la API
export interface AIResponse {
  output: string;
  session_id: string;
  assessment?: Assessment;
  risk_level?: string;
}

export interface ChatHistoryItem {
  id: number;
  message: string;
  response: string;
  created_at: string;
}

export interface UserAssessmentSummary {
  user_id: number;
  total_conversations: number;
  total_assessments: number;
  period_days: number;
  risk_levels_summary: {
    low: number;
    moderate: number;
    high: number;
    critical: number;
  };
  assessment_types_summary: {
    stress: number;
    anxiety: number;
    depression: number;
    crisis: number;
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
  audio_path?: string;
  message_type?: 'text' | 'audio';
}

// Tipos para el dashboard
export interface DashboardData {
  summary: UserAssessmentSummary;
  recentMessages: ChatMessage[];
  riskTrend: 'increasing' | 'decreasing' | 'stable';
} 