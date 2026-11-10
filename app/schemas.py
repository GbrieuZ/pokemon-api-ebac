from pydantic import BaseModel, ConfigDict, Field, model_validator


class PokemonCreate(BaseModel):
    name: str = Field(examples=["pikachu"])
    type: str = Field(examples=["electric"])
    height: int | None = Field(default=None, examples=[4])
    weight: int | None = Field(default=None, examples=[60])


class PokemonUpdate(BaseModel):
    name: str | None = Field(default=None, examples=["raichu"])
    type: str | None = Field(default=None, examples=["electric"])
    height: int | None = Field(default=None, examples=[8])
    weight: int | None = Field(default=None, examples=[300])

    @model_validator(mode="after")
    def name_e_type_nao_podem_ser_nulos(self):
        for campo in ("name", "type"):
            if campo in self.model_fields_set and getattr(self, campo) is None:
                raise ValueError(f"'{campo}' não pode ser nulo")
        return self

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

class ErrorResponse(BaseModel):
    detail: str