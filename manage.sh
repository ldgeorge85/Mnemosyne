#!/bin/bash
# Mnemosyne Management Script
# This script provides convenient commands for managing the Mnemosyne application

# Set script to exit on error
set -e

# Load environment variables
if [ -f .env ]; then
    source .env
fi

# Directories
DOCS_DIR="./docs"
BACKEND_DIR="./backend"
FRONTEND_DIR="./frontend"

# Function to display help message
function display_help {
    echo "Mnemosyne Management Script"
    echo "Usage: ./manage.sh [command]"
    echo ""
    echo "Development Commands:"
    echo "  start                Start all services in development mode"
    echo "  stop                 Stop all services"
    echo "  restart              Restart all services"
    echo "  status               Show status of all services"
    echo "  logs [service]       View logs for all or a specific service"
    echo "  build                Rebuild all services"
    echo "  clean                Remove all containers, volumes, and networks"
    echo ""
    echo "Database Commands:"
    echo "  db-shell              Access PostgreSQL shell"
    echo "  db-migrate            Run database migrations"
    echo "  db-reset              Reset the database (CAUTION: Destroys all data)"
    echo ""
    echo "Testing Commands:"
    echo "  test                  Run all tests"
    echo "  test-backend          Run backend tests"
    echo "  test-frontend         Run frontend tests"
    echo "  test-coverage         Run tests with coverage reports"
    echo ""
    echo "Quality Commands:"
    echo "  lint                  Run all linters"
    echo "  lint-backend          Run backend linters"
    echo "  lint-frontend         Run frontend linters"
    echo "  format                Format all code"
    echo "  format-backend        Format backend code"
    echo "  format-frontend       Format frontend code"
    echo ""
    echo "Utility Commands:"
    echo "  shell [service]       Open a shell in a service container"
    echo "  exec [service] [cmd]  Run a command in a service container"
    echo "  dev-tools [cmd]       Run a command in the dev-tools container"
    echo "  update-docs           Update documentation from codebase"
    echo ""
    echo "Deployment Commands:"
    echo "  prod                  Start services in production mode"
    echo "  help                  Display this help message"
}

# Check if Docker is running
function check_docker {
    if ! docker info > /dev/null 2>&1; then
        echo "Error: Docker is not running or not accessible"
        exit 1
    fi
}

# Check if a service is running
function check_service_running {
    local service_name=$1
    local running=$(docker compose ps --services --filter "status=running" | grep -w "$service_name" || true)
    if [ -z "$running" ]; then
        echo "Error: Service '$service_name' is not running"
        echo "Start the services first with: ./manage.sh start"
        exit 1
    fi
}

# Main command handling
case "$1" in
    start)
        check_docker
        echo "Starting Mnemosyne services in development mode..."
        docker compose up -d
        echo "Services started. Access the application at:"
        echo "  - Frontend: http://localhost:3000"
        echo "  - Backend API: http://localhost:8000"
        echo "  - API Documentation: http://localhost:8000/docs"
        ;;
    stop)
        check_docker
        echo "Stopping Mnemosyne services..."
        docker compose down
        ;;
    restart)
        check_docker
        echo "Restarting Mnemosyne services..."
        docker compose down
        docker compose up -d
        ;;
    status)
        check_docker
        echo "Mnemosyne services status:"
        docker compose ps
        ;;
    logs)
        check_docker
        if [ -z "$2" ]; then
            docker compose logs -f
        else
            docker compose logs -f "$2"
        fi
        ;;
    build)
        check_docker
        echo "Rebuilding Mnemosyne services..."
        docker compose build
        docker compose -f docker-compose.dev-tools.yml build
        ;;
    clean)
        check_docker
        echo "Removing all containers, volumes, and networks..."
        docker compose down -v
        docker compose -f docker-compose.dev-tools.yml down -v
        echo "Cleanup completed"
        ;;
    db-shell)
        check_docker
        check_service_running "postgres"
        echo "Accessing PostgreSQL shell..."
        docker compose exec postgres psql -U ${DB_USERNAME:-postgres} -d ${DB_DATABASE:-mnemosyne}
        ;;
    db-migrate)
        check_docker
        check_service_running "backend"
        echo "Running database migrations..."
        docker compose exec backend alembic upgrade head
        ;;
    db-reset)
        check_docker
        check_service_running "postgres"
        echo "CAUTION: This will destroy all data in the database."
        read -p "Are you sure you want to continue? (y/n): " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            echo "Resetting database..."
            docker compose exec postgres psql -U ${DB_USERNAME:-postgres} -c "DROP DATABASE IF EXISTS ${DB_DATABASE:-mnemosyne};"
            docker compose exec postgres psql -U ${DB_USERNAME:-postgres} -c "CREATE DATABASE ${DB_DATABASE:-mnemosyne};"
            echo "Database reset complete. Remember to run migrations."
        else
            echo "Database reset cancelled."
        fi
        ;;
    test)
        check_docker
        echo "Running all tests..."
        docker compose -f docker-compose.dev-tools.yml run backend-test
        docker compose -f docker-compose.dev-tools.yml run frontend-test
        ;;
    test-backend)
        check_docker
        echo "Running backend tests..."
        docker compose -f docker-compose.dev-tools.yml run backend-test
        ;;
    test-frontend)
        check_docker
        echo "Running frontend tests..."
        docker compose -f docker-compose.dev-tools.yml run frontend-test
        ;;
    test-coverage)
        check_docker
        echo "Running tests with coverage reports..."
        docker compose -f docker-compose.dev-tools.yml run backend-test pytest --cov=app --cov-report=term --cov-report=html:coverage
        docker compose -f docker-compose.dev-tools.yml run frontend-test npm test -- --coverage
        echo "Coverage reports generated in backend/coverage and frontend/coverage"
        ;;
    lint)
        check_docker
        echo "Running all linters..."
        docker compose -f docker-compose.dev-tools.yml run backend-lint
        docker compose -f docker-compose.dev-tools.yml run frontend-lint
        ;;
    lint-backend)
        check_docker
        echo "Running backend linters..."
        docker compose -f docker-compose.dev-tools.yml run backend-lint
        ;;
    lint-frontend)
        check_docker
        echo "Running frontend linters..."
        docker compose -f docker-compose.dev-tools.yml run frontend-lint
        ;;
    format)
        check_docker
        echo "Formatting all code..."
        docker compose -f docker-compose.dev-tools.yml run dev-tools bash -c "cd backend && black . && isort . && cd ../frontend && prettier --write ."
        ;;
    format-backend)
        check_docker
        echo "Formatting backend code..."
        docker compose -f docker-compose.dev-tools.yml run dev-tools bash -c "cd backend && black . && isort ."
        ;;
    format-frontend)
        check_docker
        echo "Formatting frontend code..."
        docker compose -f docker-compose.dev-tools.yml run dev-tools bash -c "cd frontend && prettier --write ."
        ;;
    shell)
        check_docker
        if [ -z "$2" ]; then
            echo "Error: Service name is required"
            echo "Usage: ./manage.sh shell [service]"
            exit 1
        fi
        check_service_running "$2"
        echo "Opening shell in $2 container..."
        docker compose exec "$2" bash || docker compose exec "$2" sh
        ;;
    exec)
        check_docker
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "Error: Service name and command are required"
            echo "Usage: ./manage.sh exec [service] [command]"
            exit 1
        fi
        check_service_running "$2"
        shift 2
        echo "Executing command in service $1..."
        docker compose exec "$1" "$@"
        ;;
    dev-tools)
        check_docker
        shift
        if [ -z "$1" ]; then
            echo "Opening shell in dev-tools container..."
            docker compose -f docker-compose.dev-tools.yml run dev-tools
        else
            echo "Running command in dev-tools container..."
            docker compose -f docker-compose.dev-tools.yml run dev-tools "$@"
        fi
        ;;
    update-docs)
        check_docker
        echo "Updating API documentation..."
        docker compose exec backend python -c "from app.main import app; import json; print(json.dumps(app.openapi()))" > "$DOCS_DIR/api/openapi.json"
        echo "Documentation updated"
        ;;
    prod)
        check_docker
        echo "Starting Mnemosyne services in production mode..."
        docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
        ;;
    help|*)
        display_help
        ;;
esac
