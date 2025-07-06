import io
from fastapi import UploadFile, HTTPException
import os
from dotenv import load_dotenv
from .langchain_config import langchain_config
import openai
from tempfile import NamedTemporaryFile

load_dotenv()

class VoiceProcessor:
    @staticmethod
    async def transcribe_audio(audio_file: UploadFile) -> str:
        try:
            # Guardar el archivo temporalmente
            with NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
                content = await audio_file.read()
                tmp.write(content)
                tmp_path = tmp.name
            
            with open(tmp_path, "rb") as audio_file:
                transcript = openai.Audio.transcribe(
                    "whisper-1",
                    audio_file,
                    api_key=os.getenv("OPENAI_API_KEY")
                )
            return transcript["text"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")

voice_processor = VoiceProcessor() 