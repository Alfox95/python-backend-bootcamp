from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator

from app.database import  get_db
from app.auth import get_current_user, requiere_admin
from app.models import Usuario
from app.security import hash_password


router = APIRouter()

class UsuarioCreate(BaseModel):
    username: str
    mail: str
    password: str
    nombre: str
    edad: int
    es_admin: bool = False


    @field_validator("password")
    def validar_password(cls, value):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña es demasiado larga")
        if len(value) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return value

class UsuarioOut(BaseModel):
    id: int
    username: str
    mail: str
    password: str
    nombre: str
    edad: int
    es_admin: bool

@router.post("/usuarios")
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    
    existing = db.query(Usuario).filter(
        (Usuario.username == usuario.username) | (Usuario.mail == usuario.mail)
        ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    if usuario.edad < 0:
        raise HTTPException(status_code=400, detail= "No se puede tener edad negativa"
        )
    
    hashed = hash_password(usuario.password)
    
    nuevo = Usuario(
        username=usuario.username,
        mail=usuario.mail,
        nombre=usuario.nombre, 
        edad=usuario.edad,
        password=hashed,
        es_admin=usuario.es_admin
     )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return {"id": nuevo.id, 
            "nombre": nuevo.nombre,
            "username": nuevo.username,
            "mail": nuevo.mail,
            "edad": nuevo.edad,
            "es_admin": nuevo.es_admin
            }
    

@router.get("/usuarios")
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if not current_user.es_admin:
        raise  HTTPException(status_code=403, detail="No tienes permisos de admin")
    return db.query(Usuario).all()

class UsuarioUpdate(BaseModel):
    nombre: str
    edad: int
    es_admin: bool

@router.get("/usuarios/me")
def leer_mi_usuario(current_user: Usuario = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "mail": current_user.mail,
        "nombre": current_user.nombre,
        "edad": current_user.edad,
        "es_admin": current_user.es_admin
    }

@router.delete("/usuarios/me")
def eliminar_cuenta(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):    
    db.delete(current_user)
    db.commit()
    return {"mensaje": "Ha eliminado su cuenta"}

@router.put("/usuarios/{usuario_id}")
def actualizar_usuario(
    usuario_id: int,
    datos: UsuarioUpdate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(requiere_admin)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail= "Usuario no encontrado")
    
    usuario.nombre = datos.nombre
    usuario.edad = datos.edad
    usuario.es_admin = datos.es_admin

    db.commit()
    db.refresh(usuario)
    return usuario

@router.delete("/usuarios/{usuario_id}")
def eliminar_usuario(
    usuario_id : int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(requiere_admin)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario: 
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    

    db.delete(usuario)
    db.commit()
    return {"mensaje": "Usuario eliminado"}



@router.get("/usuarios/{usuario_id}", response_model=UsuarioOut)
def buscar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

