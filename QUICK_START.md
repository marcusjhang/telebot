# Quick Start - Run Locally in 5 Minutes

## The Problem You're Facing

Your system Python (3.9 from Command Line Tools) can't create virtual environments properly. Here's the **easiest solution**:

---

## ✅ Solution: Install Poetry with Homebrew

### Step 1: Install Poetry

```bash
brew install poetry
```

If you don't have Homebrew, install it first:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Verify Poetry is installed

```bash
poetry --version
# Should show: Poetry (version 1.8.x)
```

---

## 🚀 Now Run Everything

### Option A: Automated (Recommended)

```bash
./start-local.sh
```

This will:
1. Check prerequisites
2. Start Docker (PostgreSQL & Redis)
3. Install dependencies
4. Run migrations
5. Tell you what to do next

### Option B: Manual Steps

#### 1. Get Your Bot Token

1. Open Telegram
2. Message [@BotFather](https://t.me/botfather)
3. Send `/newbot`
4. Follow instructions to create your bot
5. Copy the token (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### 2. Start Docker Services

```bash
cd backend
docker-compose up -d
```

Wait 10 seconds for services to start.

#### 3. Setup Backend

```bash
cd backend

# Install dependencies
poetry install

# Create .env file
cp .env.example .env

# Edit .env and add your bot token
nano .env
# Change: TELEGRAM_BOT_TOKEN=your_bot_token_here
# Save: Ctrl+O, Enter, Ctrl+X

# Run migrations
poetry run alembic upgrade head
```

#### 4. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
cp .env.example .env.local

# Edit with your bot username (from @BotFather)
nano .env.local
# Change: NEXT_PUBLIC_BOT_USERNAME=your_bot_username
# Save: Ctrl+O, Enter, Ctrl+X
```

#### 5. Start Everything (3 Terminals)

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

---

## ✅ Test It Works

### 1. Test Backend
```bash
curl http://localhost:8000/health
# Should return: {"api":"healthy","database":"healthy"}
```

### 2. Test Bot
- Open Telegram
- Search for your bot
- Send `/start`
- You should get a welcome message!

### 3. Test Frontend
- Open browser: http://localhost:3000
- Click "Login with Telegram"
- Authorize
- See your dashboard!

---

## 🎯 What You'll See

### In Telegram Bot:
```
🎉 Welcome to Health Tracker!

I'll help you track:
💧 Water intake
🍽️ Carb consumption  
🏃 Exercise sessions

Use the buttons below to get started!

[💧 Log Water] [🍽️ Log Carbs] [🏃 Log Exercise]
[📊 View Progress] [⚙️ Settings]
```

### In Web Dashboard:
- Today's progress cards (water, carbs, exercise)
- Streak badges
- Goal configuration
- Settings

---

## 🛑 Stop Everything

```bash
# Stop the 3 terminals with Ctrl+C

# Stop Docker
cd backend
docker-compose down
```

---

## 🔧 Troubleshooting

### "Poetry not found"
```bash
brew install poetry
```

### "Docker not running"
```bash
# Start Docker Desktop app
# Or install: brew install --cask docker
```

### "Port 5432 already in use"
```bash
# Stop existing PostgreSQL
brew services stop postgresql
# Or change port in docker-compose.yml
```

### "Port 3000 already in use"
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### "Bot not responding"
- Check your bot token in `backend/.env`
- Make sure bot polling terminal shows "Bot started polling..."
- Check bot username is correct

### "Frontend can't connect to backend"
- Make sure backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local`
- Check CORS settings in `backend/.env`

---

## 📚 Next Steps

Once everything is running:

1. **Test all bot commands:**
   - `/start` - Register
   - `/progress` - View today's progress
   - `/settings` - Toggle daily recap
   - Log water, carbs, exercise

2. **Test web dashboard:**
   - View progress
   - Configure goals
   - Update settings

3. **Check the scheduler:**
   - Daily recap runs at 00:05 SGT
   - Weekly recap runs Monday 00:10 SGT
   - You can manually trigger for testing

4. **Review the code:**
   - Backend: `backend/app/`
   - Frontend: `frontend/`
   - See `IMPLEMENTATION_PLAN.md` for architecture

---

## 🎉 You're All Set!

Your Telegram Health Tracker is now running locally. Enjoy! 🚀

For detailed documentation, see:
- `LOCAL_SETUP_GUIDE.md` - Complete setup guide
- `FINAL_COMPREHENSIVE_TEST_REPORT.md` - Test results
- `DETAILED_CODE_REVIEW.md` - Code review

