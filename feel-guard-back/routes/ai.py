from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid
from sqlalchemy.orm import Session
from utils.ai_agent import ai_agent, memory
from utils.voice_processor import voice_processor
from utils.auth import get_current_active_user
from models.database import get_db
from models.registro import Registro
from models.chat_history import ChatHistory
from fastapi import status
from datetime import datetime

router = APIRouter()

class TextRequest(BaseModel):
    text: str
    session_id: Optional[str] = None

class AIResponse(BaseModel):
    output: str
    session_id: str
    assessment: Optional[Dict] = None
    risk_level: Optional[str] = None

class ChatHistoryItem(BaseModel):
    id: int
    message: str
    response: str
    created_at: datetime
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserAssessmentSummary(BaseModel):
    user_id: int
    total_conversations: int
    total_assessments: int
    period_days: int
    risk_levels_summary: Dict[str, int]
    assessment_types_summary: Dict[str, int]
    average_risk_score: float
    most_common_concern: str
    recommendations: List[str]

@router.post("/process-text", response_model=AIResponse)
async def process_text_message(
    request: TextRequest,
    db: Session = Depends(get_db),
    current_user: Registro = Depends(get_current_active_user)
):
    """
    Procesa un mensaje de texto y devuelve la respuesta de la IA junto con la evaluación de salud mental.
    """
    session_id = request.session_id or str(uuid.uuid4())
    
    # Procesar el mensaje con la IA
    response = await ai_agent.process_message(request.text, session_id)
    
    # Obtener evaluación de salud mental
    from utils.mental_health_assessment import mental_health_assessment, AssessmentType
    assessment_type = ai_agent.determine_assessment_type(request.text)
    assessment = mental_health_assessment.create_assessment(
        session_id=session_id,
        text=request.text,
        assessment_type=assessment_type
    )
    
    # Guardar historial en la base de datos
    chat_entry = ChatHistory(
        user_id=current_user.id,
        message=request.text,
        response=response
    )
    db.add(chat_entry)
    db.commit()
    db.refresh(chat_entry)
    
    return AIResponse(
        output=response, 
        session_id=session_id,
        assessment=assessment,
        risk_level=assessment.get("risk_level", "low")
    )

@router.post("/process-voice", response_model=AIResponse)
async def process_voice_message(
    audio: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Registro = Depends(get_current_active_user)
):
    """
    Procesa un mensaje de voz, lo transcribe y devuelve la respuesta de la IA junto con la evaluación de salud mental.
    """
    session_id = session_id or str(uuid.uuid4())
    
    # Transcribir audio a texto
    transcribed_text = await voice_processor.transcribe_audio(audio)
    
    # Procesar el texto transcrito con la IA
    response = await ai_agent.process_message(transcribed_text, session_id)
    
    # Obtener evaluación de salud mental
    from utils.mental_health_assessment import mental_health_assessment, AssessmentType
    assessment_type = ai_agent.determine_assessment_type(transcribed_text)
    assessment = mental_health_assessment.create_assessment(
        session_id=session_id,
        text=transcribed_text,
        assessment_type=assessment_type
    )
    
    # Guardar historial en la base de datos
    chat_entry = ChatHistory(
        user_id=current_user.id,
        message=transcribed_text,
        response=response
    )
    db.add(chat_entry)
    db.commit()
    db.refresh(chat_entry)
    
    return AIResponse(
        output=response, 
        session_id=session_id,
        assessment=assessment,
        risk_level=assessment.get("risk_level", "low")
    )

@router.get("/chat-history", response_model=List[ChatHistoryItem])
async def get_chat_history(
    db: Session = Depends(get_db),
    current_user: Registro = Depends(get_current_active_user)
):
    """
    Obtiene el historial completo de chat del usuario autenticado.
    """
    history = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).order_by(ChatHistory.created_at.asc()).all()
    return history

@router.delete("/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """
    Limpia el historial de conversación de una sesión específica.
    """
    memory.clear_conversation(session_id)
    return {"message": f"Conversation {session_id} cleared"}

@router.get("/user-assessment-summary", response_model=UserAssessmentSummary)
async def get_user_assessment_summary(
    current_user: Registro = Depends(get_current_active_user),
    days: int = 30
):
    """
    Obtiene un resumen de todas las evaluaciones del usuario en los últimos días.
    
    Args:
        current_user: Usuario autenticado
        days: Número de días hacia atrás para analizar (por defecto 30)
    
    Returns:
        Resumen de evaluaciones con estadísticas y recomendaciones
    """
    try:
        # Obtener historial de chat del usuario
        db = next(get_db())
        chat_history = db.query(ChatHistory).filter(
            ChatHistory.user_id == current_user.id
        ).order_by(ChatHistory.created_at.desc()).limit(100).all()
        
        if not chat_history:
            return UserAssessmentSummary(
                user_id=current_user.id,
                total_conversations=0,
                total_assessments=0,
                period_days=days,
                risk_levels_summary={},
                assessment_types_summary={},
                average_risk_score=0.0,
                most_common_concern="Sin datos suficientes",
                recommendations=["Comienza una conversación para obtener evaluaciones"]
            )
        
        # Crear un session_id basado en el usuario para análisis
        user_session_id = f"user_{current_user.id}"
        
        # Analizar todos los mensajes del usuario
        from utils.mental_health_assessment import mental_health_assessment, AssessmentType
        
        assessments = []
        risk_levels = []
        assessment_types = []
        
        for chat in chat_history:
            assessment_type = ai_agent.determine_assessment_type(chat.message)
            assessment = mental_health_assessment.create_assessment(
                user_session_id, 
                chat.message, 
                assessment_type
            )
            assessments.append(assessment)
            risk_levels.append(assessment.get("risk_level", "low"))
            assessment_types.append(assessment.get("type", "stress"))
        
        # Calcular estadísticas
        risk_levels_summary = {}
        for level in risk_levels:
            risk_levels_summary[level] = risk_levels_summary.get(level, 0) + 1
        
        assessment_types_summary = {}
        for assessment_type in assessment_types:
            assessment_types_summary[assessment_type] = assessment_types_summary.get(assessment_type, 0) + 1
        
        # Calcular puntuación promedio de riesgo
        risk_scores = {
            "low": 1,
            "moderate": 2,
            "high": 3,
            "critical": 4
        }
        total_risk_score = sum(risk_scores.get(level, 1) for level in risk_levels)
        average_risk_score = total_risk_score / len(risk_levels) if risk_levels else 0
        
        # Determinar preocupación más común
        most_common_concern = max(assessment_types_summary.items(), key=lambda x: x[1])[0] if assessment_types_summary else "Sin datos"
        
        # Generar recomendaciones basadas en los datos
        recommendations = []
        
        if average_risk_score > 2.5:
            recommendations.append("Considera buscar ayuda profesional para evaluar tu situación")
        elif average_risk_score > 1.5:
            recommendations.append("Practica técnicas de relajación y autocuidado regularmente")
        else:
            recommendations.append("Excelente progreso. Continúa con las estrategias que te están funcionando")
        
        if assessment_types_summary.get("stress", 0) > len(assessments) * 0.4:
            recommendations.append("Considera técnicas de manejo del estrés como meditación o ejercicio")
        
        if assessment_types_summary.get("anxiety", 0) > len(assessments) * 0.3:
            recommendations.append("Practica ejercicios de respiración y mindfulness para la ansiedad")
        
        if assessment_types_summary.get("depression", 0) > len(assessments) * 0.2:
            recommendations.append("Es importante buscar apoyo profesional para evaluar tu estado de ánimo")
        
        if len(assessments) < 5:
            recommendations.append("Mantén conversaciones regulares para un mejor seguimiento")
        
        return UserAssessmentSummary(
            user_id=current_user.id,
            total_conversations=len(chat_history),
            total_assessments=len(assessments),
            period_days=days,
            risk_levels_summary=risk_levels_summary,
            assessment_types_summary=assessment_types_summary,
            average_risk_score=round(average_risk_score, 2),
            most_common_concern=most_common_concern,
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error obteniendo resumen de evaluaciones: {str(e)}"
        ) 