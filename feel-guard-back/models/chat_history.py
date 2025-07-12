from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("registros.id"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    audio_path = Column(String, nullable=True)  # Ruta o nombre del archivo de audio
    message_type = Column(String, default="text")  # "text", "audio" o "image"

    user = relationship("Registro", backref="chat_history") 