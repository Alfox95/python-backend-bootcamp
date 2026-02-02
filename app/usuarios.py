from fastapi import APIRouter, Depends
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
    nuevo = Usuario(nombre=usuario.nombre, edad=usuario.edad)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()
