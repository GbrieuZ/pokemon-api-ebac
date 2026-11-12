from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


Texto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Inteiro = Annotated[int, Field(ge=0, le=2_147_483_647)]


class PokemonCreate(BaseModel):
    name: Texto = Field(
        description="Nome único do pokémon. Não pode ser vazio nem só espaços.",
        examples=["pikachu"],
    )
    type: Texto = Field(
        description="Tipo do pokémon. Não pode ser vazio nem só espaços.",
        examples=["electric"],
    )
    height: Inteiro | None = Field(default=None, examples=[4])
    weight: Inteiro | None = Field(default=None, examples=[60])


def _remove_default_nulo(schema: dict) -> None:
    """Evita que o Swagger sugira 'default: null' para name e type."""
    for campo in ("name", "type"):
        schema.get("properties", {}).get(campo, {}).pop("default", None)


class PokemonUpdate(BaseModel):
    model_config = ConfigDict(json_schema_extra=_remove_default_nulo)

    name: Texto = Field(
        default=None,
        description=(
            "Opcional. Pode ser omitido, mas se enviado deve ser um texto "
            "não vazio. null não é aceito (422)."
        ),
        examples=["raichu"],
    )
    type: Texto = Field(
        default=None,
        description=(
            "Opcional. Pode ser omitido, mas se enviado deve ser um texto "
            "não vazio. null não é aceito (422)."
        ),
        examples=["electric"],
    )
    height: Inteiro | None = Field(
        default=None, description="Opcional. Aceita null para limpar o valor.",
        examples=[8],
    )
    weight: Inteiro | None = Field(
        default=None, description="Opcional. Aceita null para limpar o valor.",
        examples=[300],
    )


class PokemonOut(BaseModel):
    id: int = Field(examples=[1])
    name: str = Field(examples=["pikachu"])
    type: str = Field(examples=["electric"])
    height: int | None = Field(default=None, examples=[4])
    weight: int | None = Field(default=None, examples=[60])
    model_config = ConfigDict(from_attributes=True)


class Pagination(BaseModel):
    total: int
    limit: int
    offset: int


class PokemonList(BaseModel):
    data: list[PokemonOut]
    pagination: Pagination


class ErrorResponse(BaseModel):
    detail: str