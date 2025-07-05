from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models.database import get_db
from models.registro import Registro
from schemas.user import UserUpdate, RegistroOut
from utils.auth import get_current_active_user, get_password_hash

router = APIRouter()

@router.get("/", response_model=List[RegistroOut])
def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: Registro = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de usuarios (solo para superusuarios)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    users = db.query(Registro).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=RegistroOut)
def get_user(
    user_id: int,
    current_user: Registro = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener un usuario específico"""
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    user = db.query(Registro).filter(Registro.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=RegistroOut)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: Registro = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar información de usuario"""
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(Registro).filter(Registro.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Actualizar campos si se proporcionan
    if user_update.email is not None:
        # Verificar si el email ya existe
        existing_user = db.query(Registro).filter(
            Registro.email == user_update.email,
            Registro.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user.email = user_update.email
    
    if user_update.username is not None:
        # Verificar si el username ya existe
        existing_user = db.query(Registro).filter(
            Registro.username == user_update.username,
            Registro.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        user.username = user_update.username
    
    if hasattr(user_update, 'full_name') and user_update.full_name is not None:
        user.full_name = user_update.full_name
    
    if user_update.password is not None:
        user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: Registro = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar un usuario (solo para superusuarios)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(Registro).filter(Registro.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"} 