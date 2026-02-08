import sys
import os

# Agregar directorio padre al path para todos los tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import Base, engine, SessionLocal

@pytest_asyncio.fixture(scope="session", autouse=True)
def create_test_db():
    """
    Crea todas las tablas antes de los tests y limpia después.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest_asyncio.fixture
async def client():
    """
    Cliente HTTP para tests, usando ASGI transport (FastAPI app en memoria).
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
def db_session():
    """
    Fixture para obtener sesión de DB en tests si la necesitas directamente.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()