import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.main import app, get_db

engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSession = sessionmaker(bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

PIKACHU = {"name": "pikachu", "type": "electric", "height": 4, "weight": 60}


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


def test_create_pokemon():
    r = client.post("/pokemons", json=PIKACHU)
    assert r.status_code == 201
    assert r.json()["name"] == "pikachu"
    assert "id" in r.json()


def test_create_duplicate_returns_400():
    client.post("/pokemons", json=PIKACHU)
    r = client.post("/pokemons", json=PIKACHU)
    assert r.status_code == 400


def test_list_with_pagination():
    for i in range(5):
        client.post("/pokemons", json={"name": f"poke{i}", "type": "normal"})
    r = client.get("/pokemons?limit=2&offset=2")
    body = r.json()
    assert r.status_code == 200
    assert len(body["data"]) == 2
    assert body["pagination"] == {"total": 5, "limit": 2, "offset": 2}


def test_get_pokemon():
    created = client.post("/pokemons", json=PIKACHU).json()
    r = client.get(f"/pokemons/{created['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "pikachu"


def test_get_not_found():
    r = client.get("/pokemons/999")
    assert r.status_code == 404


def test_update_pokemon():
    created = client.post("/pokemons", json=PIKACHU).json()
    r = client.put(f"/pokemons/{created['id']}", json={"weight": 99})
    assert r.status_code == 200
    assert r.json()["weight"] == 99
    assert r.json()["name"] == "pikachu"


def test_update_not_found():
    r = client.put("/pokemons/999", json={"weight": 1})
    assert r.status_code == 404


def test_delete_pokemon():
    created = client.post("/pokemons", json=PIKACHU).json()
    assert client.delete(f"/pokemons/{created['id']}").status_code == 204
    assert client.get(f"/pokemons/{created['id']}").status_code == 404