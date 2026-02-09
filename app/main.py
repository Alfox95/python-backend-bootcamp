from fastapi import FastAPI
from app.usuarios import router as usuarios_router
from app.auth import router as auth_router
from app.database import Base, engine
from app.models import Usuario  

app = FastAPI()

Base.metadata.create_all(bind=engine)

# Endpoints del mòdulo usuarios
app.include_router(usuarios_router)
app.include_router(auth_router)


@app.get("/")
def read_root():
    return{"mensaje": "Backend Python funcionando"}