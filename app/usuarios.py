from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator

from app.database import  get_db
from app.auth import get_current_user
from app.models import Usuario

from app.security import hash_password, verify_password
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter()

class UsuarioCreate(BaseModel):
    nombre: str
    edad: int
    password: str

    @field_validator("password")
    def validar_password(cls, value):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña es demasiado larga")
        if len(value) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return value


@router.post("/usuarios")
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    
    if usuario.edad < 0:
        raise HTTPException(status_code=400, detail= "No se puede tener edad negativa"
        )
    
    hashed = hash_password(usuario.password)
    
    nuevo = Usuario(
        nombre=usuario.nombre, 
        edad=usuario.edad,
        password=hashed)

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return {"id": nuevo.id, "nombre": nuevo.nombre}
    

@router.get("/usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()

class UsuarioUpdate(BaseModel):
    nombre: str
    edad: int

@router.put("/usuarios/{usuario_id}")
def actualizar_usuario(
    usuario_id: int,
    datos: UsuarioUpdate,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail= "Usuario no encontrado")
    
    usuario.nombre = datos.nombre
    usuario.edad = datos.edad

    db.commit()
    db.refresh(usuario)
    return usuario

@router.delete("/usuarios/{usuario_id}")
def eliminar_usuario(
    usuario_id = int,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario: 
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(usuario)
    db.commit()
    return {"mensaje": "Usuario eliminado"}

@router.get("/usuarios/me")
def leer_mi_usuario(current_user: Usuario = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "nombre": current_user.nombre,
        "edad": current_user.edad
    }

@router.get("/usuarios/{usuario_id}")
def buscar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="El usuario con ese ID no existe")
    
    return usuario

