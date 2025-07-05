import io
from fastapi import UploadFile, HTTPException
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class VoiceProcessor:
    @staticmethod
    async def transcribe_audio(audio_file: UploadFile) -> str:
        try:
            audio_data = await audio_file.read()
            audio_io = io.BytesIO(audio_data)
            audio_io.name = audio_file.filename or "audio.webm"
            # Nueva API v1.x
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_io
            )
            return transcript.text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")

voice_processor = VoiceProcessor() 