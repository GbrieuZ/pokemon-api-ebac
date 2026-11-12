import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.main import app, get_db
from app.schemas import PokemonUpdate

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


# ---------- CRUD básico ----------

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


# ---------- PUT: duplicidade e nulos ----------

def test_update_duplicate_name_returns_400():
    client.post("/pokemons", json=PIKACHU)
    raichu = client.post(
        "/pokemons", json={"name": "raichu", "type": "electric"}
    ).json()
    r = client.put(f"/pokemons/{raichu['id']}", json={"name": "pikachu"})
    assert r.status_code == 400
    assert r.json()["detail"] == "Pokémon já existe"


def test_update_same_name_is_allowed():
    created = client.post("/pokemons", json=PIKACHU).json()
    r = client.put(f"/pokemons/{created['id']}", json={"name": "pikachu", "weight": 70})
    assert r.status_code == 200
    assert r.json()["weight"] == 70


def test_update_name_null_returns_422():
    created = client.post("/pokemons", json=PIKACHU).json()
    r = client.put(f"/pokemons/{created['id']}", json={"name": None})
    assert r.status_code == 422


def test_update_type_null_returns_422():
    created = client.post("/pokemons", json=PIKACHU).json()
    r = client.put(f"/pokemons/{created['id']}", json={"type": None})
    assert r.status_code == 422


def test_update_omitting_name_and_type_is_allowed():
    created = client.post("/pokemons", json=PIKACHU).json()
    r = client.put(f"/pokemons/{created['id']}", json={"height": 5})
    assert r.status_code == 200
    assert r.json()["name"] == "pikachu"
    assert r.json()["type"] == "electric"
    assert r.json()["height"] == 5


# ---------- POST: nome e tipo vazios ----------

@pytest.mark.parametrize("valor", ["", "   ", "\t\n"])
def test_create_blank_name_returns_422(valor):
    r = client.post("/pokemons", json={"name": valor, "type": "electric"})
    assert r.status_code == 422


@pytest.mark.parametrize("valor", ["", "   "])
def test_create_blank_type_returns_422(valor):
    r = client.post("/pokemons", json={"name": "pikachu", "type": valor})
    assert r.status_code == 422


def test_create_trims_name_and_type():
    r = client.post("/pokemons", json={"name": "  pikachu  ", "type": " electric "})
    assert r.status_code == 201
    assert r.json()["name"] == "pikachu"
    assert r.json()["type"] == "electric"


def test_create_name_with_spaces_is_duplicate_returns_400():
    client.post("/pokemons", json=PIKACHU)
    r = client.post("/pokemons", json={"name": " pikachu ", "type": "electric"})
    assert r.status_code == 400


# ---------- PUT: nome e tipo vazios ----------

@pytest.mark.parametrize("valor", ["", "   "])
def test_update_blank_name_returns_422(valor):
    created = client.post("/pokemons", json=PIKACHU).json()
    r = client.put(f"/pokemons/{created['id']}", json={"name": valor})
    assert r.status_code == 422


@pytest.mark.parametrize("valor", ["", "   "])
def test_update_blank_type_returns_422(valor):
    created = client.post("/pokemons", json=PIKACHU).json()
    r = client.put(f"/pokemons/{created['id']}", json={"type": valor})
    assert r.status_code == 422


def test_update_blank_name_on_second_pokemon_returns_422():
    client.post("/pokemons", json=PIKACHU)
    raichu = client.post(
        "/pokemons", json={"name": "raichu", "type": "electric"}
    ).json()
    r = client.put(f"/pokemons/{raichu['id']}", json={"name": ""})
    assert r.status_code == 422


def test_update_name_with_spaces_is_duplicate_returns_400():
    client.post("/pokemons", json=PIKACHU)
    raichu = client.post(
        "/pokemons", json={"name": "raichu", "type": "electric"}
    ).json()
    r = client.put(f"/pokemons/{raichu['id']}", json={"name": " pikachu "})
    assert r.status_code == 400


def test_update_trims_name():
    created = client.post("/pokemons", json=PIKACHU).json()
    r = client.put(f"/pokemons/{created['id']}", json={"name": "  raichu  "})
    assert r.status_code == 200
    assert r.json()["name"] == "raichu"


# ---------- Limites numéricos ----------

@pytest.mark.parametrize("campo", ["height", "weight"])
@pytest.mark.parametrize("valor", [-1, 2147483648])
def test_create_invalid_number_returns_422(campo, valor):
    r = client.post("/pokemons", json={**PIKACHU, campo: valor})
    assert r.status_code == 422


@pytest.mark.parametrize("valor", [-1, 2147483648])
def test_update_invalid_number_returns_422(valor):
    created = client.post("/pokemons", json=PIKACHU).json()
    r = client.put(f"/pokemons/{created['id']}", json={"weight": valor})
    assert r.status_code == 422


def test_update_height_null_is_allowed():
    created = client.post("/pokemons", json=PIKACHU).json()
    r = client.put(f"/pokemons/{created['id']}", json={"height": None})
    assert r.status_code == 200
    assert r.json()["height"] is None


# ---------- Documentação (schema do PUT) ----------

def test_update_schema_documents_name_and_type_as_string_only():
    schema = PokemonUpdate.model_json_schema()
    for campo in ("name", "type"):
        prop = schema["properties"][campo]
        assert prop["type"] == "string"
        assert "anyOf" not in prop
        assert "default" not in prop
        assert campo not in schema.get("required", [])