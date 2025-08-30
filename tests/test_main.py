"""
Tests principales de la aplicación FastAPI.

Este módulo contiene tests de integración para los endpoints principales
de la aplicación, incluyendo autenticación, registro de usuarios y
funcionalidades básicas.

Tests incluidos:
- test_root_endpoint: Test del endpoint raíz
- test_health_check: Test del health check
- test_register_user: Test de registro de usuarios
- test_login_user: Test de login de usuarios
- test_get_current_user: Test de obtener usuario actual

Los tests usan el fixture client_fixture que proporciona un cliente
de test con una base de datos temporal SQLite en memoria.
"""
import pytest
from tests.conftest import client


def test_root_endpoint(client_fixture):
    """Test del endpoint raíz"""
    response = client_fixture.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check(client_fixture):
    """
    Test del endpoint de health check.
    
    Verifica que el endpoint /health responda correctamente
    con status healthy y información de versión.
    
    Args:
        client_fixture: Cliente de test proporcionado por pytest
    """
    response = client_fixture.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_register_user(client_fixture):
    """
    Test de registro de usuario nuevo.
    
    Verifica que el endpoint de registro funcione correctamente:
    - Acepte datos válidos de usuario
    - Retorne el usuario creado con ID
    - No incluya la contraseña en la respuesta
    
    Args:
        client_fixture: Cliente de test proporcionado por pytest
    """
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123"
    }
    
    response = client_fixture.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data


def test_login_user(client_fixture):
    """
    Test de autenticación de usuario.
    
    Verifica el flujo completo de login:
    1. Registra un usuario nuevo
    2. Intenta hacer login con las credenciales
    3. Verifica que retorne un token JWT válido
    
    Args:
        client_fixture: Cliente de test proporcionado por pytest
    """
    # Primero registrar usuario
    user_data = {
        "email": "login@example.com",
        "username": "loginuser",
        "password": "loginpassword123"
    }
    client_fixture.post("/api/v1/auth/register", json=user_data)
    
    # Luego hacer login
    login_data = {
        "username": "loginuser",
        "password": "loginpassword123"
    }
    
    response = client_fixture.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_current_user(client_fixture):
    """
    Test de obtención del usuario actual autenticado.
    
    Verifica el flujo completo de autenticación:
    1. Registra un usuario nuevo
    2. Hace login para obtener token JWT
    3. Usa el token para obtener datos del usuario actual
    4. Verifica que los datos coincidan
    
    Args:
        client_fixture: Cliente de test proporcionado por pytest
    """
    # Registrar y hacer login
    user_data = {
        "email": "current@example.com",
        "username": "currentuser",
        "password": "currentpassword123"
    }
    client_fixture.post("/api/v1/auth/register", json=user_data)
    
    login_response = client_fixture.post("/api/v1/auth/login", data={
        "username": "currentuser",
        "password": "currentpassword123"
    })
    token = login_response.json()["access_token"]
    
    # Obtener usuario actual
    headers = {"Authorization": f"Bearer {token}"}
    response = client_fixture.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "currentuser"
    assert data["email"] == "current@example.com"
