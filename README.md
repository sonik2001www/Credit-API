# Credit API (FastAPI + MySQL)

Async FastAPI service with clean layering, API key auth, and Docker compose for MySQL.

## Stack
- Python 3.11
- FastAPI + Pydantic v2
- SQLAlchemy 2 async + asyncmy
- MySQL 8
- Docker / docker-compose

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # or set DATABASE_URL and API_KEY
uvicorn src.main:app --reload
```

## Run with Docker
```bash
docker-compose up --build
```
- Apply migrations (in running container):
```bash
docker-compose exec api alembic upgrade head
```
- (Optional) Seed demo data (drops/recreates tables):
```bash
docker-compose exec api python -m scripts.seed_from_csv
```

## Seeding sample data
```bash
python -m scripts.seed_from_csv
```

## Migrations (Alembic)
- Create a migration (autogenerate):
```bash
alembic revision --autogenerate -m "init"
```
- Apply migrations:
```bash
alembic upgrade head
```
- Alembic reads `DATABASE_URL` from `.env` (configured in `migrations/env.py`).

## Auth
Send header `X-API-Key: <value>` matching `API_KEY` env (default `dev-api-key`).

## Endpoints (under /api/v1)
- `GET /user_credits/{user_id}`
- `POST /plans/insert` (multipart/form-data with file)
- `GET /plans/performance?report_date=YYYY-MM-DD`
- `GET /plans/year_performance?year=YYYY`

## Project layout
- `src/main.py` - FastAPI app wiring
- `src/api` - Routers
- `src/services` - Business logic
- `src/models` - SQLAlchemy models
- `src/schemas` - Pydantic schemas
- `src/core` - settings, db, security
- `scripts/seed_from_csv.py` - recreate DB and load CSV samples

## Notes
- Uses async SQLAlchemy sessions and dependency injection.
- Basic API key auth; swap with JWT easily.
- Keep logic in services, not routers.
