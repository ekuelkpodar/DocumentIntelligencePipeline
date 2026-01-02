#!/bin/bash
set -e

echo "🚀 Document Intelligence Pipeline - Quick Start"
echo "=============================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your ANTHROPIC_API_KEY before continuing"
    echo "   Open .env in your editor and set ANTHROPIC_API_KEY=your-key-here"
    echo ""
    read -p "Press Enter after you've added your API key..."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "🐳 Starting infrastructure services..."
docker-compose up -d postgres redis minio minio-setup

echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "📦 Poetry is not installed. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "📦 Installing Python dependencies..."
poetry install

echo "🗄️  Running database migrations..."
poetry run alembic upgrade head

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Next steps:"
echo ""
echo "1. Start the API server (in one terminal):"
echo "   poetry run uvicorn src.main:app --reload"
echo ""
echo "2. Start the worker (in another terminal):"
echo "   poetry run arq src.queue.worker.WorkerSettings"
echo ""
echo "3. Access the services:"
echo "   - API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - MinIO Console: http://localhost:9001 (minioadmin/minioadmin)"
echo ""
echo "4. Read the guides:"
echo "   - README.md - Project overview"
echo "   - IMPLEMENTATION_GUIDE.md - Development guide"
echo "   - PROJECT_STATUS.md - Current status"
echo ""
echo "Happy coding! 🎉"
