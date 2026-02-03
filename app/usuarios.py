from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import SessionLocal
from app.models import Usuario


router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UsuarioCreate(BaseModel):
    nombre: str
    edad: int


@router.post("/usuarios")
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    
    if usuario.edad < 0:
        raise HTTPException(status_code=400, detail= "No se puede tener edad negativa"
        )
    
    nuevo = Usuario(nombre=usuario.nombre, edad=usuario.edad)

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo
    


    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

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

@router.get("/usuarios/{usuario_id}")
def buscar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="El usuario con ese ID no existe")
    
    return usuario