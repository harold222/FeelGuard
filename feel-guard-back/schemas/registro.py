from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class RegistroBase(BaseModel):
    email: EmailStr
    nombre: str
    edad: int
    sexo: str

class RegistroCreate(RegistroBase):
    pass

class RegistroOut(RegistroBase):
    id: int
    fecha_registro: datetime

    class Config:
        from_attributes = True 