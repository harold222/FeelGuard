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
from fastapi.responses import JSONResponse
from utils.depression_image_classifier import image_classifier
import httpx
import paho.mqtt.client as mqtt
import json
import asyncio
import threading
import time

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

class ESP32ValidationRequest(BaseModel):
    probability: float
    level: str
    confidence: float
    type: str

class MQTTClient:
    def __init__(self):
        try:
            # Intentar con la nueva API primero
            self.client = mqtt.Client("FeelGuard-Backend", callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        except (TypeError, AttributeError):
            # Fallback a la API antigua
            self.client = mqtt.Client("FeelGuard-Backend")
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.connected = False
        self.last_message = None
        self.message_received = threading.Event()
        
    def on_connect(self, client, userdata, flags, rc):
        print(f"Conectado a MQTT con código: {rc}")
        self.connected = True
        # Suscribirse al topic para recibir datos del sensor
        client.subscribe("wokwi/depresion/bpm")
        
    def on_message(self, client, userdata, msg):
        print(f"Mensaje recibido en {msg.topic}: {msg.payload}")
        try:
            self.last_message = json.loads(msg.payload.decode())
            self.message_received.set()
        except Exception as e:
            print(f"Error al procesar mensaje MQTT: {e}")
            
    def on_disconnect(self, client, userdata, rc):
        print(f"Desconectado de MQTT con código: {rc}")
        self.connected = False
        
    def connect(self):
        try:
            self.client.connect("test.mosquitto.org", 1883, 60)
            self.client.loop_start()
            # Esperar a que se conecte
            timeout = 10
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            return self.connected
        except Exception as e:
            print(f"Error conectando a MQTT: {e}")
            return False
            
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        
    def publish(self, topic, message):
        if self.connected:
            self.client.publish(topic, message)
            return True
        return False
        
    def wait_for_response(self, timeout=30):
        """Espera por una respuesta del sensor"""
        if self.message_received.wait(timeout):
            message = self.last_message
            self.message_received.clear()
            self.last_message = None
            return message
        return None

# Instancia global del cliente MQTT
mqtt_client = MQTTClient()

# Inicializar conexión MQTT al arrancar
@router.on_event("startup")
async def startup_event():
    """Inicializar conexión MQTT al arrancar la aplicación"""
    try:
        if mqtt_client.connect():
            print("✅ Conexión MQTT establecida exitosamente")
        else:
            print("❌ No se pudo establecer conexión MQTT")
    except Exception as e:
        print(f"❌ Error al conectar MQTT: {e}")

@router.on_event("shutdown")
async def shutdown_event():
    """Cerrar conexión MQTT al apagar la aplicación"""
    try:
        mqtt_client.disconnect()
        print("✅ Conexión MQTT cerrada")
    except Exception as e:
        print(f"❌ Error al cerrar MQTT: {e}")

UPLOAD_DIR = "uploads"
UPLOAD_IMAGE_DIR = "uploads/images"
os.makedirs(UPLOAD_IMAGE_DIR, exist_ok=True)

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

@router.post("/process-image")
async def process_image(
    image: UploadFile = File(...),
    session_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Registro = Depends(get_current_active_user)
):
    """
    Procesa una imagen enviada por el usuario, la clasifica con el modelo de depresión y guarda el historial.
    """
    session_id = session_id or str(uuid.uuid4())
    # Guardar la imagen en disco
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    ext = os.path.splitext(image.filename)[-1] or ".jpg"
    image_filename = f"{session_id}_{timestamp}{ext}"
    image_path = os.path.join(UPLOAD_IMAGE_DIR, image_filename)
    content = await image.read()
    with open(image_path, "wb") as f:
        f.write(content)
    # Clasificación con el modelo entrenado
    result = image_classifier.classify(image_bytes=io.BytesIO(content))
    # Determinar nivel de depresión
    confidence = result["confidence"]
    if result["is_depression"]:
        if confidence >= 0.8:
            level = "Alto"
        elif confidence >= 0.6:
            level = "Moderado"
        else:
            level = "Bajo"
    else:
        level = "Sin indicadores"
    # Guardar historial en la base de datos (como texto, para mantener consistencia)
    from models.chat_history import ChatHistory
    chat_entry = ChatHistory(
        user_id=current_user.id,
        message=f"[Imagen] {image_filename}",
        response=f"Clasificación: {result['label']} (Nivel: {level}, Confianza: {confidence:.2f})",
        audio_path=image_path,  # Reutilizamos el campo para guardar la ruta de la imagen
        message_type="image"
    )
    db.add(chat_entry)
    db.commit()
    db.refresh(chat_entry)
    # Estructura de respuesta compatible con AIResponse
    # Traducción de label
    label_map = {"neutral": "Neutral", "depression": "Depresión"}
    label_es = label_map.get(result["label"].lower(), result["label"].capitalize())
    # Construir output
    if result["label"].lower() == "neutral":
        output = f"Clasificación: {label_es}"
    else:
        output = f"Clasificación: {label_es} (Nivel: {level}, Confianza: {confidence:.2f})"
    depression_classification = {
        "is_depression": result["is_depression"],
        "confidence": result["confidence"],
        "probability": [result["probabilities"]["neutral"], result["probabilities"]["depression"]],
        "label": label_es,
        "level": level
    }
    return {
        "output": output,
        "session_id": session_id,
        "assessment": None,
        "risk_level": level.lower() if result["is_depression"] else "low",
        "depression_classification": depression_classification,
        "image_path": f"/uploads/images/{image_filename}",
        "history_id": chat_entry.id
    }

@router.get("/chat-history", response_model=List[ChatHistoryItem])
async def get_chat_history(
    db: Session = Depends(get_db),
    current_user: Registro = Depends(get_current_active_user)
):
    """
    Obtiene el historial completo de chat del usuario autenticado.
    """
    history = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).order_by(ChatHistory.created_at.asc()).all()
    result = []
    for chat in history:
        item = {
            "id": chat.id,
            "message": chat.message,
            "response": chat.response,
            "created_at": chat.created_at,
            "message_type": chat.message_type,
            "image_path": ""
        }
        if chat.message_type == "audio" and chat.audio_path:
            item["audio_path"] = chat.audio_path.replace("\\", "/") if chat.audio_path else None
        elif chat.message_type == "image":
            # Normalizar path y asegurar que sea absoluto
            path = (chat.audio_path or "").replace("\\", "/")
            if not path:
                # Buscar el nombre del archivo en el mensaje tipo "[Imagen] nombre_archivo.jpg"
                import re
                match = re.search(r"\[Imagen\]\s*([^\s]+)", chat.message or "")
                if match:
                    filename = match.group(1)
                    path = f"/uploads/images/{filename}"
                else:
                    path = ""
            else:
                # Si el path no comienza con /uploads/, normalizarlo
                if path.startswith("uploads/"):
                    path = "/" + path
                else:
                    path = "/uploads/images/" + path.split("/")[-1]
            item["image_path"] = path or ""
        result.append(item)
    return result

@router.delete("/clear-conversation")
async def clear_conversation(
    db: Session = Depends(get_db),
    current_user: Registro = Depends(get_current_active_user)
):
    """
    Limpia todo el historial de conversación del usuario autenticado y elimina los archivos de audio e imagen asociados.
    """
    # Buscar todos los mensajes del usuario
    history = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).all()
    # Eliminar archivos de audio e imagen si existen
    for chat in history:
        if chat.message_type == "audio" and chat.audio_path:
            try:
                if os.path.exists(chat.audio_path):
                    os.remove(chat.audio_path)
            except Exception as e:
                print(f"No se pudo eliminar el archivo de audio: {chat.audio_path}. Error: {e}")
        if chat.message_type == "image" and chat.audio_path:
            try:
                if os.path.exists(chat.audio_path):
                    os.remove(chat.audio_path)
            except Exception as e:
                print(f"No se pudo eliminar el archivo de imagen: {chat.audio_path}. Error: {e}")
    # Eliminar los mensajes del historial
    db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).delete()
    db.commit()
    # Limpiar la memoria en RAM (por usuario)
    return {"message": f"Historial del usuario {current_user.id} eliminado, incluyendo archivos de audio e imagen."}

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
        
        # Generar recomendaciones detalladas y personalizadas
        recommendations = []
        
        # 1. Recomendaciones basadas en el puntaje promedio de riesgo
        if average_risk_score >= 3.5:
            recommendations.extend([
                "🚨 **URGENTE**: Considera contactar inmediatamente a un profesional de salud mental",
                "💡 Practica técnicas de respiración profunda cuando sientas ansiedad",
                "📞 Mantén contacto regular con amigos y familiares",
                "🏥 Considera buscar ayuda en servicios de crisis si es necesario"
            ])
        elif average_risk_score >= 2.5:
            recommendations.extend([
                "⚠️ **IMPORTANTE**: Busca ayuda profesional para evaluar tu situación",
                "🧘‍♀️ Practica meditación diaria por al menos 10 minutos",
                "📝 Mantén un diario de emociones para identificar patrones"
            ])
        elif average_risk_score >= 1.5:
            recommendations.extend([
                "💪 **PROGRESO**: Continúa con las estrategias que te están funcionando",
                "🌅 Establece una rutina matutina saludable",
                "🎯 Practica técnicas de mindfulness durante el día",
                "📚 Lee sobre bienestar emocional y autocuidado"
            ])
        else:
            recommendations.extend([
                "🌟 **EXCELENTE**: Tu bienestar emocional está en buen estado",
                "✨ Mantén las prácticas positivas que has desarrollado",
                "🤝 Ayuda a otros que puedan estar pasando por dificultades",
                "📈 Continúa monitoreando tu estado de ánimo regularmente"
            ])
        
        # 2. Recomendaciones basadas en el tipo de evaluación más común
        depression_count = assessment_types_summary.get("depression", 0)
        neutral_count = assessment_types_summary.get("neutral", 0)
        total_assessments = len(assessments)
        
        if depression_count > total_assessments * 0.4:
            recommendations.extend([
                "🌞 Expón tu piel a la luz solar por 15-20 minutos diarios",
                "😴 Establece una rutina de sueño consistente (7-9 horas)"
            ])
        elif depression_count > total_assessments * 0.2:
            recommendations.extend([
                "🤔 **SEÑALES**: Presta atención a cambios en tu estado de ánimo",
                "🎨 Practica actividades creativas para expresar emociones",
                "🌿 Considera técnicas de aromaterapia con aceites esenciales",
                "📱 Limita el uso de redes sociales si afectan tu ánimo"
            ])
        
        # 3. Recomendaciones basadas en la frecuencia de uso
        if len(assessments) < 3:
            recommendations.extend([
                "📊 **SEGUIMIENTO**: Mantén conversaciones regulares para mejor monitoreo",
                "📱 Usa la app al menos 3 veces por semana para seguimiento"
            ])
        elif len(assessments) > 20:
            recommendations.extend([
                "📈 **COMPROMISO**: Excelente dedicación al seguimiento de tu salud mental",
                "📊 Revisa tu progreso semanalmente para identificar tendencias"
            ])
        
        # 4. Recomendaciones basadas en la distribución de niveles de riesgo
        high_critical_count = risk_levels_summary.get("high", 0) + risk_levels_summary.get("critical", 0)
        if high_critical_count > total_assessments * 0.3:
            recommendations.extend([
                "📞 Ten a mano números de emergencia y líneas de crisis",
                "👥 Busca grupos de apoyo para personas con experiencias similares"
            ])
        
        # 5. Recomendaciones basadas en la tendencia temporal (si hay suficientes datos)
        if len(assessments) >= 5:
            recent_assessments = assessments[:5]  # Últimos 5
            recent_risk_levels = [a.get("risk_level", "") for a in recent_assessments if a.get("risk_level")]
            recent_avg = sum(risk_scores.get(level, 0) for level in recent_risk_levels) / len(recent_risk_levels) if recent_risk_levels else 0
            
            if recent_avg < average_risk_score * 0.8:
                recommendations.extend([
                    "📈 **MEJORANDO**: ¡Excelente progreso! Tu estado de ánimo está mejorando",
                    "🎉 Celebra tus pequeños logros diarios",
                    "🔄 Mantén las estrategias que están funcionando"
                ])
            elif recent_avg > average_risk_score * 1.2:
                recommendations.extend([
                    "🔍 Identifica qué factores pueden estar contribuyendo",
                    "🤝 Busca apoyo adicional de profesionales o seres queridos"
                ])
        
        # Limitar a máximo 15 recomendaciones para no abrumar
        recommendations = recommendations[:10]
        
        # Traducir las claves del risk_levels_summary a español
        risk_levels_summary_es = {}
        risk_level_translation = {
            "low": "bajo",
            "moderate": "moderado", 
            "high": "alto",
            "critical": "crítico"
        }
        
        for level_en, count in risk_levels_summary.items():
            level_es = risk_level_translation.get(level_en, level_en)
            risk_levels_summary_es[level_es] = count
        
        return UserAssessmentSummary(
            user_id=current_user.id,
            total_conversations=len(chat_history),
            total_assessments=len(assessments),
            period_days=days,
            risk_levels_summary=risk_levels_summary_es,
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

@router.post("/validate-depression-esp32")
async def validate_depression_with_esp32(
    request: ESP32ValidationRequest,
    current_user: Registro = Depends(get_current_active_user)
):
    """
    Envía datos de depresión a la ESP32 para validación con sensores físicos usando MQTT.
    
    Args:
        request: Datos de depresión a validar
        current_user: Usuario autenticado
    
    Returns:
        Respuesta de la ESP32 con validación
    """
    try:
        # Conectar a MQTT si no está conectado
        if not mqtt_client.connected:
            if not mqtt_client.connect():
                return {
                    "success": False,
                    "message": "No se pudo conectar al broker MQTT. Verifica la conexión de red.",
                    "esp32_response": None
                }
        
        # Preparar datos para enviar a la ESP32
        esp32_data = {
            "probability": request.probability,
            "level": request.level,
            "confidence": request.confidence,
            "type": request.type,
            "user_id": current_user.id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Publicar mensaje de inicio en MQTT
        start_message = {
            "level": request.level,
            "probability": request.probability,
            "confidence": request.confidence,
            "type": request.type,
            "user_id": current_user.id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Publicar en el topic de inicio
        if mqtt_client.publish("wokwi/depresion/start", json.dumps(start_message)):
            print(f"Mensaje publicado en MQTT: {start_message}")
            
            # Esperar respuesta del sensor (máximo 30 segundos)
            sensor_response = mqtt_client.wait_for_response(timeout=30)
            
            if sensor_response:
                return {
                    "success": True,
                    "message": "Validación con sensores físicos completada exitosamente",
                    "esp32_response": sensor_response
                }
            else:
                return {
                    "success": False,
                    "message": "No se recibió respuesta del sensor en el tiempo esperado.",
                    "esp32_response": None
                }
        else:
            return {
                "success": False,
                "message": "No se pudo publicar el mensaje en MQTT. Verifica la conexión al broker.",
                "esp32_response": None
            }
                
    except Exception as e:
        print(f"Error en validación MQTT: {e}")
        return {
            "success": False,
            "message": f"Error al validar con sensores físicos: {str(e)}",
            "esp32_response": None
        } 