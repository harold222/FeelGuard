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
import os
from tempfile import NamedTemporaryFile
import io

router = APIRouter()

class TextRequest(BaseModel):
    text: str
    session_id: Optional[str] = None

class AIResponse(BaseModel):
    output: str
    session_id: str
    assessment: Optional[Dict] = None
    risk_level: Optional[str] = None
    depression_classification: Optional[Dict] = None

class ChatHistoryItem(BaseModel):
    id: int
    message: str
    response: str
    created_at: datetime
    audio_path: Optional[str] = None
    message_type: Optional[str] = "text"
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

UPLOAD_DIR = "uploads"

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
    
    # Obtener clasificación del modelo de depresión
    from utils.depression_classifier import depression_classifier
    depression_classification = depression_classifier.classify_text(request.text)
    
    # Guardar historial en la base de datos
    chat_entry = ChatHistory(
        user_id=current_user.id,
        message=request.text,
        response=response
    )
    db.add(chat_entry)
    db.commit()
    db.refresh(chat_entry)
    
    # Validar que risk_level esté presente
    if "risk_level" not in assessment:
        raise HTTPException(status_code=500, detail="No se pudo determinar el nivel de riesgo")
    
    return AIResponse(
        output=response, 
        session_id=session_id,
        assessment=assessment,
        risk_level=assessment["risk_level"],
        depression_classification=depression_classification
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
    # Guardar el archivo de audio en uploads/
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    audio_filename = f"{session_id}_{audio.filename}"
    audio_path = os.path.join(UPLOAD_DIR, audio_filename)
    content = await audio.read()
    with open(audio_path, "wb") as f:
        f.write(content)
    # Transcribir audio a texto usando el mismo contenido
    audio_bytes = io.BytesIO(content)
    audio_bytes.name = audio.filename if audio.filename else "audio.webm"
    transcribed_text = await voice_processor.transcribe_audio_from_bytes(audio_bytes)
    # Procesar el texto transcrito con la IA
    response = await ai_agent.process_message(transcribed_text, session_id)
    # Guardar historial en la base de datos
    chat_entry = ChatHistory(
        user_id=current_user.id,
        message=transcribed_text,
        response=response,
        audio_path=audio_path,
        message_type="audio"
    )
    db.add(chat_entry)
    db.commit()
    db.refresh(chat_entry)
    from utils.mental_health_assessment import mental_health_assessment, AssessmentType
    assessment_type = ai_agent.determine_assessment_type(transcribed_text)
    assessment = mental_health_assessment.create_assessment(
        session_id=session_id,
        text=transcribed_text,
        assessment_type=assessment_type
    )
    
    # Obtener clasificación del modelo de depresión
    from utils.depression_classifier import depression_classifier
    depression_classification = depression_classifier.classify_text(transcribed_text)
    
    # Validar que risk_level esté presente
    if "risk_level" not in assessment:
        raise HTTPException(status_code=500, detail="No se pudo determinar el nivel de riesgo")
    
    return AIResponse(
        output=response, 
        session_id=session_id,
        assessment=assessment,
        risk_level=assessment["risk_level"],
        depression_classification=depression_classification
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

@router.delete("/clear-conversation")
async def clear_conversation(
    db: Session = Depends(get_db),
    current_user: Registro = Depends(get_current_active_user)
):
    """
    Limpia todo el historial de conversación del usuario autenticado y elimina los archivos de audio asociados.
    """
    # Buscar todos los mensajes del usuario
    history = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).all()
    # Eliminar archivos de audio si existen
    for chat in history:
        if chat.message_type == "audio" and chat.audio_path:
            try:
                if os.path.exists(chat.audio_path):
                    os.remove(chat.audio_path)
            except Exception as e:
                print(f"No se pudo eliminar el archivo de audio: {chat.audio_path}. Error: {e}")
    # Eliminar los mensajes del historial
    db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).delete()
    db.commit()
    # Limpiar la memoria en RAM (por usuario)
    # Si tienes session_id, podrías limpiar por sesión, pero aquí limpiamos todo
    return {"message": f"Historial del usuario {current_user.id} eliminado, incluyendo archivos de audio."}

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
            risk_levels.append(assessment.get("risk_level", ""))
            assessment_types.append(assessment.get("type", ""))
        
        # Filtrar vacíos
        filtered_risk_levels = [level for level in risk_levels if level]
        filtered_assessment_types = [atype for atype in assessment_types if atype]
        # Calcular estadísticas
        risk_levels_summary = {}
        for level in filtered_risk_levels:
            risk_levels_summary[level] = risk_levels_summary.get(level, 0) + 1
        assessment_types_summary = {}
        for assessment_type in filtered_assessment_types:
            assessment_types_summary[assessment_type] = assessment_types_summary.get(assessment_type, 0) + 1
        # Calcular puntuación promedio de riesgo
        risk_scores = {
            "low": 1,
            "moderate": 2,
            "high": 3,
            "critical": 4
        }
        total_risk_score = sum(risk_scores.get(level, 0) for level in filtered_risk_levels)
        average_risk_score = total_risk_score / len(filtered_risk_levels) if filtered_risk_levels else 0
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