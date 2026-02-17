#!/bin/bash

# 🚀 ZenBot POC - Automated Setup Script

set -e

echo "🤖 ZenBot POC Setup Starting..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Warning: .env file not found${NC}"
    echo "Creating .env from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}Please edit .env and add your API keys before continuing${NC}"
        exit 1
    else
        echo "GEMINI_API_KEY=your_key_here" > .env
        echo "LANGSMITH_API_KEY=your_key_here" >> .env
        echo "LANGSMITH_PROJECT=Zen_Project" >> .env
        echo -e "${YELLOW}Created .env file. Please edit it with your API keys.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ .env file found${NC}"
echo ""

# Check Python
echo -e "${BLUE}Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 not found. Please install Python 3.10+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"
echo ""

# Check Node.js
echo -e "${BLUE}Checking Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✅ Node.js $NODE_VERSION${NC}"
echo ""

# Setup Backend
echo -e "${BLUE}📦 Setting up Backend...${NC}"
cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "Installing Python dependencies..."
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Backend dependencies installed${NC}"
cd ..
echo ""

# Setup Frontend
echo -e "${BLUE}📦 Setting up Frontend...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
else
    echo -e "${GREEN}✅ node_modules already exists${NC}"
fi
cd ..
echo ""

# Instructions
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          🎉 Setup Complete! Ready to Start! 🎉             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo -e "${YELLOW}Option 1: Manual Start (2 terminals)${NC}"
echo ""
echo "  Terminal 1 - Backend:"
echo "  $ cd backend"
echo "  $ source venv/bin/activate"
echo "  $ python main.py"
echo ""
echo "  Terminal 2 - Frontend:"
echo "  $ cd frontend"
echo "  $ npm run dev"
echo ""
echo -e "${YELLOW}Option 2: Docker Compose (1 command)${NC}"
echo ""
echo "  $ docker-compose --profile web up --build"
echo ""
echo -e "${GREEN}Then open: http://localhost:3000${NC}"
echo ""
echo -e "${BLUE}To start now, would you like to:${NC}"
echo "  1) Start backend in this terminal"
echo "  2) See full instructions again"
echo "  3) Exit"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}Starting backend...${NC}"
        echo -e "${YELLOW}Open a new terminal and run:${NC}"
        echo "  cd frontend && npm run dev"
        echo ""
        cd backend
        source venv/bin/activate
        python main.py
        ;;
    2)
        echo ""
        cat QUICKSTART.md
        ;;
    3)
        echo "Goodbye! 👋"
        exit 0
        ;;
    *)
        echo "Invalid choice. Run './setup-poc.sh' again."
        exit 1
        ;;
esac
