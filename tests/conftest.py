"""
Configuración compartida para tests con pytest.

Este módulo configura fixtures y dependencias compartidas para todos los tests:
- Base de datos de test temporal SQLite
- Cliente de test de FastAPI
- Override de dependencias para testing

La configuración asegura que cada test se ejecute con un entorno limpio
y predecible, usando una base de datos temporal que se crea y destruye
automáticamente.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel

from app.main import app
from app.database import get_db

# Base de datos de prueba en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})


def get_test_db():
    """
    Dependencia de base de datos para tests.
    
    Proporciona una sesión de base de datos temporal que se usa
    únicamente durante los tests, aislando los tests de la base
    de datos de producción/desarrollo.
    
    Yields:
        Session: Sesión de SQLModel para operaciones de BD
    """
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_db] = get_test_db

client = TestClient(app)


@pytest.fixture(scope="session")
def setup_database():
    """
    Setup de base de datos de prueba.
    
    Fixture que se ejecuta una vez por sesión de tests:
    1. Crea todas las tablas necesarias en la BD de test
    2. Yield para que se ejecuten los tests
    3. Limpia todas las tablas al finalizar
    
    Scope='session' significa que se ejecuta una sola vez
    para toda la suite de tests.
    
    Yields:
        None: Permite que se ejecuten los tests
    """
    SQLModel.metadata.create_all(bind=engine)
    yield
    SQLModel.metadata.drop_all(bind=engine)


@pytest.fixture
def client_fixture():
    """
    Cliente de test para hacer requests HTTP.
    
    Proporciona un TestClient de FastAPI configurado para hacer
    requests a la aplicación durante los tests. El cliente está
    configurado para usar la base de datos de test.
    
    Returns:
        TestClient: Cliente de test de FastAPI
    """
    return client
