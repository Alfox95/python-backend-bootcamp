import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import Base, engine
from app.models import Usuario
import asyncio



# Fixture para el cliente HTTP
@pytest_asyncio.fixture
async def client():
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac



#Test 1: Verificar que la app levanta
@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "mensaje" in data
    assert data["mensaje"] == "Backend Python funcionando"

#Test 2: Crear un usuario
@pytest.mark.asyncio
async def test_crear_usuario(client):
    user_data = {
        "nombre": "UsuarioTest",
        "username": "UsuarioTest",
        "edad": 30,
        "password": "test123",
        "mail": "test@test.compile",
        "es_admin": True
    }

    response = await client.post("/usuarios", json=user_data)
    assert response.status_code == 200, f"Error: {response.text}"

    data= response.json()
    assert "id" in data
    assert data["nombre"] == "UsuarioTest"
    assert "password" not in data

#Test 3: Login con el usuario creado
@pytest.mark.asyncio
async def test_login(client):
    login_data = {
        "username": "UsuarioTest",
        "password": "test123"
    }

    response = await client.post("/login", data=login_data)
    assert response.status_code == 200, f"Login falló: {response.text}"

    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

    return data["access_token"]

#Test 4: Endpoint protegido /usuarios/me
@pytest.mark.asyncio
async def test_endpoint_protegido(client):
    # 1.Login para obtener token
    login_data = {"username": "UsuarioTest", "password":"test123"}
    login_response = await client.post("/login", data=login_data)
    token = login_response.json()["access_token"]

    # 2. Llamar al endpoint protegido con token
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/usuarios/me", headers=headers)

    assert response.status_code == 200, f"Error protegido: {response.text}"

    data = response.json()
    assert "id" in data
    assert "nombre" in data
    assert data["nombre"] == "UsuarioTest"

# Test 5: Error 401 sin token
@pytest.mark.asyncio
async def test_endpoint_sin_token(client):
    response = await client.get("/usuarios/me")
    assert response.status_code == 401, "Debería dar 401"

# Test 6: Listar usuarios (solo si no requiere auth)
@pytest.mark.asyncio
async def test_listar_usuarios(client):
    # Crear usuario
    await client.post("/usuarios", json={
        "nombre": "UsuarioTest",
        "username": "UsuarioTest",
        "edad": 30,
        "password": "test123",
        "mail": "test@test.compile",
        "es_admin": True
    })

    # Login
    login_response = await client.post("/login", data={
        "username": "UsuarioTest",
        "password": "test123"
    })

    token = login_response.json()["access_token"]

    # Llamar endpoint protegido
    response = await client.get(
        "/usuarios",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

# Test 7: Validación de edad negativa
@pytest.mark.asyncio
async def test_validacion_edad_negativa(client):
    user_data = {
        "nombre": "UsuarioInvalido",
        "username": "UsuarioInvalido",
        "edad": -30,
        "password": "test123",
        "mail": "edadinvalida@test.com",
        "es_admin": False
    }

    response = await client.post("/usuarios", json=user_data)
    assert response.status_code == 400, "Debería rechazar edad negativa"
    assert "edad" in response.text.lower() or "negativa" in response.text.lower()

#Test 8: Validación de contraseña corta
@pytest.mark.asyncio
async def test_validacion_password_corta(client):
    user_data = {
        "nombre": "UsuarioPassCorta",
        "username": "UsuarioPassCorta",
        "mail": "passcorta@test.com",
        "edad": 25,
        "password": "123",
        "es_admim": False
    }

    response = await client.post("/usuarios", json=user_data)
    # Debería dar 422 (validación fallida) o 400
    assert response.status_code in [400, 422], f"Error inesperdo: {response.status_code}"
    