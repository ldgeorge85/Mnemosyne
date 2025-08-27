# Mnemosyne Protocol - Production Deployment Guide
*Last Updated: August 27, 2025*

This guide will walk you through deploying Mnemosyne Protocol to production with SSL, security, and monitoring.

## Current Features Available in Production
- ✅ **Agentic Chat**: ReAct pattern with 92% confidence persona selection
- ✅ **Task Management**: Full CRUD with LIST_TASKS action
- ✅ **Memory System**: Vector embeddings and semantic search
- ✅ **5 Persona Modes**: Confidant, Mentor, Mediator, Guardian, Mirror
- ✅ **Token Management**: 64k context window support
- ✅ **Receipt Generation**: Full transparency for all actions

## Prerequisites

### Server Requirements
- **OS**: Ubuntu 20.04+ or similar Linux distribution
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Storage**: 50GB+ SSD storage
- **CPU**: 2+ cores
- **Network**: Static IP address with ports 80, 443 accessible

### Software Requirements
- Docker 20.10+
- Docker Compose v2
- Domain name pointing to your server
- SSL email for Let's Encrypt certificates

### API Keys Required
- OpenAI API key (for LLM and embeddings)
- Optional: Anthropic API key for Claude models

## Quick Start

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose v2 (if not included)
sudo apt install docker-compose-plugin
```

### 2. Clone and Configure

```bash
# Clone repository
git clone https://github.com/ldgeorge85/Mnemosyne.git
cd Mnemosyne

# Copy production environment template
cp .env.prod .env.prod

# Edit configuration (see Configuration section below)
nano .env.prod
```

### 3. Configure Environment

Edit `.env.prod` with your settings:

```bash
# Domain and SSL
DOMAIN=your-actual-domain.com
SSL_EMAIL=your-email@domain.com

# Generate strong passwords
POSTGRES_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)

# Add your API keys
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# Optional: Anthropic
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 4. Deploy

```bash
# Full deployment with SSL
./deploy.sh deploy

# Setup SSL certificates (after deployment)
./deploy.sh ssl
```

Your Mnemosyne instance will be available at `https://your-domain.com`!

## Detailed Configuration

### Environment Variables

#### Core Settings
- `DOMAIN`: Your domain name (e.g., `mnemosyne.yourdomain.com`)
- `SSL_EMAIL`: Email for Let's Encrypt certificates
- `MODE`: Set to `personal` for single-user instance

#### Security Keys (Generate Unique Values!)
```bash
# Generate secure keys
openssl rand -hex 32  # For SECRET_KEY and JWT_SECRET_KEY
openssl rand -hex 32  # For ENCRYPTION_KEY
openssl rand -base64 32  # For POSTGRES_PASSWORD
```

#### LLM Configuration
```bash
# OpenAI (Required)
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# Alternative: Local or compatible API
OPENAI_BASE_URL=http://your-local-llm:8000/v1
OPENAI_MODEL=your-model-name

# Embeddings
MEMORY_EMBEDDING_MODEL=text-embedding-ada-002
MEMORY_VECTOR_DIMENSIONS=1536
```

### DNS Configuration

Point your domain to your server:

```bash
# A record
your-domain.com → YOUR_SERVER_IP

# Optional: www subdomain
www.your-domain.com → YOUR_SERVER_IP
```

## Deployment Commands

### Initial Setup
```bash
# Check requirements and setup directories
./deploy.sh setup

# Full deployment
./deploy.sh deploy

# Setup SSL certificates
./deploy.sh ssl
```

### Maintenance
```bash
# Update to latest version
./deploy.sh update

# Create backup
./deploy.sh backup

# View logs
./deploy.sh logs
./deploy.sh logs backend  # specific service

# Check status
./deploy.sh status

# Stop services
./deploy.sh stop
```

## Architecture

### Services
- **Frontend**: React app served via Nginx
- **Backend**: FastAPI Python application
- **PostgreSQL**: Primary database with pgvector
- **Redis**: Caching and session storage
- **Qdrant**: Vector database for embeddings
- **Nginx**: Reverse proxy with SSL termination

### Network Security
- Internal Docker network for service communication
- Only Nginx exposed to internet (ports 80, 443)
- Rate limiting on API endpoints
- Security headers configured

### Data Persistence
- PostgreSQL data in `postgres_data` volume
- Qdrant vectors in `qdrant_data` volume
- Redis persistence in `redis_data` volume
- Application logs in `backend_logs` volume

## SSL Certificates

### Automatic Setup (Recommended)
```bash
# After deployment, setup SSL
./deploy.sh ssl
```

This will:
- Request certificates from Let's Encrypt
- Configure automatic renewal (cron job)
- Update Nginx configuration

### Manual Setup
If automatic setup fails, configure manually:

```bash
# Request certificate manually
docker compose -f docker-compose.prod.yml run --rm \
    certbot certonly --webroot \
    -w /var/www/certbot \
    --email your-email@domain.com \
    --agree-tos --no-eff-email \
    -d your-domain.com
```

## Monitoring and Logs

### Health Checks
- **Application**: `https://your-domain.com/health`
- **API**: `https://your-domain.com/api/v1/health`
- **Individual services**: `docker compose -f docker-compose.prod.yml ps`

### Log Locations
- **Application logs**: `docker compose logs backend`
- **Nginx logs**: `nginx/logs/` directory
- **SSL logs**: `ssl/` directory

### Monitoring
```bash
# Service status
./deploy.sh status

# Real-time logs
./deploy.sh logs

# Resource usage
docker compose -f docker-compose.prod.yml exec backend df -h
docker stats
```

## Backup and Recovery

### Creating Backups
```bash
# Full system backup
./deploy.sh backup
```

Backup includes:
- Database dump
- Vector database data
- SSL certificates
- Application data

### Restore from Backup
```bash
# Restore database
docker compose -f docker-compose.prod.yml exec postgres \
    psql -U postgres -d mnemosyne < backups/YYYYMMDD_HHMMSS/database.sql

# Restore volumes
docker run --rm -v mnemosyne_postgres_data:/data \
    -v $(pwd)/backups/YYYYMMDD_HHMMSS:/backup alpine \
    tar xzf /backup/postgres_data.tar.gz -C /data

# Restart services
./deploy.sh update
```

## Security Considerations

### Server Security
- Use SSH key authentication (disable password auth)
- Configure firewall (UFW):
  ```bash
  sudo ufw allow 22/tcp   # SSH
  sudo ufw allow 80/tcp   # HTTP
  sudo ufw allow 443/tcp  # HTTPS
  sudo ufw enable
  ```
- Keep system updated: `sudo apt update && sudo apt upgrade`
- Monitor failed login attempts

### Application Security
- Generate unique, strong secrets for all keys
- Use HTTPS everywhere (no HTTP access)
- Rate limiting configured on API endpoints
- Security headers configured in Nginx
- Regular security updates via `./deploy.sh update`

### Data Security
- Database passwords generated randomly
- All data encrypted at rest
- User data never leaves your server
- Model API keys stored securely in environment

## Troubleshooting

### Common Issues

#### SSL Certificate Issues
```bash
# Check certificate status
./deploy.sh logs certbot

# Manual certificate renewal
docker compose -f docker-compose.prod.yml run --rm certbot renew
```

#### Service Won't Start
```bash
# Check service logs
./deploy.sh logs SERVICE_NAME

# Check resource usage
docker system df
docker stats

# Restart specific service
docker compose -f docker-compose.prod.yml restart SERVICE_NAME
```

#### Database Connection Issues
```bash
# Check database logs
./deploy.sh logs postgres

# Test database connection
docker compose -f docker-compose.prod.yml exec postgres \
    psql -U postgres -d mnemosyne -c "SELECT version();"
```

#### High Memory Usage
- Reduce worker count in `.env.prod`: `WORKERS=2`
- Increase swap space
- Monitor with: `docker stats`

### Getting Help
- Check logs: `./deploy.sh logs`
- Verify configuration: `./deploy.sh status`
- Review environment file: `cat .env.prod`
- Check service health: `docker compose -f docker-compose.prod.yml ps`

## Scaling and Performance

### Single Server Optimization
- Increase worker count: `WORKERS=4` (based on CPU cores)
- Tune database connections: `MAX_CONNECTIONS=100`
- Monitor resource usage and adjust

### Multi-Server Setup (Future)
- Database on separate server
- Load balancer for multiple app servers
- Shared storage for volumes
- Redis cluster for sessions

## Updates and Maintenance

### Regular Maintenance
- **Weekly**: Check logs and system resources
- **Monthly**: Create backups, update dependencies
- **Quarterly**: Review security configuration

### Version Updates
```bash
# Pull latest code
git pull origin main

# Update deployment
./deploy.sh update
```

### Security Updates
- Monitor Docker image security advisories
- Update base images regularly
- Keep host system updated

---

## Quick Reference

### Essential Commands
```bash
./deploy.sh deploy    # Initial deployment
./deploy.sh ssl       # Setup SSL
./deploy.sh backup    # Create backup
./deploy.sh logs      # View logs
./deploy.sh status    # Check health
./deploy.sh update    # Update system
```

### URLs
- **Application**: `https://your-domain.com`
- **Health Check**: `https://your-domain.com/health`
- **API Health**: `https://your-domain.com/api/v1/health`

### File Locations
- **Config**: `.env.prod`
- **Logs**: `nginx/logs/`
- **Backups**: `backups/`
- **SSL**: `ssl/`

---

*Your Mnemosyne Protocol instance is now ready for production use with enterprise-grade security, monitoring, and backup capabilities.*