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
    