import os
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import HTTPException
from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from .langchain_config import langchain_config
from .mental_health_prompts import mental_health_prompts
from .mental_health_assessment import mental_health_assessment, AssessmentType

load_dotenv()

# Configurar el modelo de LangChain con OpenAI usando la configuración centralizada
llm = langchain_config.get_chat_model()

# Almacenamiento en memoria para las conversaciones (en producción usar Redis o BD)
conversation_memory: Dict[str, ConversationBufferMemory] = {}

class SimpleMemory:
    def __init__(self, max_messages: int = 30):
        self.max_messages = max_messages
    
    def get_memory(self, session_id: str) -> ConversationBufferMemory:
        if session_id not in conversation_memory:
            conversation_memory[session_id] = ConversationBufferMemory(
                return_messages=True,
                max_token_limit=6000  # Aproximadamente 30 mensajes
            )
        return conversation_memory[session_id]
    
    def clear_conversation(self, session_id: str):
        if session_id in conversation_memory:
            del conversation_memory[session_id]

memory = SimpleMemory(max_messages=30)

class AIAgent:
    def __init__(self):
        self.system_message = mental_health_prompts.get_system_prompt()
        self.crisis_keywords = [
            "suicidio", "suicidar", "matar", "morir", "muerte", "no quiero vivir",
            "mejor estar muerto", "acabar con todo", "no aguanto más",
            "autolesión", "cortarme", "herirme", "dolor físico", "crisis",
            "ataque de pánico", "no puedo respirar", "me voy a morir",
            "pensamientos intrusivos", "voces", "alucinaciones", 
            "no valgo para nada", "nadie me quiere", "sería mejor no existir"
            "estoy harto(a) de vivir", "no siento ganas de seguir", "todo da igual"
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
    
    def determine_assessment_type(self, text: str) -> AssessmentType:
        """Determina el tipo de evaluación basado en el contenido del texto"""
        text_lower = text.lower()
        
        # Detectar crisis primero (prioridad máxima)
        if self.detect_crisis(text):
            return AssessmentType.CRISIS
        
        # Detectar patrones específicos
        if any(word in text_lower for word in ["estrés", "estresado", "estresada", "tenso", "tensa", "presión"]):
            return AssessmentType.STRESS
        
        if any(word in text_lower for word in ["ansiedad", "ansioso", "ansiosa", "preocupado", "preocupada", "pánico"]):
            return AssessmentType.ANXIETY
        
        if any(word in text_lower for word in [
            "depresión", "deprimido", "deprimida", "triste", "sin esperanza", "vacío", "problema",
            "abrumado", "abrumada", "no encuentro salida", "no tengo ganas", "no tengo fuerzas", "no puedo más", "no puedo mas", "me siento vacío", "me siento vacio", "me siento solo", "me siento sola", "me siento sin esperanza", "me siento sin salida", "me siento destruido", "me siento destruida", "me siento fatal", "me siento sin valor", "me siento sin sentido", "me siento sin futuro", "me siento sin ganas de vivir",
            "nunca podré", "no puedo lograr", "no tengo futuro", "no tengo posibilidades", "por mi pobreza", "por mi situación", "no merezco", "no valgo", "no soy suficiente", "no tengo oportunidad", "no tengo suerte", "no tengo recursos", "no tengo salida", "no tengo opción", "no tengo alternativa", "no tengo motivación", "no tengo ilusión", "no tengo sueños", "no tengo metas", "no tengo propósito"
        ]):
            return AssessmentType.DEPRESSION
        
        if any(word in text_lower for word in ["bienestar", "salud", "ejercicio", "sueño", "alimentación"]):
            return AssessmentType.WELLNESS
        
        # Por defecto, si no coincide con ningún patrón, retornar None
        return None
    
    def get_appropriate_prompt(self, text: str, conversation_history: List[str]) -> str:
        """Determina el prompt más apropiado basado en el contenido del mensaje"""
        text_lower = text.lower()
        
        # Detectar crisis primero (prioridad máxima)
        if self.detect_crisis(text):
            return mental_health_prompts.get_crisis_intervention_prompt()
        
        # Detectar patrones específicos
        if any(word in text_lower for word in ["estrés", "estresado", "estresada", "tenso", "tensa", "presión"]):
            return mental_health_prompts.get_stress_assessment_prompt()
        
        if any(word in text_lower for word in ["ansiedad", "ansioso", "ansiosa", "preocupado", "preocupada", "pánico"]):
            return mental_health_prompts.get_anxiety_assessment_prompt()
        
        if any(word in text_lower for word in ["depresión", "deprimido", "deprimida", "triste", "sin esperanza", "vacío", "problema"]):
            return mental_health_prompts.get_depression_assessment_prompt()
        
        if any(word in text_lower for word in ["bienestar", "salud", "ejercicio", "sueño", "alimentación"]):
            return mental_health_prompts.get_wellness_assessment_prompt()
        
        # Si es una conversación continua, usar prompt de seguimiento
        if len(conversation_history) > 2:
            return mental_health_prompts.get_follow_up_prompt()
        
        # Prompt general por defecto
        return self.system_message
    
    async def process_message(self, text: str, session_id: str) -> str:
        try:
            # Obtener la memoria de conversación para esta sesión
            conversation_memory = memory.get_memory(session_id)
            
            # Obtener historial de conversación
            conversation_history = conversation_memory.chat_memory.messages
            history_text = "\n".join([f"{msg.type}: {msg.content}" for msg in conversation_history[-6:]])  # Últimos 6 mensajes
            
            # Determinar el tipo de evaluación
            assessment_type = self.determine_assessment_type(text)
            
            # Crear evaluación estructurada
            assessment = mental_health_assessment.create_assessment(
                session_id=session_id,
                text=text,
                assessment_type=assessment_type
            )
            
            # Determinar el prompt más apropiado
            system_prompt = self.get_appropriate_prompt(text, history_text)
            system_prompt = system_prompt.format(current_time=datetime.now().isoformat())
            
            # Agregar información de evaluación al prompt si es relevante
            if assessment["risk_level"] in ["high", "critical"]:
                system_prompt += f"\n\nIMPORTANTE: Se ha detectado un nivel de riesgo {assessment['risk_level']} en el mensaje del usuario. Prioriza la seguridad y proporciona recursos de ayuda apropiados."
            
            # Crear la cadena de conversación con memoria
            conversation = ConversationChain(
                llm=llm,
                memory=conversation_memory,
                verbose=False
            )
            
            # Crear el prompt personalizado usando ChatPromptTemplate
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "Conversación anterior:\n{history}\n\nUsuario: {input}\n\nAsistente:")
            ])
            
            conversation.prompt = prompt
            
            # Procesar el mensaje
            response = await conversation.arun(text)
            
            # Si se detectó crisis, agregar recursos de emergencia
            if self.detect_crisis(text):
                emergency_resources = """
                
                ⚠️ **RECURSOS DE EMERGENCIA** ⚠️
                
                Si estás en crisis o tienes pensamientos suicidas:
                - Línea Nacional de Prevención del Suicidio (EE.UU.): 988
                - Crisis Text Line: Envía "HOME" al 741741
                - Servicios de emergencia: 911
                - Habla con alguien de confianza inmediatamente
                
                Tu vida es valiosa. Por favor, busca ayuda profesional inmediata."""
                response += emergency_resources
            
            return response.strip()
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

ai_agent = AIAgent() 