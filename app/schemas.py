from pydantic import BaseModel, ConfigDict


class PokemonCreate(BaseModel):
    name: str
    type: str
    height: int | None = None
    weight: int | None = None


class PokemonUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    height: int | None = None
    weight: int | None = None


class PokemonOut(PokemonCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class Pagination(BaseModel):
    total: int
    limit: int
    offset: int


class PokemonList(BaseModel):
    data: list[PokemonOut]
    pagination: Pagination