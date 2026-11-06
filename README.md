# Pokémon API

API REST para gerenciar pokémons (CRUD completo), construída com **FastAPI** e **SQLAlchemy**.

## Tecnologias

- Python 3
- FastAPI (framework e documentação Swagger automática)
- SQLAlchemy (ORM)
- Pydantic (validação de dados)
- SQLite (padrão local) / PostgreSQL (via `DATABASE_URL`)

## Estrutura do projeto

```
pokemon-api/
├── app/
│   ├── __init__.py
│   ├── database.py    # conexão com o banco
│   ├── models.py      # tabela Pokemon (SQLAlchemy)
│   ├── schemas.py     # validação de entrada e saída (Pydantic)
│   └── main.py        # endpoints da API
├── tests/
│   └── __init__.py
├── requirements.txt
└── .gitignore
```

## Como rodar localmente

1. Criar e ativar o ambiente virtual (Windows):

```bash
py -m venv .venv
.venv\Scripts\activate
```

2. Instalar as dependências:

```bash
pip install -r requirements.txt
```

3. Iniciar a API:

```bash
uvicorn app.main:app --reload
```

4. Acessar:

- API: http://localhost:8000
- Documentação (Swagger): http://localhost:8000/docs

Por padrão a API usa um banco SQLite local (`pokemon.db`). Para usar outro banco, defina a variável de ambiente `DATABASE_URL`.

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| POST | `/pokemons` | Criar pokémon |
| GET | `/pokemons?limit=20&offset=0&name=` | Listar (paginado) e buscar por nome |
| GET | `/pokemons/{id}` | Buscar pokémon por id |
| PUT | `/pokemons/{id}` | Atualizar pokémon |
| DELETE | `/pokemons/{id}` | Excluir pokémon |

## Exemplo de uso

**Requisição:** `POST /pokemons`

```json
{
  "name": "pikachu",
  "type": "electric",
  "height": 4,
  "weight": 60
}
```

**Resposta (201):**

```json
{
  "id": 1,
  "name": "pikachu",
  "type": "electric",
  "height": 4,
  "weight": 60
}
```

**Requisição:** `GET /pokemons?limit=20&offset=0`

**Resposta (200):**

```json
{
  "data": [
    { "id": 1, "name": "pikachu", "type": "electric", "height": 4, "weight": 60 }
  ],
  "pagination": {
    "total": 1,
    "limit": 20,
    "offset": 0
  }
}
```

## Erros

- `404`: pokémon não encontrado
- `400`: pokémon com nome já existente
- `422`: dados inválidos

## Em desenvolvimento

- [ ] Testes unitários (pytest)
- [ ] Docker e docker-compose com PostgreSQL
- [ ] Variáveis de ambiente (`.env.example`)