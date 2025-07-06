"""
Sistema de evaluación estructurada para salud mental en Feel Guard
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json

class AssessmentType(Enum):
    STRESS = "stress"
    ANXIETY = "anxiety"
    DEPRESSION = "depression"
    WELLNESS = "wellness"
    CRISIS = "crisis"

class RiskLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

class MentalHealthAssessment:
    def __init__(self):
        self.assessment_history: Dict[str, List[Dict]] = {}
        self.risk_keywords = {
            RiskLevel.LOW: [
                "ligero", "leve", "poco", "ocasional", "manejable"
            ],
            RiskLevel.MODERATE: [
                "moderado", "regular", "frecuente", "interfiere", "difícil"
            ],
            RiskLevel.HIGH: [
                "severo", "intenso", "constante", "abrumador", "no puedo"
            ],
            RiskLevel.CRITICAL: [
                "suicidio", "morir", "acabar", "no aguanto", "crisis", "pánico"
            ]
        }
    
    def assess_risk_level(self, text: str) -> RiskLevel:
        """Evalúa el nivel de riesgo basado en el contenido del texto"""
        text_lower = text.lower()
        
        # Verificar nivel crítico primero
        if any(keyword in text_lower for keyword in self.risk_keywords[RiskLevel.CRITICAL]):
            return RiskLevel.CRITICAL
        
        # Contar palabras de cada nivel
        risk_counts = {}
        for level, keywords in self.risk_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            risk_counts[level] = count
        
        # Determinar nivel basado en conteos
        if risk_counts[RiskLevel.HIGH] >= 2:
            return RiskLevel.HIGH
        elif risk_counts[RiskLevel.MODERATE] >= 2:
            return RiskLevel.MODERATE
        elif risk_counts[RiskLevel.LOW] >= 1:
            return RiskLevel.LOW
        
        return RiskLevel.LOW
    
    def assess_stress_level(self, text: str) -> Dict:
        """Evalúa específicamente el nivel de estrés"""
        stress_indicators = {
            "físicos": ["dolor de cabeza", "tensión", "fatiga", "insomnio", "dolor muscular"],
            "emocionales": ["irritabilidad", "ansiedad", "frustración", "impaciencia"],
            "cognitivos": ["dificultad para concentrarse", "olvidos", "confusión"],
            "conductuales": ["cambios en el apetito", "aislamiento", "procrastinación"]
        }
        
        text_lower = text.lower()
        scores = {}
        
        for category, indicators in stress_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            scores[category] = score
        
        total_score = sum(scores.values())
        
        if total_score >= 6:
            level = "Alto"
        elif total_score >= 3:
            level = "Moderado"
        else:
            level = "Bajo"
        
        return {
            "level": level,
            "score": total_score,
            "categories": scores,
            "timestamp": datetime.now().isoformat()
        }
    
    def assess_anxiety_level(self, text: str) -> Dict:
        """Evalúa específicamente el nivel de ansiedad"""
        anxiety_indicators = {
            "preocupación": ["preocupado", "preocupada", "preocupación", "miedo", "temor"],
            "físicos": ["palpitaciones", "sudoración", "temblores", "mareos", "náuseas"],
            "cognitivos": ["pensamientos intrusivos", "catastrofización", "rumiación"],
            "conductuales": ["evitación", "escape", "compulsiones"]
        }
        
        text_lower = text.lower()
        scores = {}
        
        for category, indicators in anxiety_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            scores[category] = score
        
        total_score = sum(scores.values())
        
        if total_score >= 5:
            level = "Alto"
        elif total_score >= 2:
            level = "Moderado"
        else:
            level = "Bajo"
        
        return {
            "level": level,
            "score": total_score,
            "categories": scores,
            "timestamp": datetime.now().isoformat()
        }
    
    def assess_depression_level(self, text: str) -> Dict:
        """Evalúa específicamente el nivel de depresión"""
        depression_indicators = {
            "estado_animo": ["triste", "vacío", "sin esperanza", "desesperado"],
            "interés": ["pérdida de interés", "sin motivación", "apatía"],
            "sueño": ["insomnio", "dormir demasiado", "cambios en el sueño"],
            "apetito": ["pérdida de apetito", "comer en exceso", "cambios de peso"],
            "pensamientos": ["culpa", "inutilidad", "muerte", "suicidio"]
        }
        
        text_lower = text.lower()
        scores = {}
        
        for category, indicators in depression_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            scores[category] = score
        
        total_score = sum(scores.values())
        
        if total_score >= 6:
            level = "Alto"
        elif total_score >= 3:
            level = "Moderado"
        else:
            level = "Bajo"
        
        return {
            "level": level,
            "score": total_score,
            "categories": scores,
            "timestamp": datetime.now().isoformat()
        }
    
    def assess_wellness_level(self, text: str) -> Dict:
        """Evalúa el nivel de bienestar general"""
        wellness_indicators = {
            "físico": ["ejercicio", "sueño", "alimentación", "energía"],
            "emocional": ["feliz", "contento", "satisfecho", "paz"],
            "social": ["amigos", "familia", "relaciones", "apoyo"],
            "ocupacional": ["trabajo", "estudios", "propósito", "logros"]
        }
        
        text_lower = text.lower()
        scores = {}
        
        for category, indicators in wellness_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            scores[category] = score
        
        total_score = sum(scores.values())
        
        if total_score >= 4:
            level = "Alto"
        elif total_score >= 2:
            level = "Moderado"
        else:
            level = "Bajo"
        
        return {
            "level": level,
            "score": total_score,
            "categories": scores,
            "timestamp": datetime.now().isoformat()
        }
    
    def create_assessment(self, session_id: str, text: str, assessment_type: AssessmentType) -> Dict:
        """Crea una evaluación completa"""
        risk_level = self.assess_risk_level(text)
        
        assessment = {
            "session_id": session_id,
            "type": assessment_type.value,
            "risk_level": risk_level.value,
            "timestamp": datetime.now().isoformat(),
            "text_sample": text[:200] + "..." if len(text) > 200 else text
        }
        
        # Agregar evaluaciones específicas
        if assessment_type == AssessmentType.STRESS:
            assessment["stress_assessment"] = self.assess_stress_level(text)
        elif assessment_type == AssessmentType.ANXIETY:
            assessment["anxiety_assessment"] = self.assess_anxiety_level(text)
        elif assessment_type == AssessmentType.DEPRESSION:
            assessment["depression_assessment"] = self.assess_depression_level(text)
        elif assessment_type == AssessmentType.WELLNESS:
            assessment["wellness_assessment"] = self.assess_wellness_level(text)
        elif assessment_type == AssessmentType.CRISIS:
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
        
        values = [level_values[level] for level in risk_levels]
        
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
            if assessment_type == "stress" and assessment.get("stress_assessment", {}).get("level") == "Alto":
                recommendations.append("Practica técnicas de relajación como respiración profunda o meditación")
            
            elif assessment_type == "anxiety" and assessment.get("anxiety_assessment", {}).get("level") == "Alto":
                recommendations.append("Considera técnicas de mindfulness y ejercicios de respiración")
            
            elif assessment_type == "depression" and assessment.get("depression_assessment", {}).get("level") == "Alto":
                recommendations.append("Es importante buscar apoyo profesional para evaluar tu estado de ánimo")
            
            elif assessment_type == "wellness" and assessment.get("wellness_assessment", {}).get("level") == "Bajo":
                recommendations.append("Intenta incorporar pequeñas actividades de autocuidado en tu rutina diaria")
        
        return recommendations

# Instancia global para uso en otros módulos
mental_health_assessment = MentalHealthAssessment() 