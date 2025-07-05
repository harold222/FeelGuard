from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.registro import Registro
from schemas.registro import RegistroCreate, RegistroOut
from utils.auth import create_access_token

router = APIRouter()

@router.post("/registro")
def crear_registro(registro: RegistroCreate, db: Session = Depends(get_db)):
    db_registro = db.query(Registro).filter(Registro.email == registro.email).first()
    if db_registro:
        # Si ya existe, retornar el token y los datos existentes
        token = create_access_token({"usuario": db_registro.email})
        return {
            "success": True,
            "message": "El correo ya estaba registrado.",
            "data": RegistroOut.model_validate(db_registro).model_dump(),
            "token": token
        }
    nuevo = Registro(
        email=registro.email,
        nombre=registro.nombre,
        edad=registro.edad,
        sexo=registro.sexo
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    token = create_access_token({"usuario": nuevo.email})
    return {
        "success": True,
        "message": "Registro exitoso",
        "data": RegistroOut.model_validate(nuevo).model_dump(),
        "token": token
    }

@router.get("/registro/email/{email}", response_model=RegistroOut)
def obtener_registro_por_email(email: str, db: Session = Depends(get_db)):
    registro = db.query(Registro).filter(Registro.email == email).first()
    if not registro:
        raise HTTPException(status_code=404, detail="No existe un registro con ese correo")
    return registro 