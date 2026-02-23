import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models import Usuario


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

async def crear_admin(client, username:str):
        user_data = {
        "nombre": "UsuarioTest",
        "username": username,
        "edad": 30,
        "password": "test123",
        "mail": username + "@test.com",
        "es_admin": True
    }
        return await client.post("/usuarios", json=user_data)

async def crear_usuario(client, username : str):
        user_data = {
        "nombre": "UserTest",
        "username": username,
        "mail": username + "@test.com",
        "edad": 25,
        "password": "test123",
        "es_admin": False
    }
        return await client.post("/usuarios", json=user_data)

async def user_token(client, username :str):
    await crear_usuario(client, username)

    login = await client.post("/login", data={
        "username": username,
        "password": "test123"
    })
    us_token = login.json()["access_token"]
    return us_token

async def admin_token(client, username :str):
    await crear_admin(client, username)

    login = await client.post("/login", data={
        "username": username,
        "password": "test123"
    })
    ad_token = login.json()["access_token"]
    return ad_token



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

    response = await crear_admin(client, "Admin1")
    response2 = await crear_usuario(client, "Usuario1")
    assert response.status_code == 200, f"Error: {response.text}"
    assert response2.status_code == 200, f"Error: {response.text}"

    data= response.json()
    data2= response2.json()
    assert "id" in data, "id" in data2
    assert data["nombre"] == "UsuarioTest", data2["nombre"] == "NoAdmin"
    assert "password" not in data, "password" not in data2

#Test 3: Login con el usuario creado
@pytest.mark.asyncio
async def test_login(client):
    await crear_admin(client, "Login")

    response = await client.post("/login", data= {
        "username": "Login", 
        "password": "test123"
        })
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
    token = await admin_token(client, "Endpoint")

    # 2. Llamar al endpoint protegido con token
    response = await client.get("/usuarios/me", headers=auth_headers(token))

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
    # Login
    token = await admin_token(client, "Listar")

    # Llamar endpoint protegido
    response = await client.get(
        "/usuarios",
        headers=auth_headers(token)
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
        "es_admin": False
    }

    response = await client.post("/usuarios", json=user_data)
    # Debería dar 422 (validación fallida) o 400
    assert response.status_code in [400, 422], f"Error inesperdo: {response.status_code}"

#Test 9: Usuario no admin puede eliminar
@pytest.mark.asyncio
async def test_user_eliminarse(client):

    token = await user_token(client, "Eliminarse")

    response = await client.delete("/usuarios/me", headers=auth_headers(token))
    assert response.status_code == 200

#Test 10: Usuario no admin no puede eliminar
@pytest.mark.asyncio
async def test_user_no_elimina(client):
    token = await user_token(client, "No_admin")
    
    me = await client.get("/usuarios/me", headers=auth_headers(token))
    user_id = me.json()["id"]

    headers = {"Authorization": f"Bearer {token}"}   

    response = await client.delete(f"/usuarios/{user_id}", headers=headers)
    assert response.status_code == 403

#Test 11: Usuario no lista todos los usuarios
@pytest.mark.asyncio
async def test_user_no_lista_usuarios(client):
    # Login
    token = await user_token(client, "No_Listar")

    # Llamar endpoint protegido
    response = await client.get(
        "/usuarios",
        headers=auth_headers(token)
    )

    assert response.status_code == 403

#Test 12: Usuario no edita
@pytest.mark.asyncio
async def test_user_no_edita(client):
    
    token = await user_token(client, "No_edita")
    me = await client.get("/usuarios/me", headers=auth_headers(token))
    user_id = me.json()["id"]

    response = await client.put(
        f"/usuarios/{user_id}", 
        headers= auth_headers(token),
        json= {"nombre": "Edita",
                "edad": 10,
                "es_admin": True} 
        )
    
    assert response.status_code == 403

#Test 13: Usuario lee usuario
@pytest.mark.asyncio
async def test_user_lee_datos(client):
    token = await user_token(client,"Leo_datos")

    response = await client.get("/usuarios/me", headers=auth_headers(token))
    assert response.status_code == 200

#Test 14: Usuario busca usuario
@pytest.mark.asyncio
async def test_user_busca_user(client):
    token = await user_token(client,"Busco")
    token2 = await user_token(client,"Encontrado")

    user2 = await client.get("/usuarios/me", headers=auth_headers(token2))
    user_id = user2.json()["id"]

    headers = {"Authorization": f"Bearer {token}"}   

    response = await client.get(f"/usuarios/{user_id}", headers=headers)
    assert response.status_code == 200

#Test 15: Admin puede eliminarse
@pytest.mark.asyncio
async def test_admin_eliminarse(client):

    token = await admin_token(client, "Eliminarse")

    response = await client.delete("/usuarios/me", headers=auth_headers(token))
    assert response.status_code == 200

#Test 16: Admin puede eliminar
@pytest.mark.asyncio
async def test_admin_elimina(client):
    token = await admin_token(client, "Admin")
    token2= await user_token(client,"No_admin")
    
    me = await client.get("/usuarios/me", headers=auth_headers(token2))
    user_id = me.json()["id"]

    headers = {"Authorization": f"Bearer {token}"}   

    response = await client.delete(f"/usuarios/{user_id}", headers=headers)
    assert response.status_code == 200

#Test 17: Admin edita
@pytest.mark.asyncio
async def test_admin_edita(client):

    token = await admin_token(client, "Edita")
    token2 = await user_token(client, "No_edita")
    me = await client.get("/usuarios/me", headers=auth_headers(token2))
    user_id = me.json()["id"]

    response = await client.put(
        f"/usuarios/{user_id}", 
        headers= auth_headers(token),
        json= {"nombre": "Editado",
                "edad": 10,
                "es_admin": True} 
        )
    
    assert response.status_code == 200

#Test 18: Admin lee usuario
@pytest.mark.asyncio
async def test_admin_lee_datos(client):
    token = await admin_token(client,"Leo_datos")

    response = await client.get("/usuarios/me", headers=auth_headers(token))
    assert response.status_code == 200

#Test 19: Admin busca usuario
@pytest.mark.asyncio
async def test_admin_busca_user(client):
    token = await admin_token(client,"Busco")
    token2 = await user_token(client,"Encontrado")

    user2 = await client.get("/usuarios/me", headers=auth_headers(token2))
    user_id = user2.json()["id"]

    headers = {"Authorization": f"Bearer {token}"}   

    response = await client.get(f"/usuarios/{user_id}", headers=headers)
    assert response.status_code == 200