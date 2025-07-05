from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel
from typing import Optional, List
import uuid
from sqlalchemy.orm import Session
from utils.ai_agent import ai_agent, memory
from utils.voice_processor import voice_processor
from utils.auth import get_current_active_user
from models.database import get_db
from models.registro import Registro
from models.chat_history import ChatHistory
from fastapi import status

router = APIRouter()

class TextRequest(BaseModel):
    text: str
    session_id: Optional[str] = None

class AIResponse(BaseModel):
    output: str
    session_id: str

class ChatHistoryItem(BaseModel):
    id: int
    message: str
    response: str
    created_at: str
    class Config:
        orm_mode = True

@router.post("/process-text", response_model=AIResponse)
async def process_text_message(
    request: TextRequest,
    db: Session = Depends(get_db),
    current_user: Registro = Depends(get_current_active_user)
):
    session_id = request.session_id or str(uuid.uuid4())
    response = await ai_agent.process_message(request.text, session_id)
    # Guardar historial en la base de datos
    chat_entry = ChatHistory(
        user_id=current_user.id,
        message=request.text,
        response=response
    )
    db.add(chat_entry)
    db.commit()
    db.refresh(chat_entry)
    return AIResponse(output=response, session_id=session_id)

@router.post("/process-voice", response_model=AIResponse)
async def process_voice_message(
    audio: UploadFile = File(...),
    session_id: Optional[str] = Form(None)
):
    session_id = session_id or str(uuid.uuid4())
    transcribed_text = await voice_processor.transcribe_audio(audio)
    response = await ai_agent.process_message(transcribed_text, session_id)
    return AIResponse(output=response, session_id=session_id)

@router.get("/conversation/{session_id}")
async def get_conversation_history(session_id: str):
    history = memory.get_conversation(session_id)
    return {"session_id": session_id, "conversation": history}

@router.delete("/conversation/{session_id}")
async def clear_conversation(session_id: str):
    memory.clear_conversation(session_id)
    return {"message": f"Conversation {session_id} cleared"}

@router.post("/process", response_model=AIResponse)
async def process_universal(
    text: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    session_id: Optional[str] = Form(None)
):
    session_id = session_id or str(uuid.uuid4())
    if text and audio:
        raise HTTPException(status_code=400, detail="Send either text or audio, not both")
    if not text and not audio:
        raise HTTPException(status_code=400, detail="Must provide either text or audio")
    if text:
        response = await ai_agent.process_message(text, session_id)
    else:
        transcribed_text = await voice_processor.transcribe_audio(audio)
        response = await ai_agent.process_message(transcribed_text, session_id)
    return AIResponse(output=response, session_id=session_id)

@router.get("/chat-history", response_model=List[ChatHistoryItem], status_code=status.HTTP_200_OK)
async def get_chat_history(
    db: Session = Depends(get_db),
    current_user: Registro = Depends(get_current_active_user)
):
    history = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).order_by(ChatHistory.created_at.asc()).all()
    return history 