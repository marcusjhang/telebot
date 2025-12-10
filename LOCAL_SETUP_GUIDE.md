# Local Setup Guide - Running Everything Locally

This guide will help you run the entire Telegram Health Tracker application on your local machine.

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.11+** installed
- **Node.js 18+** and npm installed
- **PostgreSQL** installed (or use Docker)
- **Redis** installed (or use Docker)
- **Telegram Bot Token** from [@BotFather](https://t.me/botfather)

---

## Quick Start with Docker (Recommended)

### 1. Start PostgreSQL and Redis with Docker

```bash
# Start PostgreSQL and Redis
cd backend
docker-compose up -d

# This will start:
# - PostgreSQL on localhost:5432
# - Redis on localhost:6379
```

### 2. Verify Docker containers are running

```bash
docker ps

# You should see:
# - postgres container
# - redis container
```

---

## Manual Setup (Without Docker)

### Option A: Install PostgreSQL

**macOS (using Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb telebot_tracker
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql

# Create database
sudo -u postgres createdb telebot_tracker
```

### Option B: Install Redis

**macOS (using Homebrew):**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt install redis-server
sudo systemctl start redis-server
```

---

## Backend Setup

### 1. Install Poetry (Python dependency manager)

```bash
# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# Or using pip
pip3 install poetry
```

### 2. Install Backend Dependencies

```bash
cd backend

# Install all dependencies
poetry install

# This creates a virtual environment and installs all packages
```

### 3. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your values
nano .env  # or use your preferred editor
```

**Required environment variables in `.env`:**

```bash
# Telegram Bot (Get from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_WEBHOOK_SECRET=any_random_string_32_chars

# Database (if using Docker Compose, use this)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/telebot_tracker

# Redis (if using Docker Compose, use this)
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# JWT Secret (generate a random string)
JWT_SECRET_KEY=your_random_secret_key_min_32_chars_here

# API Configuration
API_V1_PREFIX=/api/v1
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Web App
WEB_APP_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Generate secure secrets:**
```bash
# Generate JWT secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate webhook secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Run Database Migrations

```bash
# Make sure you're in the backend directory
cd backend

# Run migrations to create tables
poetry run alembic upgrade head

# You should see:
# INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial schema...
```

### 5. Start the Backend Server

```bash
# Start FastAPI server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

**Test the backend:**
```bash
# In a new terminal
curl http://localhost:8000/health

# Should return:
# {"api":"healthy","database":"healthy"}
```

### 6. Start the Bot (Polling Mode for Development)

**In a new terminal:**

```bash
cd backend

# Start bot polling
poetry run python -m app.bot.polling

# You should see:
# INFO - Bot started polling...
```

**Test the bot:**
- Open Telegram
- Search for your bot (username from @BotFather)
- Send `/start` command
- You should get a welcome message!

---

## Frontend Setup

### 1. Install Frontend Dependencies

```bash
cd frontend

# Install all npm packages
npm install
```

### 2. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env.local

# Edit .env.local
nano .env.local  # or use your preferred editor
```

**Required environment variables in `.env.local`:**

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Your bot username (from @BotFather)
NEXT_PUBLIC_BOT_USERNAME=your_bot_username
```

### 3. Start the Frontend Development Server

```bash
# Start Next.js dev server
npm run dev

# You should see:
# ▲ Next.js 16.0.8
# - Local:        http://localhost:3000
# - Ready in 2.5s
```

**Test the frontend:**
- Open browser: http://localhost:3000
- You should see the landing page with "Login with Telegram" button

---

## Complete Local Testing

### 1. Test the Full Flow

**Terminal 1 - Backend:**
```bash
cd backend
poetry run uvicorn app.main:app --reload
```

**Terminal 2 - Bot:**
```bash
cd backend
poetry run python -m app.bot.polling
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 4 - Docker (if using):**
```bash
cd backend
docker-compose up
```

### 2. Test Authentication Flow

1. Open http://localhost:3000 in browser
2. Click "Login with Telegram"
3. Authorize the bot
4. You should be redirected to the dashboard

### 3. Test Bot Commands

In Telegram, send these commands to your bot:

```
/start          - Register and see welcome message
/progress       - View today's progress
/settings       - Toggle daily recap
```

Test logging flows:
- Click "💧 Log Water" button
- Click "🍽️ Log Carbs" button
- Click "🏃 Log Exercise" button

### 4. Test Web Dashboard

After logging in:
- View today's progress cards
- Check streak badges
- Navigate to Goals page
- Navigate to Settings page

---

## Troubleshooting

### Backend won't start

**Error: "No module named 'pydantic_settings'"**
```bash
cd backend
poetry install
```

**Error: "Connection refused" (Database)**
```bash
# Check if PostgreSQL is running
docker ps  # if using Docker
# or
brew services list  # if using Homebrew

# Check DATABASE_URL in .env
```

**Error: "Connection refused" (Redis)**
```bash
# Check if Redis is running
docker ps  # if using Docker
# or
redis-cli ping  # should return PONG
```

### Bot won't respond

**Check bot token:**
```bash
# Test bot token
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe

# Should return bot info
```

**Check polling is running:**
```bash
# Make sure you see "Bot started polling..." in terminal
```

### Frontend can't connect to backend

**Check CORS settings:**
- Make sure `BACKEND_CORS_ORIGINS` in backend `.env` includes `http://localhost:3000`

**Check API URL:**
- Make sure `NEXT_PUBLIC_API_URL` in frontend `.env.local` is `http://localhost:8000`

### Database migration fails

**Reset database:**
```bash
cd backend

# Downgrade all migrations
poetry run alembic downgrade base

# Re-run migrations
poetry run alembic upgrade head
```

---

## Useful Commands

### Backend

```bash
# Run tests (when implemented)
poetry run pytest

# Check code style
poetry run black app/
poetry run ruff check app/

# View logs
tail -f logs/app.log  # if logging to file
```

### Frontend

```bash
# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### Database

```bash
# Connect to PostgreSQL
psql -U postgres -d telebot_tracker

# View tables
\dt

# View users
SELECT * FROM users;

# View logs
SELECT * FROM daily_logs ORDER BY log_date DESC LIMIT 10;
```

### Redis

```bash
# Connect to Redis
redis-cli

# View all keys
KEYS *

# View bot state
KEYS telebot_state_*

# Clear all data (careful!)
FLUSHALL
```

---

## Next Steps

Once everything is running locally:

1. **Test all features thoroughly**
2. **Check scheduler jobs** (they run at specific times in SGT)
3. **Review logs** for any errors
4. **Test edge cases** (invalid inputs, network errors, etc.)
5. **Prepare for deployment** (see DEPLOYMENT_GUIDE.md)

---

## Quick Reference

**Start everything:**
```bash
# Terminal 1 - Docker services
cd backend && docker-compose up

# Terminal 2 - Backend
cd backend && poetry run uvicorn app.main:app --reload

# Terminal 3 - Bot
cd backend && poetry run python -m app.bot.polling

# Terminal 4 - Frontend
cd frontend && npm run dev
```

**Stop everything:**
```bash
# Ctrl+C in each terminal
# Then stop Docker:
cd backend && docker-compose down
```

---

**Need help?** Check the detailed documentation:
- `backend/README.md` - Backend documentation
- `frontend/README.md` - Frontend documentation
- `IMPLEMENTATION_PLAN.md` - Full project specification

