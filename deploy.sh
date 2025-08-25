#!/bin/bash

# Mnemosyne Protocol - Production Deployment Script
# Usage: ./deploy.sh [setup|deploy|update|ssl|backup|logs|stop]

set -e

COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking deployment requirements..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available. Please install Docker Compose v2."
        exit 1
    fi
    
    # Check if .env.prod exists
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error "Production environment file $ENV_FILE not found."
        log_info "Please copy .env.prod template and configure it:"
        log_info "cp .env.prod.example .env.prod && nano .env.prod"
        exit 1
    fi
    
    # Check if domain is configured
    if grep -q "your-domain.com" "$ENV_FILE"; then
        log_warning "Domain still set to 'your-domain.com' in $ENV_FILE"
        log_warning "Please configure your actual domain before deploying"
    fi
    
    # Check if default passwords are still used
    if grep -q "CHANGE_THIS" "$ENV_FILE"; then
        log_error "Default passwords detected in $ENV_FILE"
        log_error "Please change all CHANGE_THIS values to secure passwords"
        exit 1
    fi
    
    log_success "Requirements check passed"
}

setup_directories() {
    log_info "Setting up deployment directories..."
    
    mkdir -p nginx/logs
    mkdir -p ssl
    mkdir -p backups
    
    # Create nginx directory structure for certbot
    mkdir -p nginx/www/certbot
    
    log_success "Directories created"
}

generate_secrets() {
    log_info "Generating secure secrets..."
    
    # Generate secrets if they don't exist
    if [[ ! -f ".secrets" ]]; then
        echo "# Generated secrets - keep this file secure!" > .secrets
        echo "SECRET_KEY=$(openssl rand -hex 32)" >> .secrets
        echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .secrets  
        echo "ENCRYPTION_KEY=$(openssl rand -hex 32)" >> .secrets
        
        log_success "Secrets generated in .secrets file"
        log_warning "Please add these to your $ENV_FILE"
        cat .secrets
    else
        log_info "Secrets file already exists"
    fi
}

deploy() {
    log_info "Starting production deployment..."
    
    check_requirements
    setup_directories
    
    # Build and start services
    log_info "Building and starting services..."
    docker compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d --build
    
    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 30
    
    # Run database migrations
    log_info "Running database migrations..."
    docker compose -f $COMPOSE_FILE exec backend alembic upgrade head
    
    # Check if services are healthy
    log_info "Checking service health..."
    docker compose -f $COMPOSE_FILE ps
    
    log_success "Deployment completed!"
    log_info "Your Mnemosyne instance should be available at https://$(grep DOMAIN $ENV_FILE | cut -d'=' -f2)"
}

setup_ssl() {
    log_info "Setting up SSL certificates..."
    
    # Get domain from env file
    DOMAIN=$(grep DOMAIN $ENV_FILE | cut -d'=' -f2)
    
    if [[ "$DOMAIN" == "your-domain.com" ]]; then
        log_error "Please configure your domain in $ENV_FILE first"
        exit 1
    fi
    
    # Initial certificate request
    docker compose -f $COMPOSE_FILE run --rm certbot
    
    # Set up certificate renewal
    echo "0 12 * * * cd $(pwd) && docker compose -f $COMPOSE_FILE run --rm certbot renew --quiet" | crontab -
    
    log_success "SSL certificates configured"
    log_info "Certificate auto-renewal scheduled"
}

update() {
    log_info "Updating Mnemosyne deployment..."
    
    # Pull latest images and rebuild
    docker compose -f $COMPOSE_FILE --env-file $ENV_FILE pull
    docker compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d --build
    
    # Run any new migrations
    docker compose -f $COMPOSE_FILE exec backend alembic upgrade head
    
    log_success "Update completed"
}

backup() {
    log_info "Creating backup..."
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    docker compose -f $COMPOSE_FILE exec postgres pg_dump -U postgres mnemosyne > "$BACKUP_DIR/database.sql"
    
    # Backup volumes
    docker run --rm -v mnemosyne_postgres_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .
    docker run --rm -v mnemosyne_qdrant_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/qdrant_data.tar.gz -C /data .
    
    # Backup SSL certificates
    if [[ -d "ssl" ]]; then
        tar czf "$BACKUP_DIR/ssl_certs.tar.gz" ssl/
    fi
    
    log_success "Backup created in $BACKUP_DIR"
}

show_logs() {
    SERVICE=${2:-}
    if [[ -n "$SERVICE" ]]; then
        docker compose -f $COMPOSE_FILE logs -f "$SERVICE"
    else
        docker compose -f $COMPOSE_FILE logs -f
    fi
}

stop() {
    log_info "Stopping Mnemosyne services..."
    docker compose -f $COMPOSE_FILE down
    log_success "Services stopped"
}

show_status() {
    log_info "Service Status:"
    docker compose -f $COMPOSE_FILE ps
    
    log_info "\nResource Usage:"
    docker compose -f $COMPOSE_FILE exec backend df -h
    
    log_info "\nRecent Logs:"
    docker compose -f $COMPOSE_FILE logs --tail=10
}

# Main command handling
case "${1:-deploy}" in
    "setup")
        check_requirements
        setup_directories
        generate_secrets
        ;;
    "deploy")
        deploy
        ;;
    "ssl")
        setup_ssl
        ;;
    "update")
        update
        ;;
    "backup")
        backup
        ;;
    "logs")
        show_logs "$@"
        ;;
    "stop")
        stop
        ;;
    "status")
        show_status
        ;;
    *)
        echo "Usage: $0 {setup|deploy|ssl|update|backup|logs [service]|stop|status}"
        echo ""
        echo "Commands:"
        echo "  setup   - Check requirements and setup directories"
        echo "  deploy  - Full production deployment"
        echo "  ssl     - Setup SSL certificates with Let's Encrypt"
        echo "  update  - Update deployment with latest changes"
        echo "  backup  - Create full system backup"
        echo "  logs    - Show service logs (optionally specify service)"
        echo "  stop    - Stop all services"
        echo "  status  - Show service status and resource usage"
        ;;
esac