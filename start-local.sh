#!/bin/bash

# Telegram Health Tracker - Local Development Startup Script
# This script helps you start all services for local development

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Telegram Health Tracker - Local Development Setup        ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i :"$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command_exists docker; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    echo "  Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓ Docker is installed${NC}"

if ! command_exists poetry; then
    echo -e "${RED}✗ Poetry is not installed${NC}"
    echo ""
    echo -e "${YELLOW}Please install Poetry manually:${NC}"
    echo ""
    echo "  Option 1 - Using Homebrew (recommended for macOS):"
    echo "    brew install poetry"
    echo ""
    echo "  Option 2 - Using pip:"
    echo "    pip3 install poetry"
    echo ""
    echo "  Option 3 - Official installer (if you have Python 3.10+):"
    echo "    curl -sSL https://install.python-poetry.org | python3 -"
    echo ""
    echo "After installing, run this script again."
    exit 1
fi
echo -e "${GREEN}✓ Poetry is installed${NC}"

if ! command_exists node; then
    echo -e "${RED}✗ Node.js is not installed${NC}"
    echo "  Please install Node.js: https://nodejs.org/"
    exit 1
fi
echo -e "${GREEN}✓ Node.js is installed${NC}"

echo ""

# Check if .env files exist
echo -e "${YELLOW}Checking configuration files...${NC}"

if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠ backend/.env not found${NC}"
    echo "  Creating from .env.example..."
    cp backend/.env.example backend/.env
    echo -e "${RED}  ⚠ IMPORTANT: Edit backend/.env and add your TELEGRAM_BOT_TOKEN${NC}"
    echo -e "${RED}  Get your bot token from @BotFather on Telegram${NC}"
    read -p "Press Enter to continue after editing .env file..."
fi
echo -e "${GREEN}✓ backend/.env exists${NC}"

if [ ! -f "frontend/.env.local" ]; then
    echo -e "${YELLOW}⚠ frontend/.env.local not found${NC}"
    echo "  Creating from .env.example..."
    cp frontend/.env.example frontend/.env.local
    echo -e "${YELLOW}  You may need to edit frontend/.env.local with your bot username${NC}"
fi
echo -e "${GREEN}✓ frontend/.env.local exists${NC}"

echo ""

# Start Docker services
echo -e "${YELLOW}Starting Docker services (PostgreSQL & Redis)...${NC}"
cd backend
docker-compose up -d
cd ..

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 5

# Check if PostgreSQL is ready
until docker exec telebot_postgres pg_isready -U postgres >/dev/null 2>&1; do
    echo -e "${YELLOW}  Waiting for PostgreSQL...${NC}"
    sleep 2
done
echo -e "${GREEN}✓ PostgreSQL is ready${NC}"

# Check if Redis is ready
until docker exec telebot_redis redis-cli ping >/dev/null 2>&1; do
    echo -e "${YELLOW}  Waiting for Redis...${NC}"
    sleep 2
done
echo -e "${GREEN}✓ Redis is ready${NC}"

echo ""

# Install backend dependencies
echo -e "${YELLOW}Installing backend dependencies...${NC}"
cd backend
if [ ! -d ".venv" ]; then
    poetry install
else
    echo -e "${GREEN}✓ Backend dependencies already installed${NC}"
fi
cd ..

# Run database migrations
echo -e "${YELLOW}Running database migrations...${NC}"
cd backend
poetry run alembic upgrade head
cd ..
echo -e "${GREEN}✓ Database migrations complete${NC}"

echo ""

# Install frontend dependencies
echo -e "${YELLOW}Installing frontend dependencies...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
else
    echo -e "${GREEN}✓ Frontend dependencies already installed${NC}"
fi
cd ..

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Setup Complete! 🎉                         ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}To start the application, run these commands in separate terminals:${NC}"
echo ""
echo -e "${YELLOW}Terminal 1 - Backend API:${NC}"
echo "  cd backend && poetry run uvicorn app.main:app --reload"
echo ""
echo -e "${YELLOW}Terminal 2 - Telegram Bot:${NC}"
echo "  cd backend && poetry run python -m app.bot.polling"
echo ""
echo -e "${YELLOW}Terminal 3 - Frontend:${NC}"
echo "  cd frontend && npm run dev"
echo ""
echo -e "${BLUE}Then open your browser to:${NC}"
echo "  http://localhost:3000"
echo ""
echo -e "${BLUE}And test your bot on Telegram!${NC}"
echo ""
echo -e "${YELLOW}To stop Docker services:${NC}"
echo "  cd backend && docker-compose down"
echo ""

