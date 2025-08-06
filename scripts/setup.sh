#!/bin/bash

# Mnemosyne Protocol - Setup Script

set -e

echo "🧠 Mnemosyne Protocol Setup"
echo "=========================="

# Check for required tools
echo "Checking dependencies..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

echo "✅ All dependencies found"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your API keys"
fi

# Create data directories
echo "Creating data directories..."
mkdir -p data/memories data/shadow data/dialogues data/collective

# Install Python dependencies for local development
echo "Installing Python dependencies..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Initialize database
echo "Initializing database..."
docker-compose up -d postgres redis
sleep 5  # Wait for postgres to start

# Run migrations
echo "Running database migrations..."
docker-compose run --rm backend alembic upgrade head

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: docker-compose up"
echo "3. Access the application at http://localhost:3000"
echo ""
echo "For development:"
echo "- Backend API: http://localhost:8000"
echo "- Shadow API: http://localhost:8001"  
echo "- Collective API: http://localhost:8003"
echo "- Frontend: http://localhost:3000"