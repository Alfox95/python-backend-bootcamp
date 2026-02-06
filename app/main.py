from fastapi import FastAPI
from app.usuarios import router as usuarios_router
from app.auth import router as auth_router

app = FastAPI()

# Endpoints del mòdulo usuarios
app.include_router(usuarios_router)
app.include_router(auth_router)


@app.get("/")
def read_root():
    return{"mensaje": "Backend Python funcionando"}