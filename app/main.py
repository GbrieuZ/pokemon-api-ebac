from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.models import Pokemon
from app.schemas import (
    PokemonCreate, PokemonUpdate, PokemonOut, PokemonList, ErrorResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Pokémon API", lifespan=lifespan)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_or_404(db: Session, pokemon_id: int) -> Pokemon:
    pokemon = db.get(Pokemon, pokemon_id)
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokémon não encontrado")
    return pokemon


def commit_ou_400(db: Session) -> None:
    """Rede de segurança: nome duplicado vira 400, nunca 500."""
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Pokémon já existe")


@app.post(
    "/pokemons",
    response_model=PokemonOut,
    status_code=201,
    summary="Criar pokémon",
    responses={
        201: {
            "description": "Pokémon criado",
            "content": {"application/json": {"example": {
                "id": 1, "name": "pikachu", "type": "electric",
                "height": 4, "weight": 60}}},
        },
        400: {
            "model": ErrorResponse,
            "description": "Pokémon com esse nome já existe",
            "content": {"application/json": {"example": {"detail": "Pokémon já existe"}}},
        },
    },
)
def create_pokemon(data: PokemonCreate, db: Session = Depends(get_db)):
    if db.query(Pokemon).filter(Pokemon.name == data.name).first():
        raise HTTPException(status_code=400, detail="Pokémon já existe")
    pokemon = Pokemon(**data.model_dump())
    db.add(pokemon)
    commit_ou_400(db)
    db.refresh(pokemon)
    return pokemon


@app.get(
    "/pokemons",
    response_model=PokemonList,
    summary="Listar pokémons (paginado, com busca por nome)",
)
def list_pokemons(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    name: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Pokemon)
    if name:
        query = query.filter(Pokemon.name.ilike(f"%{name}%"))
    total = query.count()
    items = query.order_by(Pokemon.id).offset(offset).limit(limit).all()
    return {"data": items,
            "pagination": {"total": total, "limit": limit, "offset": offset}}


@app.get(
    "/pokemons/{pokemon_id}",
    response_model=PokemonOut,
    summary="Buscar pokémon por id",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Pokémon não encontrado",
            "content": {"application/json": {"example": {"detail": "Pokémon não encontrado"}}},
        },
    },
)
def get_pokemon(pokemon_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, pokemon_id)


@app.put(
    "/pokemons/{pokemon_id}",
    response_model=PokemonOut,
    summary="Atualizar pokémon (parcial)",
    description=(
        "Atualização parcial. `name` e `type` podem ser omitidos, mas, se "
        "enviados, devem ser textos não vazios (`null`, vazio ou só espaços "
        "retornam 422). `height` e `weight` aceitam `null`."
    ),
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Já existe outro pokémon com esse nome",
            "content": {"application/json": {"example": {"detail": "Pokémon já existe"}}},
        },
        404: {
            "model": ErrorResponse,
            "description": "Pokémon não encontrado",
            "content": {"application/json": {"example": {"detail": "Pokémon não encontrado"}}},
        },
    },
)
def update_pokemon(pokemon_id: int, data: PokemonUpdate,
                   db: Session = Depends(get_db)):
    pokemon = get_or_404(db, pokemon_id)
    changes = data.model_dump(exclude_unset=True)

    new_name = changes.get("name")
    if new_name is not None and new_name != pokemon.name:
        duplicate = db.query(Pokemon).filter(
            Pokemon.name == new_name, Pokemon.id != pokemon_id
        ).first()
        if duplicate:
            raise HTTPException(status_code=400, detail="Pokémon já existe")

    for field, value in changes.items():
        setattr(pokemon, field, value)
    commit_ou_400(db)
    db.refresh(pokemon)
    return pokemon


@app.delete(
    "/pokemons/{pokemon_id}",
    status_code=204,
    summary="Excluir pokémon",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Pokémon não encontrado",
            "content": {"application/json": {"example": {"detail": "Pokémon não encontrado"}}},
        },
    },
)
def delete_pokemon(pokemon_id: int, db: Session = Depends(get_db)):
    pokemon = get_or_404(db, pokemon_id)
    db.delete(pokemon)
    db.commit()