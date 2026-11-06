from sqlalchemy import Column, Integer, String
from app.database import Base


class Pokemon(Base):
    __tablename__ = "pokemons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)
    height = Column(Integer)
    weight = Column(Integer)