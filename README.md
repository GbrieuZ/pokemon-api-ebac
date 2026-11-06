# Pokémon API

API REST para gerenciar pokémons (CRUD completo), construída com **FastAPI**, **SQLAlchemy** e **PostgreSQL**, e containerizada com **Docker**.

## Tecnologias

- Python 3.12
- FastAPI (framework e documentação Swagger automática)
- SQLAlchemy (ORM)
- Pydantic (validação de dados)
- PostgreSQL (via Docker) / SQLite (testes e uso local sem Docker)
- Pytest (testes unitários)
- Docker e docker-compose

## Estrutura do projeto

```
projetoFinal/
├── app/
│   ├── __init__.py
│   ├── database.py    # conexão com o banco (lê DATABASE_URL)
│   ├── models.py      # tabela Pokemon (SQLAlchemy)
│   ├── schemas.py     # validação de entrada e saída (Pydantic)
│   └── main.py        # endpoints da API
├── tests/
│   ├── __init__.py
│   └── test_pokemons.py
├── .env.example       # modelo das variáveis de ambiente
├── .gitignore
├── docker-compose.yml # API + PostgreSQL
├── Dockerfile
├── README.md
└── requirements.txt
```

## Variáveis de ambiente

As credenciais ficam fora do código, em um arquivo `.env` (que não é versionado). Use o `.env.example` como modelo:

```
POSTGRES_USER=pokemon
POSTGRES_PASSWORD=pokemon
POSTGRES_DB=pokemon
DATABASE_URL=postgresql+psycopg2://pokemon:pokemon@db:5432/pokemon
```

Crie o seu `.env` a partir do modelo:

```bash
# Windows (cmd)
copy .env.example .env

# Linux / Mac
cp .env.example .env
```

## Como rodar com Docker (recomendado)

Pré-requisito: Docker Desktop aberto.

```bash
copy .env.example .env
docker compose up --build
```

Serão iniciados dois containers separados: a API (FastAPI) e o banco (PostgreSQL). Os dados ficam guardados no volume `pgdata`.

- API: http://localhost:8000
- Documentação (Swagger): http://localhost:8000/docs

Para parar:

```bash
docker compose down
```

## Como rodar localmente (sem Docker)

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

Sem a variável `DATABASE_URL` definida, a API usa um banco SQLite local (`pokemon.db`).

## Como executar os testes

```bash
pip install -r requirements.txt
pytest
```

Os testes usam um SQLite em memória, portanto não precisam de Docker nem alteram o banco real. Cobrem os 5 endpoints, a paginação e os erros (400 e 404).

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

- [ ] Revisão final contra o enunciado (Parte 6)