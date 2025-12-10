# Telegram Water/Carb/Exercise Tracker - Comprehensive Implementation Plan

## Project Overview
A Telegram bot for tracking daily water intake, carb consumption, and weekly exercise with a companion web app for analytics and goal management.

**Key Change from Original Plan:**
- ✅ **No timezone selection** - All users default to Singapore Time (Asia/Singapore, UTC+8)

---

## Technology Stack (Research-Based Recommendations)

### Backend & Bot
- **Language:** Python 3.11+
- **Bot Framework:** `pyTelegramBotAPI` (telebot) - Simple, well-documented, production-ready
- **API Framework:** FastAPI - Modern, async, auto-documentation with OpenAPI
- **Database:** Supabase (PostgreSQL) - Managed Postgres with built-in auth, REST API, real-time subscriptions
- **ORM:** SQLAlchemy 2.0 with async support
- **Scheduler:** APScheduler 3.x - Timezone-aware cron jobs for daily/weekly resets
- **Task Queue:** Redis + RQ (Redis Queue) - Lightweight for broadcast notifications

### Frontend
- **Framework:** Next.js 14+ (App Router) with React
- **UI Library:** shadcn/ui + Tailwind CSS
- **Auth:** Telegram Login Widget → JWT tokens
- **Charts:** Recharts or Chart.js
- **State Management:** React Context + SWR for data fetching

### Deployment (2025 Best Practices)
**Research Findings:**
- ❌ PythonAnywhere: Limited async support, not ideal for webhooks
- ❌ Heroku: Free tier discontinued
- ✅ **Railway.app** (RECOMMENDED): 
  - $5/month starter plan with generous limits
  - Native GitHub integration
  - Built-in PostgreSQL (or use Supabase)
  - Easy environment variables
  - Automatic HTTPS
  - Perfect for webhook-based bots
- Alternative: Render.com (similar features, slightly different pricing)

**Deployment Architecture:**
- **Bot + API:** Railway (single Python service)
- **Database:** Supabase (free tier: 500MB, 2GB bandwidth)
- **Web App:** Vercel (free tier, auto-deploy from GitHub)
- **Redis:** Railway Redis addon or Upstash (serverless Redis)

### Development Tools
- **Environment:** Poetry for dependency management
- **Linting:** Ruff (fast Python linter)
- **Formatting:** Black
- **Type Checking:** mypy
- **Testing:** pytest + pytest-asyncio
- **API Testing:** httpx (async HTTP client)

---

## Phase 1: Project Setup & Infrastructure

### 1.1 Initialize Project Structure

**IMPORTANT ARCHITECTURAL NOTE:**
The bot and API are integrated into a **single FastAPI application**. The bot handlers are registered within the FastAPI app, and webhook requests are processed through a FastAPI endpoint. This is the recommended approach for webhook-based bots.

```
telebot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app + Bot webhook integration
│   │   ├── config.py            # Settings (Pydantic BaseSettings)
│   │   ├── database.py          # SQLAlchemy async setup
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── goal.py
│   │   │   ├── log.py
│   │   │   └── event.py
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── goal.py
│   │   │   └── log.py
│   │   ├── api/                 # API routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # Telegram auth endpoint
│   │   │   ├── users.py
│   │   │   ├── goals.py
│   │   │   ├── logs.py
│   │   │   └── progress.py
│   │   ├── bot/                 # Bot handlers (no separate main.py)
│   │   │   ├── __init__.py
│   │   │   ├── handlers.py      # Command & callback handlers
│   │   │   ├── keyboards.py     # Inline keyboard builders
│   │   │   └── middleware.py    # Rate limiting, logging
│   │   ├── services/            # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── user_service.py
│   │   │   ├── goal_service.py
│   │   │   ├── log_service.py
│   │   │   └── progress_service.py
│   │   ├── workers/             # Background workers
│   │   │   ├── __init__.py
│   │   │   └── broadcast.py     # RQ worker for broadcasts
│   │   ├── scheduler/
│   │   │   ├── __init__.py
│   │   │   └── jobs.py          # Daily/weekly reset jobs
│   │   └── utils/               # Helpers
│   │       ├── __init__.py
│   │       ├── auth.py          # JWT utilities
│   │       └── date_helpers.py  # Week calculation
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   ├── test_bot.py
│   │   └── test_services.py
│   ├── alembic/                 # Database migrations
│   │   ├── env.py
│   │   └── versions/
│   ├── pyproject.toml           # Poetry dependencies
│   ├── poetry.lock
│   ├── alembic.ini
│   ├── .env.example
│   └── README.md
├── frontend/
│   ├── app/                     # Next.js app directory
│   │   ├── page.tsx
│   │   ├── dashboard/
│   │   └── layout.tsx
│   ├── components/
│   │   ├── ui/                  # shadcn components
│   │   ├── LoginButton.tsx
│   │   └── ProgressChart.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   └── utils.ts
│   ├── package.json
│   └── next.config.js
├── docker-compose.yml           # Local development (Redis, PostgreSQL)
├── railway.toml                 # Railway deployment config
└── README.md
```

### 1.2 Initialize Poetry & Dependencies

**Create `pyproject.toml`:**

```toml
[tool.poetry]
name = "telebot-tracker"
version = "0.1.0"
description = "Telegram bot for tracking water, carbs, and exercise"
authors = ["Your Name <you@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.109.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
pyTelegramBotAPI = "^4.16.0"
sqlalchemy = {extras = ["asyncio"], version = "^2.0.25"}
asyncpg = "^0.29.0"
alembic = "^1.13.0"
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.6"
redis = "^5.0.1"
rq = "^1.15.1"
apscheduler = "^3.10.4"
pytz = "^2024.1"
httpx = "^0.26.0"
slowapi = "^0.1.9"
sentry-sdk = {extras = ["fastapi"], version = "^1.40.0"}

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
black = "^24.0.0"
ruff = "^0.1.0"
mypy = "^1.8.0"
httpx = "^0.26.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
```

**Install dependencies:**
```bash
cd backend
poetry install
```

### 1.3 Set Up Supabase
1. Create Supabase project at https://supabase.com
2. Note down:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - Direct PostgreSQL connection string (use this for `DATABASE_URL`)
3. Enable Row Level Security (RLS) - disable for bot service role

### 1.3 Create Telegram Bot
1. Message @BotFather on Telegram
2. `/newbot` → name: "Water Tracker Bot"
3. Save `BOT_TOKEN`
4. Configure bot:
   ```
   /setdescription - Track water, carbs, and exercise daily
   /setcommands
   start - Start tracking
   progress - View your progress
   settings - Configure goals
   help - Get help
   ```

### 1.4 Environment Variables & Configuration

Create `.env` file with the following variables:

```bash
# .env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_WEBHOOK_URL=https://your-app.railway.app
TELEGRAM_WEBHOOK_SECRET=generate_random_string_32_chars  # For webhook verification

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=your_service_key

# Redis
REDIS_URL=redis://localhost:6379/0

# API
API_SECRET_KEY=generate_with_openssl_rand_hex_32
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=43200  # 30 days

# App Config
ENVIRONMENT=development  # development | production
DEFAULT_TIMEZONE=Asia/Singapore
LOG_LEVEL=INFO
WEB_APP_URL=http://localhost:3000  # Frontend URL for CORS
```

**Create `app/config.py` with Pydantic Settings:**

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: str
    TELEGRAM_WEBHOOK_SECRET: str

    # Database
    DATABASE_URL: str
    SUPABASE_URL: str | None = None
    SUPABASE_SERVICE_KEY: str | None = None

    # Redis
    REDIS_URL: str
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    # API
    API_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 43200

    # App
    ENVIRONMENT: str = "development"
    DEFAULT_TIMEZONE: str = "Asia/Singapore"
    LOG_LEVEL: str = "INFO"
    WEB_APP_URL: str

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
```

---

## Phase 2: Database Schema & Models

### 2.1 Database Tables (PostgreSQL)

#### Table: `users`
Stores user profile and preferences.
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_user_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    timezone VARCHAR(50) DEFAULT 'Asia/Singapore' NOT NULL,
    broadcast_opt_out BOOLEAN DEFAULT FALSE,
    recap_enabled BOOLEAN DEFAULT TRUE,
    week_start_day INTEGER DEFAULT 1,  -- 0=Sunday, 1=Monday
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_telegram_id ON users(telegram_user_id);
CREATE INDEX idx_users_active ON users(is_active, last_active);
```

#### Table: `goals`
Tracks user goals with effective dates (allows goal changes over time).
```sql
CREATE TABLE goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    daily_water_bottles DECIMAL(4,1) DEFAULT 3.0 NOT NULL CHECK (daily_water_bottles > 0),
    daily_carb_max_portions DECIMAL(4,1) DEFAULT 4.0 NOT NULL CHECK (daily_carb_max_portions > 0),
    weekly_exercise_sessions INTEGER DEFAULT 6 NOT NULL CHECK (weekly_exercise_sessions > 0),
    effective_from DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, effective_from)
);

CREATE INDEX idx_goals_user_effective ON goals(user_id, effective_from DESC);
```

#### Table: `daily_logs`
Aggregated daily totals for water, carbs, and exercise.
```sql
CREATE TABLE daily_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    log_date DATE NOT NULL,  -- In user's timezone (always Singapore)
    water_bottles DECIMAL(5,1) DEFAULT 0 NOT NULL CHECK (water_bottles >= 0),
    carb_portions DECIMAL(5,1) DEFAULT 0 NOT NULL CHECK (carb_portions >= 0),
    exercise_sessions INTEGER DEFAULT 0 NOT NULL CHECK (exercise_sessions >= 0),  -- Daily exercise count
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, log_date)
);

CREATE INDEX idx_daily_logs_user_date ON daily_logs(user_id, log_date DESC);
```

**Note:** Exercise is tracked both in `daily_logs` (for daily view) and `weekly_logs` (for weekly aggregation and goal tracking).

#### Table: `weekly_logs`
Aggregated weekly exercise totals.
```sql
CREATE TABLE weekly_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    week_start_date DATE NOT NULL,  -- Monday of the week
    exercise_sessions INTEGER DEFAULT 0 NOT NULL CHECK (exercise_sessions >= 0),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, week_start_date)
);

CREATE INDEX idx_weekly_logs_user_week ON weekly_logs(user_id, week_start_date DESC);
```

#### Table: `events`
Detailed event log for audit trail and analytics.
```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(20) NOT NULL,  -- 'water', 'carb', 'exercise'
    delta DECIMAL(5,1) NOT NULL,  -- Can be negative for decreases
    subtype VARCHAR(20),  -- 'meal', 'snack', 'custom' for carbs
    portions DECIMAL(5,1),  -- Calculated portions for carbs
    occurred_at TIMESTAMPTZ DEFAULT NOW(),
    message_id BIGINT,  -- Telegram message ID for idempotency
    callback_query_id VARCHAR(255),  -- For deduplication
    source VARCHAR(20) DEFAULT 'bot',  -- 'bot' or 'web'
    metadata JSONB  -- Extra data (e.g., quick button used)
);

CREATE INDEX idx_events_user_time ON events(user_id, occurred_at DESC);
CREATE INDEX idx_events_callback ON events(callback_query_id) WHERE callback_query_id IS NOT NULL;
```

#### Table: `notifications`
Queue for broadcast notifications.
```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    notification_type VARCHAR(50) NOT NULL,  -- 'broadcast', 'recap', 'weekly_recap'
    payload JSONB NOT NULL,
    target_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,  -- NULL for broadcast
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'sent', 'failed'
    scheduled_for TIMESTAMPTZ,
    sent_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notifications_status ON notifications(status, scheduled_for);
CREATE INDEX idx_notifications_user ON notifications(target_user_id, created_at DESC);
```

#### Table: `monthly_stats` (Materialized View)
Pre-computed monthly statistics for faster dashboard loading.
```sql
CREATE MATERIALIZED VIEW monthly_stats AS
SELECT
    user_id,
    DATE_TRUNC('month', log_date) AS month,
    COUNT(*) AS total_days,
    SUM(CASE WHEN water_bottles >= (
        SELECT daily_water_bottles FROM goals g
        WHERE g.user_id = dl.user_id AND g.effective_from <= dl.log_date
        ORDER BY g.effective_from DESC LIMIT 1
    ) THEN 1 ELSE 0 END) AS days_water_goal_met,
    SUM(CASE WHEN carb_portions <= (
        SELECT daily_carb_max_portions FROM goals g
        WHERE g.user_id = dl.user_id AND g.effective_from <= dl.log_date
        ORDER BY g.effective_from DESC LIMIT 1
    ) THEN 1 ELSE 0 END) AS days_carb_goal_met,
    AVG(water_bottles) AS avg_water_bottles,
    AVG(carb_portions) AS avg_carb_portions,
    MAX(water_bottles) AS max_water_bottles,
    MAX(carb_portions) AS max_carb_portions
FROM daily_logs dl
GROUP BY user_id, DATE_TRUNC('month', log_date);

-- IMPORTANT: Remove DESC from unique index to allow CONCURRENT refresh
CREATE UNIQUE INDEX idx_monthly_stats_user_month ON monthly_stats(user_id, month);

-- Add separate index for ordering
CREATE INDEX idx_monthly_stats_month_desc ON monthly_stats(user_id, month DESC);
```

**Note:** The unique index cannot have DESC when using `REFRESH MATERIALIZED VIEW CONCURRENTLY`.

### 2.2 SQLAlchemy Models

Create `app/database.py` first:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Create async engine with connection pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.LOG_LEVEL == "DEBUG",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

# Dependency for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

Create models in `backend/app/models/`:
- `user.py` - User model
- `goal.py` - Goal model
- `daily_log.py` - DailyLog model
- `weekly_log.py` - WeeklyLog model
- `event.py` - Event model
- `notification.py` - Notification model

### 2.3 Alembic Configuration & Migrations

**Create `alembic.ini`:**
```ini
[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = driver://user:pass@localhost/dbname

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

**Update `alembic/env.py`:**
```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.config import settings
from app.database import Base
from app.models import *  # Import all models

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace('+asyncpg', ''))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
```

**Run migrations:**
```bash
# Initialize Alembic (if not done)
cd backend
poetry run alembic init alembic

# Create initial migration
poetry run alembic revision --autogenerate -m "Initial schema"

# Apply migration
poetry run alembic upgrade head
```

---

## Phase 3: Backend API Development

### 3.1 FastAPI Application Structure

#### Core Endpoints

**Base URL:** `https://your-app.railway.app/api/v1`

#### 3.1.0 Authentication

**POST /auth/telegram**
- **Purpose:** Authenticate user via Telegram Login Widget
- **Auth:** None (public endpoint)
- **Request Body:**
```json
{
  "id": 123456789,
  "first_name": "John",
  "last_name": "Doe",
  "username": "john_doe",
  "photo_url": "https://...",
  "auth_date": 1702123456,
  "hash": "abc123..."
}
```
- **Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "telegram_user_id": 123456789,
    "username": "john_doe",
    "first_name": "John"
  }
}
```
- **Business Logic:**
  1. Verify Telegram hash using bot token
  2. Check auth_date is within last 24 hours
  3. Create or update user in database
  4. Generate JWT token
  5. Return token and user data

**Implementation:**
```python
import hmac
import hashlib
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from app.schemas.auth import TelegramAuthData
from app.services.user_service import create_or_update_user
from app.utils.auth import create_jwt_token
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/telegram")
async def telegram_auth(data: TelegramAuthData):
    # 1. Verify hash
    check_data = {k: v for k, v in data.dict().items() if k != "hash" and v is not None}
    check_string = "\n".join([f"{k}={v}" for k, v in sorted(check_data.items())])
    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    calculated_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()

    if calculated_hash != data.hash:
        raise HTTPException(status_code=401, detail="Invalid authentication data")

    # 2. Check auth_date (within 24 hours)
    if datetime.now().timestamp() - data.auth_date > 86400:
        raise HTTPException(status_code=401, detail="Authentication data expired")

    # 3. Create or update user
    user = await create_or_update_user(
        telegram_user_id=data.id,
        username=data.username,
        first_name=data.first_name,
        last_name=data.last_name
    )

    # 4. Generate JWT
    token = create_jwt_token(user.telegram_user_id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "telegram_user_id": user.telegram_user_id,
            "username": user.username,
            "first_name": user.first_name
        }
    }
```

**Create `app/utils/auth.py`:**
```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.config import settings

def create_jwt_token(telegram_user_id: int) -> str:
    """Generate JWT token for user"""
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(telegram_user_id),
        "exp": expire
    }
    return jwt.encode(to_encode, settings.API_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def verify_jwt_token(token: str) -> int:
    """Verify JWT and return telegram_user_id"""
    try:
        payload = jwt.decode(token, settings.API_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        telegram_user_id: int = int(payload.get("sub"))
        if telegram_user_id is None:
            raise JWTError("Invalid token")
        return telegram_user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
```

#### 3.1.1 User Management

**POST /api/v1/users**
- **Purpose:** Create or update user (idempotent)
- **Auth:** Bot token or user JWT
- **Request Body:**
```json
{
  "telegram_user_id": 123456789,
  "username": "john_doe",
  "first_name": "John",
  "last_name": "Doe"
}
```
- **Response:** `201 Created` or `200 OK`
```json
{
  "id": 1,
  "telegram_user_id": 123456789,
  "username": "john_doe",
  "timezone": "Asia/Singapore",
  "created_at": "2025-12-10T10:00:00Z"
}
```
- **Business Logic:**
  - Upsert user by `telegram_user_id`
  - Set `timezone` to `Asia/Singapore` (hardcoded)
  - **Create default goals if new user:**
    ```python
    # In user_service.py
    async def create_or_update_user(telegram_user_id: int, username: str, first_name: str, last_name: str = None):
        # Upsert user
        user = await upsert_user(...)

        # Check if user has goals
        existing_goal = await get_active_goal(user.id, date.today())
        if not existing_goal:
            # Create default goals
            await create_goal(
                user_id=user.id,
                daily_water_bottles=3.0,
                daily_carb_max_portions=4.0,
                weekly_exercise_sessions=6,
                effective_from=date.today()
            )

        return user
    ```
  - Update `last_active` timestamp

**GET /api/v1/users/me**
- **Purpose:** Get current user profile
- **Auth:** User JWT
- **Response:** User object with current goals

**PATCH /api/v1/users/me**
- **Purpose:** Update user preferences
- **Request Body:**
```json
{
  "broadcast_opt_out": true,
  "recap_enabled": false,
  "week_start_day": 1
}
```

**GET /api/v1/users/broadcast-recipients**
- **Purpose:** Get all users who haven't opted out of broadcasts (for bot use)
- **Auth:** Bot token (internal use only)
- **Query Params:** `?exclude_user_id=123` (optional - exclude the user who triggered the event)
- **Response:**
```json
[
  {
    "telegram_user_id": 123456789,
    "first_name": "John",
    "username": "john_doe"
  },
  {
    "telegram_user_id": 987654321,
    "first_name": "Jane"
  }
]
```
- **Implementation:**
```python
@router.get("/users/broadcast-recipients")
async def get_broadcast_recipients(
    exclude_user_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all users who haven't opted out of broadcasts"""
    query = select(User).where(
        User.is_active == True,
        User.broadcast_opt_out == False
    )

    if exclude_user_id:
        query = query.where(User.telegram_user_id != exclude_user_id)

    result = await db.execute(query)
    users = result.scalars().all()

    return [
        {
            "telegram_user_id": u.telegram_user_id,
            "first_name": u.first_name,
            "username": u.username
        }
        for u in users
    ]
```

#### 3.1.2 Goals Management

**GET /api/v1/goals**
- **Purpose:** Get current active goals
- **Auth:** User JWT
- **Query Params:** `?effective_date=2025-12-10` (optional)
- **Response:**
```json
{
  "id": 5,
  "user_id": 1,
  "daily_water_bottles": 3.0,
  "daily_carb_max_portions": 4.0,
  "weekly_exercise_sessions": 6,
  "effective_from": "2025-12-01",
  "created_at": "2025-12-01T00:00:00Z"
}
```
- **Business Logic:**
  - Return latest goal where `effective_from <= query_date`
  - Default to today if no date specified

**POST /api/v1/goals**
- **Purpose:** Create new goal (effective from specified date)
- **Auth:** User JWT
- **Request Body:**
```json
{
  "daily_water_bottles": 4.0,
  "daily_carb_max_portions": 3.5,
  "weekly_exercise_sessions": 5,
  "effective_from": "2025-12-15"  // Optional, defaults to today
}
```
- **Validation:**
  - All values must be > 0
  - `effective_from` cannot be in the past (except today)
  - Max limits: water ≤ 20, carbs ≤ 20, exercise ≤ 30
- **Response:** `201 Created` with goal object

**GET /api/v1/goals/history**
- **Purpose:** Get all historical goals
- **Response:** Array of goals ordered by `effective_from DESC`

#### 3.1.3 Logging Activities

**POST /api/v1/logs/water**
- **Purpose:** Add/decrease water intake
- **Auth:** User JWT or Bot token
- **Headers:** `Idempotency-Key: <callback_query_id>` (optional)
- **Request Body:**
```json
{
  "delta": 1.0,  // Can be negative
  "message_id": 12345,  // Telegram message ID
  "source": "bot"  // or "web"
}
```
- **Response:** `200 OK`
```json
{
  "success": true,
  "new_total": 2.0,
  "goal": 3.0,
  "remaining": 1.0,
  "date": "2025-12-10"
}
```
- **Business Logic:**
  1. Check idempotency key - return cached response if duplicate
  2. Get or create today's `daily_log`
  3. Calculate new total: `current + delta`
  4. Clamp to 0 if negative (cannot go below 0)
  5. Update `daily_log.water_bottles`
  6. Insert event record
  7. Queue broadcast notification
  8. Cache response with idempotency key (15 min TTL)

**POST /api/v1/logs/carbs**
- **Purpose:** Add/decrease carb intake
- **Request Body:**
```json
{
  "delta": 2.0,  // In portions
  "subtype": "meal",  // "meal", "snack", or "custom"
  "message_id": 12345,
  "source": "bot"
}
```
- **Response:** Similar to water endpoint
```json
{
  "success": true,
  "new_total": 3.5,
  "goal": 4.0,
  "remaining": 0.5,
  "over_limit": false,
  "date": "2025-12-10"
}
```
- **Business Logic:**
  - Same as water, but update `daily_log.carb_portions`
  - Store `subtype` and `portions` in event
  - Set `over_limit: true` if `new_total > goal`

**POST /api/v1/logs/exercise**
- **Purpose:** Add/decrease exercise sessions
- **Request Body:**
```json
{
  "delta": 1,  // Integer sessions
  "message_id": 12345,
  "source": "bot"
}
```
- **Response:**
```json
{
  "success": true,
  "new_total": 4,
  "weekly_goal": 6,
  "remaining": 2,
  "week_start": "2025-12-09",
  "date": "2025-12-10"
}
```
- **Business Logic:**
  1. Calculate current week start (Monday) using helper function
  2. Get or create `weekly_log` for this week
  3. Update `weekly_log.exercise_sessions`
  4. Also update today's `daily_log.exercise_sessions` (for daily summary)
  5. Clamp to 0 minimum

**Week Calculation Helper:**

Create `app/utils/date_helpers.py`:

```python
from datetime import date, timedelta

def get_week_bounds(target_date: date, week_start_day: int = 1) -> tuple[date, date]:
    """
    Get week start and end dates for a given date.

    Args:
        target_date: The date to find the week for
        week_start_day: 0=Sunday, 1=Monday (default)

    Returns:
        Tuple of (week_start, week_end)
    """
    # Calculate days since the week start day
    days_since_start = (target_date.weekday() - week_start_day) % 7
    week_start = target_date - timedelta(days=days_since_start)
    week_end = week_start + timedelta(days=6)

    return week_start, week_end

# Usage in exercise logging:
# week_start, week_end = get_week_bounds(date.today(), user.week_start_day)
```

#### 3.1.4 Progress & Analytics

**GET /api/v1/progress/today**
- **Purpose:** Get today's progress summary
- **Auth:** User JWT
- **Response:**
```json
{
  "date": "2025-12-10",
  "water": {
    "current": 2.0,
    "goal": 3.0,
    "remaining": 1.0,
    "percentage": 66.7,
    "goal_met": false
  },
  "carbs": {
    "current": 3.5,
    "goal": 4.0,
    "remaining": 0.5,
    "percentage": 87.5,
    "over_limit": false
  },
  "exercise": {
    "today": 1,
    "weekly_total": 4,
    "weekly_goal": 6,
    "remaining": 2,
    "percentage": 66.7
  },
  "streaks": {
    "water_days": 5,
    "carb_days": 3,
    "combined_days": 2
  }
}
```

**Streak Calculation Implementation:**

Create `app/services/progress_service.py`:

```python
from datetime import date, timedelta
from sqlalchemy import select
from app.models import DailyLog, Goal
from app.database import AsyncSession

async def calculate_streaks(user_id: int, db: AsyncSession) -> dict:
    """Calculate consecutive days meeting goals"""
    # Get last 30 days of logs
    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    query = select(DailyLog).where(
        DailyLog.user_id == user_id,
        DailyLog.log_date >= start_date,
        DailyLog.log_date <= end_date
    ).order_by(DailyLog.log_date.desc())

    result = await db.execute(query)
    logs = result.scalars().all()

    water_streak = 0
    carb_streak = 0
    combined_streak = 0

    for log in logs:  # Already ordered desc (today first)
        # Get goal for this date
        goal_query = select(Goal).where(
            Goal.user_id == user_id,
            Goal.effective_from <= log.log_date
        ).order_by(Goal.effective_from.desc()).limit(1)

        goal_result = await db.execute(goal_query)
        goal = goal_result.scalar_one_or_none()

        if not goal:
            break

        water_met = log.water_bottles >= goal.daily_water_bottles
        carb_met = log.carb_portions <= goal.daily_carb_max_portions

        # Water streak
        if water_met and water_streak == (end_date - log.log_date).days:
            water_streak += 1

        # Carb streak
        if carb_met and carb_streak == (end_date - log.log_date).days:
            carb_streak += 1

        # Combined streak (both met)
        if water_met and carb_met and combined_streak == (end_date - log.log_date).days:
            combined_streak += 1

    return {
        "water_days": water_streak,
        "carb_days": carb_streak,
        "combined_days": combined_streak
    }
```

**GET /api/v1/progress/week**
- **Purpose:** Get past 7 days summary
- **Response:**
```json
{
  "days": [
    {
      "date": "2025-12-10",
      "water_met": true,
      "carb_met": true,
      "water_bottles": 3.0,
      "carb_portions": 3.5
    },
    // ... 6 more days
  ],
  "weekly_exercise": {
    "total": 4,
    "goal": 6,
    "goal_met": false
  }
}
```

**GET /api/v1/progress/month**
- **Purpose:** Get monthly statistics
- **Query Params:** `?year=2025&month=12`
- **Response:**
```json
{
  "month": "2025-12",
  "total_days": 10,
  "days_water_goal_met": 8,
  "days_carb_goal_met": 7,
  "avg_water_bottles": 2.8,
  "avg_carb_portions": 3.2,
  "max_water_bottles": 4.0,
  "max_carb_portions": 5.5,
  "weekly_exercise_completion": [
    {"week_start": "2025-12-02", "sessions": 6, "goal_met": true},
    {"week_start": "2025-12-09", "sessions": 4, "goal_met": false}
  ]
}
```
- **Business Logic:**
  - Query `monthly_stats` materialized view
  - Fallback to real-time calculation if view not refreshed

**GET /api/v1/progress/export**
- **Purpose:** Export all user data as CSV
- **Response:** CSV file with all events

#### 3.1.5 Notifications

**POST /api/v1/notifications/broadcast** (Internal use only)
- **Purpose:** Queue broadcast notification
- **Auth:** Service token
- **Request Body:**
```json
{
  "user_id": 1,
  "event_type": "water",
  "delta": 1.0,
  "new_total": 2.0
}
```
- **Business Logic:**
  1. Get all active users where `broadcast_opt_out = false`
  2. Create notification records
  3. Return immediately (processed by worker)

#### 3.1.6 Webhook

**POST /webhook**
- **Purpose:** Receive Telegram updates
- **Auth:** Verify Telegram secret token
- **Request Body:** Telegram Update object
- **Response:** `200 OK` (always, even on errors)
- **Business Logic:**
  - Validate `X-Telegram-Bot-Api-Secret-Token` header
  - Pass to bot handler
  - Handle in background (non-blocking)

**Implementation:**
```python
from fastapi import Request, HTTPException
from telebot import types

@app.post("/webhook")
async def webhook(request: Request):
    # Verify X-Telegram-Bot-Api-Secret-Token header
    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret_token != settings.TELEGRAM_WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret token")

    # Parse update
    update_dict = await request.json()
    update = types.Update.de_json(update_dict)

    # Process update (non-blocking)
    bot.process_new_updates([update])

    return {"ok": True}
```

**Set webhook with secret token:**
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.railway.app/webhook",
    "secret_token": "your_random_secret_32_chars"
  }'
```

### 3.2 Authentication & Middleware

#### Bot Token Auth
```python
# Verify X-Bot-Token header matches TELEGRAM_BOT_TOKEN
async def verify_bot_token(request: Request):
    token = request.headers.get("X-Bot-Token")
    if token != settings.TELEGRAM_BOT_TOKEN:
        raise HTTPException(401, "Invalid bot token")
```

#### User JWT Auth
```python
# JWT payload: {"sub": telegram_user_id, "exp": ...}
# Verify JWT and load user from database
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, settings.API_SECRET_KEY)
    user = await get_user_by_telegram_id(payload["sub"])
    return user
```

#### Rate Limiting

**Setup in `app/main.py`:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Usage in endpoints:
@app.post("/api/v1/logs/water")
@limiter.limit("60/minute")
async def log_water(request: Request, ...):
    ...
```

#### Idempotency
```python
# Check Redis for Idempotency-Key
# If exists, return cached response
# If not, process and cache for 15 minutes
async def ensure_idempotency(key: str, handler: Callable):
    cached = await redis.get(f"idempotency:{key}")
    if cached:
        return json.loads(cached)
    result = await handler()
    await redis.setex(f"idempotency:{key}", 900, json.dumps(result))
    return result
```

### 3.3 Business Logic Services

Create service classes in `backend/app/services/`:

**`user_service.py`**
- `create_or_update_user(telegram_user_id, ...)`
- `get_user_by_telegram_id(telegram_user_id)`
- `update_user_preferences(user_id, ...)`

**`goal_service.py`**
- `get_active_goal(user_id, date)`
- `create_goal(user_id, ...)`
- `get_goal_history(user_id)`

**`log_service.py`**
- `log_water(user_id, delta, ...)`
- `log_carbs(user_id, delta, subtype, ...)`
- `log_exercise(user_id, delta, ...)`
- `get_or_create_daily_log(user_id, date)`
- `get_or_create_weekly_log(user_id, week_start)`

**`progress_service.py`**
- `get_today_progress(user_id)`
- `get_week_progress(user_id)`
- `get_month_progress(user_id, year, month)`
- `calculate_streaks(user_id)`

**`notification_service.py`**
- `queue_broadcast(user_id, event_type, ...)`
- `send_daily_recap(user_id)`
- `send_weekly_recap(user_id)`

### 3.4 Complete FastAPI Application (`app/main.py`)

```python
import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from telebot import TeleBot, types
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import engine
from app.scheduler.jobs import scheduler
from app.api import auth, users, goals, logs, progress

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Telebot Tracker API",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.WEB_APP_URL,
        "http://localhost:3000",  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize bot (threaded=False for webhook mode)
bot = TeleBot(settings.TELEGRAM_BOT_TOKEN, threaded=False)

# Import bot handlers to register them
from app.bot import handlers

# Include API routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(goals.router)
app.include_router(logs.router)
app.include_router(progress.router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check for Railway"""
    checks = {
        "api": "healthy",
        "database": "unknown",
    }

    # Check database
    try:
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
        checks["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        checks["database"] = f"unhealthy: {str(e)}"

    status_code = 200 if all(v == "healthy" for v in checks.values()) else 503
    return checks

# Webhook endpoint
@app.post("/webhook")
async def webhook(request: Request):
    """Receive Telegram updates"""
    # Verify X-Telegram-Bot-Api-Secret-Token header
    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret_token != settings.TELEGRAM_WEBHOOK_SECRET:
        logger.warning("Invalid webhook secret token")
        raise HTTPException(status_code=403, detail="Invalid secret token")

    # Parse update
    update_dict = await request.json()
    update = types.Update.de_json(update_dict)

    # Process update
    bot.process_new_updates([update])

    return {"ok": True}

# Startup event
@app.on_event("startup")
async def startup():
    """Initialize services on startup"""
    logger.info(f"Starting application in {settings.ENVIRONMENT} mode")

    # Start scheduler
    scheduler.start()
    logger.info("Scheduler started")

    # Set webhook if production
    if settings.ENVIRONMENT == "production":
        webhook_url = f"{settings.TELEGRAM_WEBHOOK_URL}/webhook"
        try:
            bot.remove_webhook()
            bot.set_webhook(
                url=webhook_url,
                secret_token=settings.TELEGRAM_WEBHOOK_SECRET
            )
            logger.info(f"Webhook set to {webhook_url}")
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
    else:
        logger.info("Development mode - webhook not set")

# Shutdown event
@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    scheduler.shutdown()
    await engine.dispose()
    logger.info("Application shutdown complete")

# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.ENVIRONMENT == "development"
    )
```

---

## Phase 4: Telegram Bot Development

### 4.1 Bot Architecture

**Framework:** `pyTelegramBotAPI` (telebot)

**Create `app/bot/handlers.py`:**

```python
import logging
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.storage import StateRedisStorage
from app.config import settings
from app.services import user_service, log_service, progress_service
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

# Initialize Redis storage with 5-minute TTL for conversation timeout
state_storage = StateRedisStorage(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD if hasattr(settings, 'REDIS_PASSWORD') else None,
    prefix='telebot_state_',
)

# Initialize bot with state storage (imported in main.py)
bot = TeleBot(
    settings.TELEGRAM_BOT_TOKEN,
    threaded=False,
    state_storage=state_storage
)

# Error handling wrapper
async def safe_api_call(call, handler_func):
    """Wrapper for API calls with error handling"""
    try:
        return await handler_func()
    except Exception as e:
        logger.error(f"Error in callback {call.data}: {e}", exc_info=True)
        try:
            bot.answer_callback_query(call.id, "❌ Error occurred")
        except:
            pass
        bot.send_message(
            call.message.chat.id,
            "Sorry, something went wrong. Please try again."
        )
        return None

# Helper to answer callback with timeout
def answer_callback(call_id: str, text: str):
    """Answer callback query with timeout handling"""
    try:
        bot.answer_callback_query(call_id, text, timeout=5)
    except Exception as e:
        logger.warning(f"Failed to answer callback: {e}")
```

### 4.2 Command Handlers

**`/start` Command**
```python
@bot.message_handler(commands=['start'])
async def start_handler(message):
    telegram_user_id = message.from_user.id

    # Create user via API
    user = await api_client.create_user(
        telegram_user_id=telegram_user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )

    # Welcome message
    welcome_text = f"""
👋 Welcome {message.from_user.first_name}!

I'll help you track:
💧 Water intake (bottles)
🍽️ Carb consumption (portions)
🏃 Exercise sessions

Your default goals (tap Settings to change):
• Water: 3 bottles/day
• Carbs: Max 4 portions/day (meal=2, snack=1)
• Exercise: 6 sessions/week

Tap a button below to get started!
    """

    # Create keyboard with web app link
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🌐 Open Web App", url=f"{settings.WEB_APP_URL}")
    )
    keyboard.row(
        InlineKeyboardButton("💧 Water", callback_data="log_water"),
        InlineKeyboardButton("🍽️ Carbs", callback_data="log_carbs")
    )
    keyboard.row(
        InlineKeyboardButton("🏃 Exercise", callback_data="log_exercise"),
        InlineKeyboardButton("📊 Progress", callback_data="show_progress")
    )
    keyboard.row(InlineKeyboardButton("⚙️ Settings", callback_data="show_settings"))

    bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard)
```

**`/progress` Command**
```python
@bot.message_handler(commands=['progress'])
async def progress_handler(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📊 Today", callback_data="progress_today"),
        InlineKeyboardButton("📅 Past 7 Days", callback_data="progress_week")
    )
    keyboard.row(
        InlineKeyboardButton("🏃 This Week Exercise", callback_data="progress_exercise_week")
    )
    keyboard.row(
        InlineKeyboardButton("📈 Monthly Report", url=f"{settings.WEB_APP_URL}/reports")
    )

    bot.send_message(message.chat.id, "Choose a view:", reply_markup=keyboard)
```

**`/settings` Command**
```python
@bot.message_handler(commands=['settings'])
async def settings_handler(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("🎯 Edit Goals", callback_data="settings_goals"))
    keyboard.row(InlineKeyboardButton("🔔 Notifications", callback_data="settings_notifications"))
    keyboard.row(InlineKeyboardButton("🌐 Open Web App", url=f"{settings.WEB_APP_URL}"))

    bot.send_message(message.chat.id, "⚙️ Settings:", reply_markup=keyboard)
```

### 4.3 Inline Keyboards

**Main Menu**
```python
def create_main_menu():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("💧 Water", callback_data="log_water"),
        InlineKeyboardButton("🍽️ Carbs", callback_data="log_carbs")
    )
    keyboard.row(
        InlineKeyboardButton("🏃 Exercise", callback_data="log_exercise"),
        InlineKeyboardButton("📊 Progress", callback_data="show_progress")
    )
    keyboard.row(InlineKeyboardButton("⚙️ Settings", callback_data="show_settings"))
    return keyboard
```

**Water Logging Flow**
```python
@bot.callback_query_handler(func=lambda call: call.data == "log_water")
async def water_callback(call):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("+1 🚰", callback_data="water_add_1"),
        InlineKeyboardButton("+2 🚰", callback_data="water_add_2"),
        InlineKeyboardButton("+3 🚰", callback_data="water_add_3")
    )
    keyboard.row(
        InlineKeyboardButton("-1 🚰", callback_data="water_sub_1"),
        InlineKeyboardButton("Custom", callback_data="water_custom")
    )
    keyboard.row(InlineKeyboardButton("« Back", callback_data="main_menu"))

    bot.edit_message_text(
        "💧 Water - How many bottles?",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("water_add_"))
async def water_add_callback(call):
    # Extract amount from callback_data
    amount = int(call.data.split("_")[-1])

    # Call API with idempotency key
    result = await api_client.log_water(
        telegram_user_id=call.from_user.id,
        delta=amount,
        message_id=call.message.message_id,
        idempotency_key=call.id  # Telegram callback_query_id
    )

    # Build response message
    emoji = "✅" if result["remaining"] <= 0 else "💧"
    response = f"""
{emoji} Water logged!

Today: {result["new_total"]}/{result["goal"]} bottles
Remaining: {max(0, result["remaining"])} bottles
    """

    # Answer callback query (removes loading state)
    bot.answer_callback_query(call.id, "✅ Logged!")

    # Update message
    keyboard = create_main_menu()
    bot.edit_message_text(
        response,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard
    )
```

**Carbs Logging Flow**
```python
@bot.callback_query_handler(func=lambda call: call.data == "log_carbs")
async def carbs_callback(call):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🍽️ Meal (2 portions)", callback_data="carbs_type_meal"),
        InlineKeyboardButton("🍪 Snack (1 portion)", callback_data="carbs_type_snack")
    )
    keyboard.row(InlineKeyboardButton("« Back", callback_data="main_menu"))

    bot.edit_message_text(
        "🍽️ Carbs - Meal or Snack?",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("carbs_type_"))
async def carbs_type_callback(call):
    subtype = call.data.split("_")[-1]  # "meal" or "snack"

    # Show ALL portion options regardless of meal/snack choice
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("+2", callback_data=f"carbs_add_{subtype}_2"),
        InlineKeyboardButton("+1.5", callback_data=f"carbs_add_{subtype}_1.5"),
        InlineKeyboardButton("+1", callback_data=f"carbs_add_{subtype}_1"),
        InlineKeyboardButton("+0.5", callback_data=f"carbs_add_{subtype}_0.5")
    )
    keyboard.row(
        InlineKeyboardButton("-2", callback_data=f"carbs_sub_{subtype}_2"),
        InlineKeyboardButton("-1.5", callback_data=f"carbs_sub_{subtype}_1.5"),
        InlineKeyboardButton("-1", callback_data=f"carbs_sub_{subtype}_1"),
        InlineKeyboardButton("-0.5", callback_data=f"carbs_sub_{subtype}_0.5")
    )
    keyboard.row(
        InlineKeyboardButton("Custom", callback_data=f"carbs_custom_{subtype}")
    )
    keyboard.row(InlineKeyboardButton("« Back", callback_data="log_carbs"))

    # Show helper text based on subtype
    helper_text = "(Meal = 2 portions)" if subtype == "meal" else "(Snack = 1 portion)"

    bot.edit_message_text(
        f"🍽️ {subtype.capitalize()} {helper_text}\nHow many portions?",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("carbs_add_") or call.data.startswith("carbs_sub_"))
async def carbs_amount_callback(call):
    # Parse: carbs_add_meal_2 -> action=add, subtype=meal, amount=2
    parts = call.data.split("_")
    action = parts[1]  # "add" or "sub"
    subtype = parts[2]  # "meal" or "snack"
    amount = float(parts[3])

    delta = amount if action == "add" else -amount

    result = await api_client.log_carbs(
        telegram_user_id=call.from_user.id,
        delta=delta,
        subtype=subtype,
        message_id=call.message.message_id,
        idempotency_key=call.id
    )

    emoji = "⚠️" if result["over_limit"] else "✅"
    warning = "\n⚠️ Over your daily limit!" if result["over_limit"] else ""

    response = f"""
{emoji} Carbs logged!

Today: {result["new_total"]}/{result["goal"]} portions
Remaining: {max(0, result["remaining"])} portions{warning}
    """

    bot.answer_callback_query(call.id, "✅ Logged!")
    keyboard = create_main_menu()
    bot.edit_message_text(response, call.message.chat.id, call.message.message_id, reply_markup=keyboard)
```

**Exercise Logging Flow**
```python
@bot.callback_query_handler(func=lambda call: call.data == "log_exercise")
async def exercise_callback(call):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("+1 session", callback_data="exercise_add_1"),
        InlineKeyboardButton("+2 sessions", callback_data="exercise_add_2")
    )
    keyboard.row(
        InlineKeyboardButton("-1 session", callback_data="exercise_sub_1"),
        InlineKeyboardButton("Custom", callback_data="exercise_custom")
    )
    keyboard.row(InlineKeyboardButton("« Back", callback_data="main_menu"))

    bot.edit_message_text(
        "🏃 Exercise - How many sessions?",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("exercise_add_"))
async def exercise_add_callback(call):
    amount = int(call.data.split("_")[-1])

    result = await api_client.log_exercise(
        telegram_user_id=call.from_user.id,
        delta=amount,
        message_id=call.message.message_id,
        idempotency_key=call.id
    )

    emoji = "✅" if result["new_total"] >= result["weekly_goal"] else "🏃"
    response = f"""
{emoji} Exercise logged!

This week: {result["new_total"]}/{result["weekly_goal"]} sessions
Remaining: {max(0, result["remaining"])} sessions
Week: {result["week_start"]} - {result["week_end"]}
    """

    bot.answer_callback_query(call.id, "✅ Logged!")
    keyboard = create_main_menu()
    bot.edit_message_text(response, call.message.chat.id, call.message.message_id, reply_markup=keyboard)
```

### 4.4 Progress Display

**Today's Progress**
```python
@bot.callback_query_handler(func=lambda call: call.data == "progress_today")
async def progress_today_callback(call):
    progress = await api_client.get_today_progress(call.from_user.id)

    water_emoji = "✅" if progress["water"]["goal_met"] else "💧"
    carb_emoji = "✅" if not progress["carbs"]["over_limit"] else "⚠️"
    exercise_emoji = "✅" if progress["exercise"]["weekly_total"] >= progress["exercise"]["weekly_goal"] else "🏃"

    response = f"""
📊 Today's Progress ({progress["date"]})

{water_emoji} Water: {progress["water"]["current"]}/{progress["water"]["goal"]} bottles
   ({progress["water"]["percentage"]:.0f}% • {progress["water"]["remaining"]} remaining)

{carb_emoji} Carbs: {progress["carbs"]["current"]}/{progress["carbs"]["goal"]} portions
   ({progress["carbs"]["percentage"]:.0f}% • {progress["carbs"]["remaining"]} remaining)

{exercise_emoji} Exercise: {progress["exercise"]["weekly_total"]}/{progress["exercise"]["weekly_goal"]} sessions this week

🔥 Streaks:
   • Water: {progress["streaks"]["water_days"]} days
   • Carbs: {progress["streaks"]["carb_days"]} days
   • Both: {progress["streaks"]["combined_days"]} days
    """

    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("« Back", callback_data="show_progress"))

    bot.edit_message_text(response, call.message.chat.id, call.message.message_id, reply_markup=keyboard)
```

**This Week's Exercise Progress**
```python
@bot.callback_query_handler(func=lambda call: call.data == "progress_exercise_week")
async def progress_exercise_week_callback(call):
    progress = await api_client.get_week_progress(call.from_user.id)

    weekly_ex = progress["weekly_exercise"]
    percentage = (weekly_ex["total"] / weekly_ex["goal"] * 100) if weekly_ex["goal"] > 0 else 0

    # Create progress bar
    filled = int(percentage / 10)
    bar = "█" * filled + "░" * (10 - filled)

    status_emoji = "✅" if weekly_ex["goal_met"] else "💪"
    status_text = "Goal met!" if weekly_ex["goal_met"] else f"{weekly_ex['remaining']} more to go!"

    response = f"""
🏃 This Week's Exercise

{bar} {percentage:.0f}%

Sessions: {weekly_ex["total"]}/{weekly_ex["goal"]}
{status_emoji} {status_text}

Week: {progress["week_start"]} to {progress["week_end"]}
    """

    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("« Back", callback_data="show_progress"))

    bot.edit_message_text(response, call.message.chat.id, call.message.message_id, reply_markup=keyboard)
```

### 4.5 Conversation State Management

For custom input (e.g., "Custom" water amount):
```python
from telebot.handler_backends import State, StatesGroup

class LoggingStates(StatesGroup):
    waiting_water_amount = State()
    waiting_carb_amount = State()
    waiting_exercise_amount = State()

# Note: StateRedisStorage automatically expires states after 5 minutes of inactivity
# Configure TTL in Redis storage initialization (default is 300 seconds)

@bot.callback_query_handler(func=lambda call: call.data == "water_custom")
async def water_custom_callback(call):
    bot.set_state(call.from_user.id, LoggingStates.waiting_water_amount, call.message.chat.id)

    # Add cancel button
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("❌ Cancel", callback_data="cancel_input"))

    bot.send_message(
        call.message.chat.id,
        "💧 Enter number of bottles (e.g., 1.5):",
        reply_markup=keyboard
    )

@bot.message_handler(state=LoggingStates.waiting_water_amount)
async def water_custom_amount(message):
    try:
        amount = float(message.text)
        if amount < -50 or amount > 50:
            raise ValueError("Amount out of range")

        result = await api_client.log_water(
            telegram_user_id=message.from_user.id,
            delta=amount,
            message_id=message.message_id
        )

        response = f"✅ Logged {amount} bottles!\n\nToday: {result['new_total']}/{result['goal']} bottles"
        keyboard = create_main_menu()
        bot.send_message(message.chat.id, response, reply_markup=keyboard)

        bot.delete_state(message.from_user.id, message.chat.id)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid number. Please enter a valid amount:")

# Cancel handler for all state flows
@bot.callback_query_handler(func=lambda call: call.data == "cancel_input")
async def cancel_input_callback(call):
    """Cancel any active input state and return to main menu"""
    bot.delete_state(call.from_user.id, call.message.chat.id)
    bot.answer_callback_query(call.id, "❌ Cancelled")

    keyboard = create_main_menu()
    bot.edit_message_text(
        "❌ Cancelled. Choose an action:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard
    )
```

### 4.6 Broadcast Notifications (Using RQ)

**Create `app/services/notification_service.py`:**

```python
from rq import Queue
from redis import Redis
from app.config import settings
import logging
import time

logger = logging.getLogger(__name__)

# Initialize Redis connection
redis_conn = Redis.from_url(settings.REDIS_URL)
queue = Queue('broadcasts', connection=redis_conn)

# Broadcast debouncing: 1-minute window to collapse bursts
DEBOUNCE_WINDOW = 60  # seconds

async def queue_broadcast(user_id: int, event_type: str, delta: float, new_total: float):
    """
    Queue broadcast for background processing with burst collapsing.

    If the same user logs multiple events within 1 minute, only the latest
    event is broadcast to prevent spam.
    """
    try:
        # Create debounce key
        debounce_key = f"broadcast_debounce:{user_id}:{event_type}"

        # Check if there's a pending broadcast for this user+event
        existing_job_id = redis_conn.get(debounce_key)

        if existing_job_id:
            # Cancel the existing job (it will be replaced)
            try:
                from rq.job import Job
                existing_job = Job.fetch(existing_job_id.decode(), connection=redis_conn)
                existing_job.cancel()
                logger.info(f"Cancelled previous broadcast job {existing_job_id} (burst collapse)")
            except:
                pass  # Job may have already completed

        # Queue new broadcast with delay
        job = queue.enqueue_in(
            time_delta=DEBOUNCE_WINDOW,  # Wait 60 seconds before sending
            func='app.workers.broadcast.send_broadcast',
            user_id=user_id,
            event_type=event_type,
            delta=delta,
            new_total=new_total,
            job_timeout='5m'
        )

        # Store job ID for debouncing
        redis_conn.setex(debounce_key, DEBOUNCE_WINDOW + 10, job.id)

        logger.info(f"Queued broadcast job {job.id} for user {user_id} (debounced {DEBOUNCE_WINDOW}s)")
    except Exception as e:
        logger.error(f"Failed to queue broadcast: {e}")
```

**Create `app/workers/broadcast.py`:**

```python
import logging
from telebot import TeleBot
from app.config import settings
from app.database import AsyncSessionLocal
from app.services.user_service import get_user_by_id, get_broadcast_recipients

logger = logging.getLogger(__name__)

# Initialize bot for worker
bot = TeleBot(settings.TELEGRAM_BOT_TOKEN)

def send_broadcast(user_id: int, event_type: str, delta: float, new_total: float):
    """
    Worker function to send broadcasts (runs in RQ worker process)
    This is a synchronous function called by RQ
    """
    import asyncio

    async def _send():
        async with AsyncSessionLocal() as db:
            # Get sender info
            sender = await get_user_by_id(user_id, db)
            if not sender:
                logger.error(f"User {user_id} not found")
                return

            # Get all active users (broadcast_opt_out = false)
            recipients = await get_broadcast_recipients(
                exclude_user_id=sender.telegram_user_id,
                db=db
            )

            # Build message
            emoji_map = {"water": "💧", "carbs": "🍽️", "exercise": "🏃"}
            emoji = emoji_map.get(event_type, "📊")

            action = "added" if delta > 0 else "removed"
            message = f"{emoji} {sender.first_name} just {action} {abs(delta)} {event_type}! (Total: {new_total})"

            # Send to all recipients
            success_count = 0
            for recipient in recipients:
                try:
                    bot.send_message(recipient["telegram_user_id"], message)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to send broadcast to {recipient['telegram_user_id']}: {e}")

            logger.info(f"Broadcast sent to {success_count}/{len(recipients)} users")

    # Run async function in sync context
    asyncio.run(_send())
```

**Usage in log endpoints:**

```python
# In app/api/logs.py
from app.services.notification_service import queue_broadcast

@router.post("/logs/water")
async def log_water(...):
    # ... log water ...

    # Queue broadcast (non-blocking)
    await queue_broadcast(
        user_id=user.id,
        event_type="water",
        delta=delta,
        new_total=result.new_total
    )

    return result
```

### 4.7 Webhook Setup

**Development (Polling)**
```python
if settings.ENVIRONMENT == "development":
    bot.infinity_polling()
```

**Production (Webhook)**
```python
if settings.ENVIRONMENT == "production":
    # Set webhook
    webhook_url = f"{settings.TELEGRAM_WEBHOOK_URL}/webhook"
    bot.set_webhook(url=webhook_url)

    # FastAPI endpoint
    @app.post("/webhook")
    async def webhook_handler(request: Request):
        update = await request.json()
        bot.process_new_updates([telebot.types.Update.de_json(update)])
        return {"ok": True}
```

---

## Phase 5: Scheduler & Background Jobs

### 5.1 APScheduler Setup

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

scheduler = AsyncIOScheduler()

# Singapore timezone
sg_tz = pytz.timezone("Asia/Singapore")
```

### 5.2 Daily Reset Job

```python
async def daily_reset_job():
    """Reset daily counters at midnight Singapore time"""
    logger.info("Running daily reset job...")

    # Get all active users
    users = await api_client.get_all_active_users()

    for user in users:
        try:
            # Send daily recap (if enabled)
            if user["recap_enabled"]:
                await send_daily_recap(user["id"])

            # Daily logs are automatically created on first log of new day
            # No need to explicitly reset

        except Exception as e:
            logger.error(f"Failed daily reset for user {user['id']}: {e}")

# Schedule at 00:05 Singapore time
scheduler.add_job(
    daily_reset_job,
    CronTrigger(hour=0, minute=5, timezone=sg_tz),
    id="daily_reset",
    replace_existing=True
)
```

### 5.3 Daily Recap Notification

```python
async def send_daily_recap(user_id: int):
    """Send end-of-day summary to user"""

    # Get yesterday's progress
    yesterday = (datetime.now(sg_tz) - timedelta(days=1)).date()
    progress = await api_client.get_day_progress(user_id, yesterday)

    water_emoji = "✅" if progress["water"]["goal_met"] else "❌"
    carb_emoji = "✅" if not progress["carbs"]["over_limit"] else "❌"

    message = f"""
🌙 Daily Recap - {yesterday}

{water_emoji} Water: {progress["water"]["current"]}/{progress["water"]["goal"]} bottles
{carb_emoji} Carbs: {progress["carbs"]["current"]}/{progress["carbs"]["goal"]} portions
🏃 Exercise: {progress["exercise"]["today"]} sessions

Keep it up! 💪
    """

    user = await api_client.get_user(user_id)
    bot.send_message(user["telegram_user_id"], message)
```

### 5.4 Weekly Reset Job

```python
async def weekly_reset_job():
    """Reset weekly exercise counter on Monday"""
    logger.info("Running weekly reset job...")

    users = await api_client.get_all_active_users()

    for user in users:
        try:
            # Send weekly recap
            await send_weekly_recap(user["id"])

            # Weekly logs are automatically created on first exercise log of new week

        except Exception as e:
            logger.error(f"Failed weekly reset for user {user['id']}: {e}")

# Schedule at Monday 00:10 Singapore time
scheduler.add_job(
    weekly_reset_job,
    CronTrigger(day_of_week='mon', hour=0, minute=10, timezone=sg_tz),
    id="weekly_reset",
    replace_existing=True
)
```

### 5.5 Weekly Recap Notification

```python
async def send_weekly_recap(user_id: int):
    """Send end-of-week exercise summary"""

    # Get last week's data
    last_week_start = (datetime.now(sg_tz) - timedelta(days=7)).date()
    last_week_start = last_week_start - timedelta(days=last_week_start.weekday())  # Monday

    weekly_log = await api_client.get_weekly_log(user_id, last_week_start)
    goal = await api_client.get_active_goal(user_id, last_week_start)

    emoji = "✅" if weekly_log["exercise_sessions"] >= goal["weekly_exercise_sessions"] else "❌"

    message = f"""
📅 Weekly Recap - Week of {last_week_start}

{emoji} Exercise: {weekly_log["exercise_sessions"]}/{goal["weekly_exercise_sessions"]} sessions

{"🎉 Goal achieved!" if emoji == "✅" else "Keep pushing next week! 💪"}
    """

    user = await api_client.get_user(user_id)
    bot.send_message(user["telegram_user_id"], message)
```

### 5.6 Monthly Stats Refresh

```python
async def refresh_monthly_stats():
    """Refresh materialized view for monthly stats"""
    logger.info("Refreshing monthly stats...")

    async with get_db_session() as session:
        await session.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_stats")
        await session.commit()

# Schedule daily at 01:00 Singapore time
scheduler.add_job(
    refresh_monthly_stats,
    CronTrigger(hour=1, minute=0, timezone=sg_tz),
    id="refresh_monthly_stats",
    replace_existing=True
)
```

### 5.7 Start Scheduler

```python
# In main.py
scheduler.start()
logger.info("Scheduler started")
```

---

## Phase 6: Web App Development

### 6.1 Next.js Project Structure

```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx              # Landing page
│   ├── dashboard/
│   │   └── page.tsx          # Main dashboard
│   ├── goals/
│   │   └── page.tsx          # Goal configuration
│   ├── analytics/
│   │   └── page.tsx          # Monthly analytics
│   └── settings/
│       └── page.tsx          # User settings
├── components/
│   ├── auth/
│   │   └── TelegramLoginButton.tsx
│   ├── dashboard/
│   │   ├── TodayCard.tsx
│   │   ├── WeeklyChart.tsx
│   │   └── StreakBadge.tsx
│   ├── goals/
│   │   └── GoalForm.tsx
│   └── ui/                   # shadcn/ui components
├── lib/
│   ├── api.ts                # API client
│   ├── auth.ts               # JWT handling
│   └── utils.ts
└── package.json
```

### 6.2 Telegram Login Widget

```tsx
// components/auth/TelegramLoginButton.tsx
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function TelegramLoginButton() {
  const router = useRouter();

  useEffect(() => {
    // Load Telegram Widget script
    const script = document.createElement('script');
    script.src = 'https://telegram.org/js/telegram-widget.js?22';
    script.setAttribute('data-telegram-login', 'YOUR_BOT_USERNAME');
    script.setAttribute('data-size', 'large');
    script.setAttribute('data-auth-url', `${process.env.NEXT_PUBLIC_API_URL}/auth/telegram`);
    script.setAttribute('data-request-access', 'write');
    script.async = true;

    document.getElementById('telegram-login')?.appendChild(script);
  }, []);

  return <div id="telegram-login"></div>;
}
```

### 6.3 API Client

```typescript
// lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

// Add JWT token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwt_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const apiClient = {
  // Goals
  getGoals: () => api.get('/api/v1/goals'),
  createGoal: (data: GoalInput) => api.post('/api/v1/goals', data),

  // Progress
  getTodayProgress: () => api.get('/api/v1/progress/today'),
  getWeekProgress: () => api.get('/api/v1/progress/week'),
  getMonthProgress: (year: number, month: number) =>
    api.get(`/api/v1/progress/month?year=${year}&month=${month}`),

  // User
  getMe: () => api.get('/api/v1/users/me'),
  updatePreferences: (data: UserPreferences) => api.patch('/api/v1/users/me', data),
};
```

### 6.4 Dashboard Page

```tsx
// app/dashboard/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';
import TodayCard from '@/components/dashboard/TodayCard';
import WeeklyChart from '@/components/dashboard/WeeklyChart';

export default function DashboardPage() {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchProgress() {
      try {
        const { data } = await apiClient.getTodayProgress();
        setProgress(data);
      } catch (error) {
        console.error('Failed to fetch progress:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchProgress();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <TodayCard
          title="Water"
          current={progress.water.current}
          goal={progress.water.goal}
          emoji="💧"
        />
        <TodayCard
          title="Carbs"
          current={progress.carbs.current}
          goal={progress.carbs.goal}
          emoji="🍽️"
        />
        <TodayCard
          title="Exercise"
          current={progress.exercise.weekly_total}
          goal={progress.exercise.weekly_goal}
          emoji="🏃"
        />
      </div>

      <WeeklyChart />
    </div>
  );
}
```

### 6.5 Goal Configuration Form

```tsx
// components/goals/GoalForm.tsx
'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function GoalForm({ currentGoals }) {
  const [goals, setGoals] = useState(currentGoals);
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      await apiClient.createGoal(goals);
      alert('Goals updated successfully!');
    } catch (error) {
      alert('Failed to update goals');
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <Label htmlFor="water">Daily Water Goal (bottles)</Label>
        <Input
          id="water"
          type="number"
          step="0.5"
          min="0.5"
          max="20"
          value={goals.daily_water_bottles}
          onChange={(e) => setGoals({...goals, daily_water_bottles: parseFloat(e.target.value)})}
        />
      </div>

      <div>
        <Label htmlFor="carbs">Daily Carb Limit (portions)</Label>
        <Input
          id="carbs"
          type="number"
          step="0.5"
          min="0.5"
          max="20"
          value={goals.daily_carb_max_portions}
          onChange={(e) => setGoals({...goals, daily_carb_max_portions: parseFloat(e.target.value)})}
        />
        <p className="text-sm text-gray-500 mt-1">
          Note: Meal = 2 portions, Snack = 1 portion
        </p>
      </div>

      <div>
        <Label htmlFor="exercise">Weekly Exercise Goal (sessions)</Label>
        <Input
          id="exercise"
          type="number"
          min="1"
          max="30"
          value={goals.weekly_exercise_sessions}
          onChange={(e) => setGoals({...goals, weekly_exercise_sessions: parseInt(e.target.value)})}
        />
      </div>

      <Button type="submit" disabled={saving}>
        {saving ? 'Saving...' : 'Save Goals'}
      </Button>
    </form>
  );
}
```

---

## Phase 7: Testing & QA

### 7.1 Backend Tests

```python
# tests/test_log_service.py
import pytest
from app.services.log_service import log_water

@pytest.mark.asyncio
async def test_log_water_positive_delta(test_user):
    result = await log_water(test_user.id, delta=2.0)
    assert result["new_total"] == 2.0
    assert result["remaining"] == 1.0  # Assuming goal is 3.0

@pytest.mark.asyncio
async def test_log_water_negative_clamp(test_user):
    # First add 1 bottle
    await log_water(test_user.id, delta=1.0)
    # Try to remove 5 bottles (should clamp to 0)
    result = await log_water(test_user.id, delta=-5.0)
    assert result["new_total"] == 0.0

@pytest.mark.asyncio
async def test_idempotency(test_user):
    # Same idempotency key should return same result
    result1 = await log_water(test_user.id, delta=1.0, idempotency_key="test123")
    result2 = await log_water(test_user.id, delta=1.0, idempotency_key="test123")
    assert result1 == result2
    assert result1["new_total"] == 1.0  # Not 2.0
```

### 7.2 Bot Integration Tests

```python
# tests/test_bot_handlers.py
import pytest
from telebot.types import Message, CallbackQuery

@pytest.mark.asyncio
async def test_start_command(mock_bot, test_user):
    message = Message(
        message_id=1,
        from_user=test_user,
        chat={"id": 123},
        text="/start"
    )

    await start_handler(message)

    # Verify user created in database
    user = await get_user_by_telegram_id(test_user.id)
    assert user is not None
    assert user.timezone == "Asia/Singapore"

@pytest.mark.asyncio
async def test_water_logging_flow(mock_bot, test_user):
    # Simulate clicking "Water" button
    call = CallbackQuery(id="1", from_user=test_user, data="log_water")
    await water_callback(call)

    # Simulate clicking "+1" button
    call2 = CallbackQuery(id="2", from_user=test_user, data="water_add_1")
    await water_add_callback(call2)

    # Verify log created
    progress = await get_today_progress(test_user.id)
    assert progress["water"]["current"] == 1.0
```

### 7.3 End-to-End Test Checklist

- [ ] New user onboarding flow
- [ ] Log water (positive and negative)
- [ ] Log carbs (meal and snack)
- [ ] Log exercise
- [ ] View today's progress
- [ ] View weekly progress
- [ ] Change goals via bot
- [ ] Change goals via web app
- [ ] Daily recap notification
- [ ] Weekly recap notification
- [ ] Broadcast notification
- [ ] Opt-out from broadcasts
- [ ] Idempotency (double-click protection)
- [ ] Rate limiting
- [ ] Timezone handling (all Singapore time)
- [ ] Monthly stats calculation

---

## Phase 8: Deployment & Monitoring

### 8.1 Railway Deployment

**Step 1: Create Railway Account**
1. Sign up at https://railway.app
2. Connect GitHub account

**Step 2: Create New Project**
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository
4. Railway auto-detects Python app

**Step 3: Configure Environment Variables**
Add all variables from `.env`:
```
TELEGRAM_BOT_TOKEN=...
DATABASE_URL=...  (Railway provides this if using Railway Postgres)
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...
API_SECRET_KEY=...
REDIS_URL=...  (Railway provides this if using Railway Redis)
ENVIRONMENT=production
TELEGRAM_WEBHOOK_URL=https://your-app.railway.app
```

**Step 4: Add Services**
- **PostgreSQL:** Click "New" → "Database" → "PostgreSQL" (or use Supabase)
- **Redis:** Click "New" → "Database" → "Redis"

**Step 5: Configure Build**
Railway auto-detects `pyproject.toml` and uses Poetry.

Create `railway.toml`:
```toml
[build]
builder = "NIXPACKS"

[deploy]
# Run migrations, start FastAPI server, and RQ worker in background
startCommand = "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT & rq worker broadcasts --url $REDIS_URL"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

**Note:** This starts both the FastAPI server and RQ worker in a single dyno. For production at scale, consider running RQ worker as a separate Railway service.

**Alternative: Separate RQ Worker Service**

If you want to scale workers independently:

1. Create a second Railway service from the same repo
2. Set environment variables (same as main service)
3. Use this `railway.toml` for the worker service:

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "rq worker broadcasts --url $REDIS_URL"
```

**Step 6: Set Webhook**
After deployment, get your Railway URL (e.g., `https://telebot-production.up.railway.app`)

Run once to set webhook with secret token:
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://telebot-production.up.railway.app/webhook",
    "secret_token": "<YOUR_TELEGRAM_WEBHOOK_SECRET>"
  }'
```

**Verify webhook:**
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

### 8.2 Vercel Deployment (Web App)

**Step 1: Push Frontend to GitHub**
Separate repo or monorepo with `frontend/` directory

**Step 2: Import to Vercel**
1. Go to https://vercel.com
2. Click "New Project"
3. Import from GitHub
4. Set root directory to `frontend/` if monorepo

**Step 3: Configure Environment Variables**
```
NEXT_PUBLIC_API_URL=https://telebot-production.up.railway.app
NEXT_PUBLIC_BOT_USERNAME=your_bot_username
```

**Step 4: Deploy**
Vercel auto-deploys on push to main branch

### 8.3 Database Migrations

**Production Migration Strategy:**
```bash
# SSH into Railway or run via Railway CLI
railway run alembic upgrade head
```

Or add to `railway.toml`:
```toml
[deploy]
startCommand = "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

### 8.4 Monitoring & Logging

**Sentry for Error Tracking**
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment=settings.ENVIRONMENT
)
```

**Railway Logs**
- View logs in Railway dashboard
- Set up log drains to external services (optional)

**Health Check Endpoint**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(sg_tz).isoformat(),
        "environment": settings.ENVIRONMENT
    }
```

**Uptime Monitoring**
- Use UptimeRobot (free) to ping `/health` every 5 minutes
- Alert on downtime via email/Telegram

### 8.5 Backup Strategy

**Database Backups**
- Supabase: Automatic daily backups (free tier: 7 days retention)
- Railway Postgres: Manual backups via Railway CLI or pg_dump

**Manual Backup Script**
```bash
#!/bin/bash
# backup.sh
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
# Upload to S3 or Google Drive
```

---

## Summary & Next Steps

### Development Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Setup | 1 day | None |
| Phase 2: Database | 1 day | Phase 1 |
| Phase 3: Backend API | 3-4 days | Phase 2 |
| Phase 4: Telegram Bot | 3-4 days | Phase 3 |
| Phase 5: Scheduler | 1-2 days | Phase 3, 4 |
| Phase 6: Web App | 3-4 days | Phase 3 |
| Phase 7: Testing | 2-3 days | All phases |
| Phase 8: Deployment | 1 day | Phase 7 |
| **Total** | **15-20 days** | |

### Key Decisions Made

✅ **Timezone:** All users use Singapore Time (Asia/Singapore, UTC+8) - no user selection needed
✅ **Deployment:** Railway for backend/bot, Vercel for web app, Supabase for database
✅ **Bot Framework:** pyTelegramBotAPI (simple, production-ready)
✅ **API Framework:** FastAPI (modern, async, auto-docs)
✅ **Scheduler:** APScheduler with timezone-aware cron jobs
✅ **Webhook vs Polling:** Webhook for production (faster, more reliable)

### Recommended Development Order

1. **Start with Phase 1-2:** Set up infrastructure and database
2. **Build Phase 3 (API) incrementally:** Start with user/goal endpoints, then logging
3. **Develop Phase 4 (Bot) in parallel:** Can test with polling mode locally
4. **Add Phase 5 (Scheduler):** Once logging works
5. **Build Phase 6 (Web App):** Can be done in parallel with bot
6. **Phase 7 (Testing):** Continuous throughout development
7. **Phase 8 (Deployment):** Final step

### Critical Success Factors

🎯 **Idempotency:** Prevent double-logging from button double-clicks
🎯 **Rate Limiting:** Prevent spam and abuse
🎯 **Error Handling:** Graceful degradation, user-friendly error messages
🎯 **Timezone Consistency:** All dates/times in Singapore timezone
🎯 **Database Indexes:** Ensure fast queries on user_id + date
🎯 **Webhook Reliability:** Monitor webhook health, fallback to polling if needed

---

## Appendix: Useful Commands

### Development
```bash
# Start local development
cd backend
poetry install
poetry run uvicorn app.main:app --reload

# Run bot (polling mode)
poetry run python bot/main.py

# Run tests
poetry run pytest

# Database migrations
poetry run alembic revision --autogenerate -m "description"
poetry run alembic upgrade head
```

### Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# View logs
railway logs

# Run migrations
railway run alembic upgrade head

# SSH into container
railway shell
```

### Telegram Bot Commands
```bash
# Set webhook
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook?url=<URL>/webhook"

# Get webhook info
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"

# Delete webhook (switch to polling)
curl -X POST "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
```

---

**END OF IMPLEMENTATION PLAN**

