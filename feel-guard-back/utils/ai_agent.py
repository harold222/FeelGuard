import os
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import HTTPException
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Almacenamiento en memoria para las conversaciones (en producción usar Redis o BD)
conversation_memory: Dict[str, List[Dict]] = {}

class SimpleMemory:
    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
    
    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in conversation_memory:
            conversation_memory[session_id] = []
        conversation_memory[session_id].append({"role": role, "content": content})
        if len(conversation_memory[session_id]) > self.max_messages:
            conversation_memory[session_id] = conversation_memory[session_id][-self.max_messages:]
    
    def get_conversation(self, session_id: str) -> List[Dict]:
        return conversation_memory.get(session_id, [])
    
    def clear_conversation(self, session_id: str):
        if session_id in conversation_memory:
            del conversation_memory[session_id]

memory = SimpleMemory(max_messages=20)

class AIAgent:
    def __init__(self):
        self.system_message = (
            """# Overview\nYou are a personal assistant that helps user to fulfill their request.\n\nWhen you are asked to perform a task on the current date, please use the current time and date: {current_time}\n\n## Output\nYou should output the result and don't include any link. Just mentioned where you added it to."""
        )
    
    async def process_message(self, text: str, session_id: str) -> str:
        try:
            conversation_history = memory.get_conversation(session_id)
            messages = [
                {"role": "system", "content": self.system_message.format(current_time=datetime.now().isoformat())}
            ]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": text})
            response = await self.call_openai(messages)
            memory.add_message(session_id, "user", text)
            memory.add_message(session_id, "assistant", response)
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")
    
    async def call_openai(self, messages: List[Dict]) -> str:
        try:
            # Nueva API v1.x
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7
            )
            return completion.choices[0].message.content
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

ai_agent = AIAgent() 