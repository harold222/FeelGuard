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
            # Lee el contenido del archivo subido
            content = await audio_file.read()
            if not content:
                raise HTTPException(status_code=400, detail="El archivo de audio está vacío.")
            # Forzar extensión .webm si no está presente
            filename = audio_file.filename
            if not filename or not filename.lower().endswith((
                '.webm', '.mp3', '.wav', '.m4a', '.mp4', '.mpga', '.mpeg')):
                filename = 'audio.webm'
            # Usa io.BytesIO para simular un archivo
            audio_bytes = io.BytesIO(content)
            audio_bytes.name = filename
            return await VoiceProcessor.transcribe_audio_from_bytes(audio_bytes)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")

    @staticmethod
    async def transcribe_audio_from_bytes(audio_bytes: io.BytesIO) -> str:
        try:
            audio_bytes.seek(0)
            transcript = openai.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio_bytes,
                response_format="text"
            )
            return transcript
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")

voice_processor = VoiceProcessor() 