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
                "ligero", "leve", "poco", "ocasional", "manejable", "tranquilo", "tranquila", "controlable", "soportable", "no es grave", "puedo manejarlo", "no me afecta mucho", "es pasajero", "es temporal", "me siento bien la mayor parte del tiempo"
            ],
            RiskLevel.MODERATE: [
                "moderado", "regular", "frecuente", "interfiere", "difícil", "dificil", "estresado", "estresada", "tenso", "tensa", "me cuesta", "me afecta", "me preocupa seguido", "me siento presionado", "me siento presionada", "me siento ansioso", "me siento ansiosa", "me siento nervioso", "me siento nerviosa", "me siento inquieto", "me siento inquieta", "me siento inseguro", "me siento insegura", "me siento frustrado", "me siento frustrada", "me siento irritable", "me siento irritable a veces", "me siento cansado", "me siento cansada", "nunca podré", "no puedo lograr", "no tengo posibilidades", "por mi pobreza", "por mi situación", "no merezco", "no valgo", "no soy suficiente", "no tengo oportunidad", "no tengo suerte", "no tengo recursos", "no tengo opción", "no tengo alternativa", "no tengo motivación", "no tengo ilusión", "no tengo sueños", "no tengo metas", "no tengo propósito"
            ],
            RiskLevel.HIGH: [
                "severo", "severa", "intenso", "intensa", "constante", "abrumador", "abrumadora", "no puedo", "no puedo más", "no puedo mas", "no soporto", "no encuentro salida", "me siento atrapado", "me siento atrapada", "me siento sin salida", "me siento desesperado", "me siento desesperada", "me siento muy mal", "me siento fatal", "me siento destruido", "me siento destruida", "no tengo fuerzas", "no tengo energia", "no tengo energía", "no tengo ganas de nada", "no tengo motivación", "no tengo motivacion", "no tengo ilusión", "no tengo ilusion", "no tengo esperanza", "no tengo apoyo", "me siento solo", "me siento sola", "me siento abandonado", "me siento abandonada", "me siento incomprendido", "me siento incomprendida", "me siento muy ansioso", "me siento muy ansiosa", "me siento muy triste", "me siento muy cansado", "me siento muy cansada", "nunca podré", "no puedo lograr", "no tengo futuro", "no tengo posibilidades", "por mi pobreza", "por mi situación", "no merezco", "no valgo", "no soy suficiente", "no tengo oportunidad", "no tengo suerte", "no tengo recursos", "no tengo salida", "no tengo opción", "no tengo alternativa", "no tengo motivación", "no tengo ilusión", "no tengo sueños", "no tengo metas", "no tengo propósito"
            ],
            RiskLevel.CRITICAL: [
                "suicidio", "suicidar", "suicidarme", "suicidarse", "morir", "morirme", "acabar", "acabar con todo", "no aguanto", "no aguanto más", "no aguanto mas", "crisis", "pánico", "panico", "no quiero vivir", "mejor estar muerto", "mejor estar muerta", "no puedo más", "no puedo mas", "me rindo", "quiero acabar con todo", "no le encuentro sentido a la vida", "quiero morir", "no vale la pena vivir", "no tengo ganas de vivir", "me quiero morir", "no tengo motivos para vivir", "no encuentro sentido a nada", "no encuentro sentido", "no quiero seguir", "no quiero seguir viviendo", "no quiero despertar", "quisiera desaparecer", "quisiera no existir", "quisiera no haber nacido", "me haría daño", "me haria daño", "quiero hacerme daño", "quiero hacerme dano", "quiero lastimarme", "quiero lastimarme a mi mismo", "quiero lastimarme a mi misma", "quiero cortarme", "quiero herirme", "quiero autolesionarme", "me autolesiono", "me autolesioné", "me autolesione", "me corto", "me corté", "me corte", "me hago daño", "me hago dano", "me lastimo", "me lastimé", "me lastime", "no puedo respirar", "me voy a morir", "no quiero hablar con nadie", "no quiero ver a nadie", "no quiero salir de la cama", "no quiero salir de mi cuarto", "no quiero hacer nada", "no tengo ganas de nada", "no tengo fuerzas para nada", "no tengo energia para nada", "no tengo energía para nada", "no tengo esperanza en nada", "no tengo apoyo de nadie", "me siento completamente solo", "me siento completamente sola", "me siento vacío", "me siento vacio", "me siento sin valor", "me siento sin sentido", "me siento sin esperanza", "me siento sin futuro", "me siento sin ganas de vivir"
            ]
        }
    
    def assess_risk_level(self, text: str) -> RiskLevel:
        """Evalúa el nivel de riesgo basado en el contenido del texto"""
        text_lower = text.lower()
        # Mejorar: contar matches de frases completas, no solo palabras sueltas
        def count_matches(phrases, text):
            count = 0
            for phrase in phrases:
                if phrase in text:
                    count += 1
            return count
        
        # Verificar nivel crítico primero
        if any(phrase in text_lower for phrase in self.risk_keywords[RiskLevel.CRITICAL]):
            return RiskLevel.CRITICAL
        
        # Contar palabras/frases de cada nivel
        risk_counts = {}
        for level, keywords in self.risk_keywords.items():
            risk_counts[level] = count_matches(keywords, text_lower)

        # Determinar nivel basado en conteos
        if risk_counts[RiskLevel.HIGH] >= 1:
            return RiskLevel.HIGH
        elif risk_counts[RiskLevel.MODERATE] >= 1:
            return RiskLevel.MODERATE
        elif risk_counts[RiskLevel.LOW] >= 1:
            return RiskLevel.LOW
        # Si no hay ningún match, retornar cadena vacía
        return ""
    
    def assess_stress_level(self, text: str) -> Dict:
        """Evalúa específicamente el nivel de estrés"""
        stress_indicators = {
            "físicos": [
                "dolor de cabeza", "tensión", "fatiga", "insomnio", "dolor muscular", "palpitaciones", "sudoración", "temblores", "mareos", "náuseas", "presión en el pecho", "taquicardia", "cansancio", "agotamiento", "malestar físico", "problemas digestivos", "sudor frío"
            ],
            "emocionales": [
                "irritabilidad", "ansiedad", "frustración", "impaciencia", "enojo", "rabia", "tristeza", "llanto fácil", "sentirse abrumado", "desesperanza", "desánimo", "desmotivación",
                "preocupación económica", "preocupación por el dinero", "preocupación por el trabajo", "preocupación por el futuro", "preocupación por la familia", "preocupación por la salud", "preocupación por la situación", "preocupación por la pobreza"
            ],
            "cognitivos": [
                "dificultad para concentrarse", "olvidos", "confusión", "pensamientos acelerados", "preocupación constante", "bloqueo mental", "dificultad para tomar decisiones", "rumiación"
            ],
            "conductuales": [
                "cambios en el apetito", "aislamiento", "procrastinación", "evitación", "consumo de sustancias", "aumento de consumo de café", "fumar más", "comer en exceso", "insomnio conductual", "descuidar responsabilidades"
            ]
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
            "preocupación": [
                "preocupado", "preocupada", "preocupación", "miedo", "temor", "nervioso", "nerviosa", "inquietud", "inseguridad", "pánico", "sentirse en peligro", "anticipación negativa", "temor al futuro",
                "preocupación económica", "preocupación por el dinero", "preocupación por el trabajo", "preocupación por el futuro", "preocupación por la familia", "preocupación por la salud", "preocupación por la situación", "preocupación por la pobreza"
            ],
            "físicos": [
                "palpitaciones", "sudoración", "temblores", "mareos", "náuseas", "opresión en el pecho", "dificultad para respirar", "boca seca", "hormigueo", "tensión muscular", "dolor de estómago", "taquicardia"
            ],
            "cognitivos": [
                "pensamientos intrusivos", "catastrofización", "rumiación", "dificultad para concentrarse", "miedo irracional", "preocupación excesiva", "duda constante", "hipervigilancia"
            ],
            "conductuales": [
                "evitación", "escape", "compulsiones", "revisar repetidamente", "buscar seguridad", "inquietud motora", "incapacidad para quedarse quieto", "morderse las uñas", "tics nerviosos"
            ]
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
            "estado_animo": [
                "triste", "vacío", "sin esperanza", "desesperado", "abatido", "desanimado", "llanto frecuente", "sentirse inútil", "culpa", "vergüenza", "apatía", "indiferencia",
                "nunca podré", "no puedo lograr", "no tengo futuro", "no tengo posibilidades", "por mi pobreza", "por mi situación", "no merezco", "no valgo", "no soy suficiente", "no tengo oportunidad", "no tengo suerte", "no tengo recursos", "no tengo salida", "no tengo opción", "no tengo alternativa", "no tengo motivación", "no tengo ilusión", "no tengo sueños", "no tengo metas", "no tengo propósito"
            ],
            "interés": [
                "pérdida de interés", "sin motivación", "apatía", "nada me interesa", "no disfruto nada", "falta de placer", "anhedonia"
            ],
            "sueño": [
                "insomnio", "dormir demasiado", "cambios en el sueño", "despertar temprano", "dificultad para dormir", "sueño interrumpido", "pesadillas"
            ],
            "apetito": [
                "pérdida de apetito", "comer en exceso", "cambios de peso", "falta de hambre", "aumento de peso", "pérdida de peso"
            ],
            "pensamientos": [
                "culpa", "inutilidad", "muerte", "suicidio", "pensamientos negativos", "pensamientos de autolesión", "deseos de morir", "no vale la pena vivir",
                "nunca podré", "no puedo lograr", "no tengo futuro", "no tengo posibilidades", "por mi pobreza", "por mi situación", "no merezco", "no valgo", "no soy suficiente", "no tengo oportunidad", "no tengo suerte", "no tengo recursos", "no tengo salida", "no tengo opción", "no tengo alternativa", "no tengo motivación", "no tengo ilusión", "no tengo sueños", "no tengo metas", "no tengo propósito"
            ]
        }
        
        text_lower = text.lower()
        scores = {}
        
        for category, indicators in depression_indicators.items():
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
        # Si assessment_type es None, poner cadena vacía
        type_value = assessment_type.value if assessment_type else ""
        risk_level_value = risk_level.value if hasattr(risk_level, 'value') else (risk_level if risk_level else "")
        assessment = {
            "session_id": session_id,
            "type": type_value,
            "risk_level": risk_level_value,
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
        
        return recommendations

# Instancia global para uso en otros módulos
mental_health_assessment = MentalHealthAssessment() 