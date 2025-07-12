"""
Sistema de evaluación estructurada para salud mental en Feel Guard
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
from .depression_classifier import depression_classifier

class AssessmentType(Enum):
    DEPRESSION = "depression"
    NEUTRAL = "neutral"

class RiskLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

class MentalHealthAssessment:
    def __init__(self):
        self.assessment_history: Dict[str, List[Dict]] = {}
        # Palabras clave para crisis (mantenemos estas para detección de emergencia)
        self.crisis_keywords = [
            "suicidio", "suicidar", "matar", "morir", "muerte", "no quiero vivir",
            "mejor estar muerto", "acabar con todo", "no aguanto más",
            "autolesión", "cortarme", "herirme", "dolor físico", "crisis",
            "ataque de pánico", "no puedo respirar", "me voy a morir",
            "pensamientos intrusivos", "voces", "alucinaciones", 
            "no valgo para nada", "nadie me quiere", "sería mejor no existir",
            "estoy harto(a) de vivir", "no siento ganas de seguir", "todo da igual",
            "ya no tiene sentido", "ya no puedo más",
            "me estoy volviendo loco(a)", "me estoy desquiciando",
            "odia cuando me siento vacío(a)", "nada importa",
            "voy a buscar cómo matarme", "estoy planeándolo",
            "he pensado en cómo hacerlo", "buscando métodos",
            "si pudiera desaparecer", "ya tengo todo preparado"
        ]
    
    def detect_crisis(self, text: str) -> bool:
        """Detecta si el mensaje contiene señales de crisis"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.crisis_keywords)
    
    def assess_risk_level(self, text: str) -> RiskLevel:
        """Evalúa el nivel de riesgo basado en el contenido del texto"""
        # Primero verificar crisis
        if self.detect_crisis(text):
            return RiskLevel.CRITICAL
        
        # Usar el modelo de clasificación para depresión
        classification_result = depression_classifier.classify_text(text)
        
        if classification_result.get('is_depression', False):
            confidence = classification_result.get('confidence', 0.0)
            
            # Determinar nivel de riesgo basado en la confianza del modelo
            if confidence >= 0.8:
                return RiskLevel.HIGH
            elif confidence >= 0.6:
                return RiskLevel.MODERATE
            else:
                return RiskLevel.LOW
        else:
            # Si no es depresión, es neutro
            return ""
    
    def determine_assessment_type(self, text: str) -> AssessmentType:
        """Determina el tipo de evaluación basado en el modelo de clasificación"""
        # Usar el modelo de clasificación
        classification_result = depression_classifier.classify_text(text)
        
        if classification_result.get('is_depression', False):
            return AssessmentType.DEPRESSION
        else:
            return AssessmentType.NEUTRAL
    
    def assess_depression_level(self, text: str) -> Dict:
        """Evalúa específicamente el nivel de depresión usando el modelo"""
        classification_result = depression_classifier.classify_text(text)
        
        is_depression = classification_result.get('is_depression', False)
        confidence = classification_result.get('confidence', 0.0)
        probability = classification_result.get('probability', [1.0, 0.0])
        
        # Determinar nivel basado en la confianza
        if is_depression:
            if confidence >= 0.8:
                level = "Alto"
            elif confidence >= 0.6:
                level = "Moderado"
            else:
                level = "Bajo"
        else:
            level = "Sin indicadores"
        
        return {
            "level": level,
            "score": confidence,
            "is_depression": is_depression,
            "probability_neutral": probability[0] if len(probability) > 0 else 0.0,
            "probability_depression": probability[1] if len(probability) > 1 else 0.0,
            "timestamp": datetime.now().isoformat()
        }
    
    def create_assessment(self, session_id: str, text: str, assessment_type: AssessmentType = None) -> Dict:
        """Crea una evaluación completa usando el modelo de clasificación"""
        # Si no se proporciona assessment_type, determinarlo automáticamente
        if assessment_type is None:
            assessment_type = self.determine_assessment_type(text)
        
        risk_level = self.assess_risk_level(text)
        risk_level_value = risk_level.value if hasattr(risk_level, 'value') else (risk_level if risk_level else "")
        
        assessment = {
            "session_id": session_id,
            "type": assessment_type.value if assessment_type else "",
            "risk_level": risk_level_value,
            "timestamp": datetime.now().isoformat(),
            "text_sample": text[:200] + "..." if len(text) > 200 else text
        }
        
        # Agregar evaluación específica de depresión
        if assessment_type == AssessmentType.DEPRESSION:
            assessment["depression_assessment"] = self.assess_depression_level(text)
        elif assessment_type == AssessmentType.NEUTRAL:
            assessment["neutral_assessment"] = {
                "is_neutral": True,
                "confidence": depression_classifier.classify_text(text).get('confidence', 0.0),
                "timestamp": datetime.now().isoformat()
            }
        
        # Si se detecta crisis, agregar indicadores de crisis
        if self.detect_crisis(text):
            assessment["crisis_indicators"] = {
                "suicidal_ideation": any(word in text.lower() for word in ["suicidio", "morir", "acabar"]),
                "self_harm": any(word in text.lower() for word in ["cortarme", "herirme", "autolesión"]),
                "panic_attack": any(word in text.lower() for word in ["pánico", "no puedo respirar", "me voy a morir"])
            }
        
        # Guardar en historial
        if session_id not in self.assessment_history:
            self.assessment_history[session_id] = []
        
        self.assessment_history[session_id].append(assessment)
        
        return assessment
    
    def get_session_progress(self, session_id: str, days: int = 7) -> Dict:
        """Obtiene el progreso de una sesión en los últimos días"""
        if session_id not in self.assessment_history:
            return {"message": "No hay evaluaciones para esta sesión"}
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_assessments = [
            assessment for assessment in self.assessment_history[session_id]
            if datetime.fromisoformat(assessment["timestamp"]) > cutoff_date
        ]
        
        if not recent_assessments:
            return {"message": f"No hay evaluaciones en los últimos {days} días"}
        
        # Analizar tendencias
        risk_levels = [assessment["risk_level"] for assessment in recent_assessments]
        risk_trend = self._analyze_trend(risk_levels)
        
        # Obtener evaluaciones más recientes por tipo
        latest_by_type = {}
        for assessment in recent_assessments:
            assessment_type = assessment["type"]
            if assessment_type not in latest_by_type or \
               assessment["timestamp"] > latest_by_type[assessment_type]["timestamp"]:
                latest_by_type[assessment_type] = assessment
        
        return {
            "session_id": session_id,
            "period_days": days,
            "total_assessments": len(recent_assessments),
            "risk_trend": risk_trend,
            "latest_assessments": latest_by_type,
            "recommendations": self._generate_recommendations(latest_by_type, risk_trend)
        }
    
    def _analyze_trend(self, risk_levels: List[str]) -> str:
        """Analiza la tendencia de los niveles de riesgo"""
        if len(risk_levels) < 2:
            return "insuficiente_data"
        
        # Convertir a valores numéricos para análisis
        level_values = {
            "low": 1,
            "moderate": 2,
            "high": 3,
            "critical": 4
        }
        
        values = [level_values[level] for level in risk_levels if level in level_values]
        
        if len(values) < 2:
            return "insuficiente_data"
        
        # Calcular tendencia
        if values[-1] > values[0]:
            return "increasing"
        elif values[-1] < values[0]:
            return "decreasing"
        else:
            return "stable"
    
    def _generate_recommendations(self, latest_assessments: Dict, risk_trend: str) -> List[str]:
        """Genera recomendaciones basadas en las evaluaciones"""
        recommendations = []
        
        # Recomendaciones basadas en tendencia
        if risk_trend == "increasing":
            recommendations.append("Considera buscar ayuda profesional para evaluar tu situación")
        elif risk_trend == "decreasing":
            recommendations.append("Excelente progreso. Continúa con las estrategias que te están funcionando")
        
        # Recomendaciones específicas por tipo
        for assessment_type, assessment in latest_assessments.items():
            if assessment_type == "depression":
                depression_assessment = assessment.get("depression_assessment", {})
                if depression_assessment.get("level") == "Alto":
                    recommendations.append("Es importante buscar apoyo profesional para evaluar tu estado de ánimo")
                elif depression_assessment.get("level") == "Moderado":
                    recommendations.append("Considera técnicas de autocuidado y busca apoyo social")
                elif depression_assessment.get("level") == "Bajo":
                    recommendations.append("Mantén las estrategias que te están funcionando")
        
        return recommendations

# Instancia global para uso en otros módulos
mental_health_assessment = MentalHealthAssessment() 