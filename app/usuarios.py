from fastapi import APIRouter

router = APIRouter()

# Lista de usuarios como base de datos temporal
usuarios = [
    {"id": 1, "nombre": "Ana", "edad": 28},
    {"id": 2, "nombre": "Juan", "edad": 35}
]

# Ruta para ver todos los usuarios
@router.get("/usuarios")
def obtener_usuarios():
    return usuarios

# Ruta para ver un usuario por ID
@router.get("/usuarios/{usuario_id}")
def obtener_usuario(usuario_id: int):
    for u in usuarios:
        if u["id"] == usuario_id:
            return u
    return {"error": "Usuario no encontrado"}    

@router.get("/usuarios/mayores/{edad_minima}")
def usuarios_mayores(edad_minima: int):
    resultado = []
    for u in usuarios:
        if u["edad"] >= edad_minima:
            resultado.append(u)
    return resultado
    
from pydantic import BaseModel

class UsuarioCreate(BaseModel):
    nombre: str
    edad: int


@router.post("/usuarios")
def crear_usuario(usuario: UsuarioCreate):
    nuevo_usuario = {
        "id": len(usuarios) + 1,
        "nombre": usuario.nombre,
        "edad": usuario.edad
    }
    usuarios.append(nuevo_usuario)
    return nuevo_usuario

