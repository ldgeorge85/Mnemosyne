#!/bin/bash

# Test production configuration setup

echo "=== Mnemosyne Production Configuration Test ==="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "${GREEN}✅ PASS${NC}: $1"; }
fail() { echo -e "${RED}❌ FAIL${NC}: $1"; }
warn() { echo -e "${YELLOW}⚠️  WARN${NC}: $1"; }

echo "Testing production deployment setup..."
echo ""

# Check if required files exist
if [[ -f "docker-compose.prod.yml" ]]; then
    pass "Production docker-compose file exists"
else
    fail "docker-compose.prod.yml missing"
    exit 1
fi

if [[ -f ".env.prod" ]]; then
    pass "Production environment file exists"
else
    fail ".env.prod missing"
    exit 1
fi

if [[ -f "nginx/prod.conf" ]]; then
    pass "Nginx production config exists"
else
    fail "nginx/prod.conf missing"
    exit 1
fi

if [[ -f "deploy.sh" ]] && [[ -x "deploy.sh" ]]; then
    pass "Deployment script exists and is executable"
else
    fail "deploy.sh missing or not executable"
    exit 1
fi

# Test environment file
echo ""
echo "Checking .env.prod configuration..."

if grep -q "your-domain.com" .env.prod; then
    warn "Domain still set to 'your-domain.com' - needs configuration"
else
    pass "Domain appears to be configured"
fi

if grep -q "CHANGE_THIS" .env.prod; then
    fail "Default passwords still in use - SECURITY RISK"
    echo "     Run: ./deploy.sh setup to generate secure passwords"
else
    pass "No default passwords detected"
fi

if grep -q "your-openai-api-key" .env.prod; then
    warn "OpenAI API key not configured"
else
    pass "OpenAI API key appears configured"
fi

# Test Docker setup
echo ""
echo "Checking Docker setup..."

if command -v docker &> /dev/null; then
    pass "Docker is installed"
    docker --version
else
    fail "Docker not installed"
    exit 1
fi

if docker compose version &> /dev/null; then
    pass "Docker Compose v2 available"
    docker compose version
else
    fail "Docker Compose v2 not available"
    exit 1
fi

# Test configuration syntax
echo ""
echo "Validating configuration syntax..."

if docker compose -f docker-compose.prod.yml config &> /dev/null; then
    pass "Docker Compose configuration is valid"
else
    fail "Docker Compose configuration has errors"
    echo "Run: docker compose -f docker-compose.prod.yml config"
    exit 1
fi

# Check network connectivity requirements
echo ""
echo "Checking deployment requirements..."

if [[ -d "nginx" ]]; then
    pass "Nginx directory exists"
else
    warn "Nginx directory missing - will be created during deployment"
fi

if [[ -d "ssl" ]]; then
    pass "SSL directory exists"
else
    warn "SSL directory missing - will be created during deployment"
fi

echo ""
echo "=== Test Summary ==="
echo ""
echo "Configuration test completed. Next steps:"
echo ""
echo "1. Configure your domain in .env.prod:"
echo "   DOMAIN=your-actual-domain.com"
echo ""
echo "2. Add your API keys to .env.prod:"
echo "   OPENAI_API_KEY=sk-your-actual-key"
echo ""
echo "3. Generate secure passwords:"
echo "   ./deploy.sh setup"
echo ""
echo "4. Deploy to production:"
echo "   ./deploy.sh deploy"
echo ""
echo "5. Setup SSL certificates:"
echo "   ./deploy.sh ssl"
echo ""
echo "For full deployment guide, see: docs/DEPLOYMENT_GUIDE.md"