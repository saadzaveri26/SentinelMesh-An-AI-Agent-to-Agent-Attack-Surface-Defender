# SentinelMesh — Tech Stack

All choices below are confirmed. Do not substitute without asking.

| Layer | Technology |
|---|---|
| Messaging | Apache Kafka (Docker) |
| Backend | FastAPI (Python) |
| Detection | Fine-tuned BERT (Hugging Face Transformers) |
| Database | PostgreSQL + SQLAlchemy |
| Frontend | Next.js + React Flow |
| Infra | Docker Compose (local) |

## Key libraries (Python backend)
- `fastapi` + `uvicorn`
- `kafka-python` (or `confluent-kafka` — confirm on install)
- `sqlalchemy` + `alembic`
- `transformers` + `torch`
- `pydantic`

## Key libraries (Frontend)
- `next`
- `reactflow`

## Environment
- Secrets via `.env` (must be in `.gitignore`)
- All services orchestrated via a single `docker-compose.yml`
