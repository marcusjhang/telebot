# Telegram Water/Carb/Exercise Tracker - Backend

FastAPI backend with integrated Telegram bot for tracking daily water, carbs, and exercise.

## Setup

### Prerequisites
- Python 3.11+
- Poetry
- PostgreSQL (or use Supabase)
- Redis

### Installation

1. Install dependencies:
```bash
cd backend
poetry install
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Edit `.env` with your credentials:
   - Get `TELEGRAM_BOT_TOKEN` from @BotFather
   - Set `DATABASE_URL` to your PostgreSQL connection string
   - Set `REDIS_URL` to your Redis connection string
   - Generate `JWT_SECRET_KEY` (min 32 characters)

4. Start local services (PostgreSQL + Redis):
```bash
cd ..
docker-compose up -d
```

5. Run database migrations:
```bash
poetry run alembic upgrade head
```

6. Start the development server:
```bash
poetry run uvicorn app.main:app --reload
```

7. In a separate terminal, start the RQ worker:
```bash
poetry run rq worker --url redis://localhost:6379/0 broadcasts
```

## Development

### Create a new migration:
```bash
poetry run alembic revision --autogenerate -m "description"
```

### Run tests:
```bash
poetry run pytest
```

### Format code:
```bash
poetry run black .
poetry run ruff check . --fix
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app + Bot integration
│   ├── config.py            # Settings
│   ├── database.py          # Database setup
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API routes
│   ├── bot/                 # Bot handlers
│   ├── services/            # Business logic
│   ├── workers/             # Background workers
│   ├── scheduler/           # Scheduled jobs
│   └── utils/               # Utilities
├── tests/                   # Tests
├── alembic/                 # Database migrations
└── pyproject.toml           # Dependencies
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

