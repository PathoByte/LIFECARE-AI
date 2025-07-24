#!/bin/bash

# LifeCare AI Deployment Script
echo "🏥 LifeCare AI - Deployment Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Docker and Docker Compose are installed"

# Create necessary directories
print_info "Creating necessary directories..."
mkdir -p data models logs
print_status "Directories created"

# Build and start services
print_info "Building and starting LifeCare AI services..."
docker-compose down --remove-orphans
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
print_info "Waiting for services to start..."
sleep 30

# Check if backend is healthy
print_info "Checking backend health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "Backend is healthy"
else
    print_error "Backend health check failed"
    docker-compose logs backend
    exit 1
fi

# Check if frontend is accessible
print_info "Checking frontend accessibility..."
if curl -f http://localhost:3000/health > /dev/null 2>&1; then
    print_status "Frontend is accessible"
else
    print_warning "Frontend health check failed, but this might be normal"
fi

# Display deployment information
echo ""
echo "🎉 LifeCare AI Deployment Complete!"
echo "=================================="
echo ""
echo "📋 Access Information:"
echo "🌐 Frontend:     http://localhost:3000"
echo "🔗 Backend API:  http://localhost:8000"
echo "📖 API Docs:     http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/health"
echo ""
echo "📊 Container Status:"
docker-compose ps
echo ""
echo "📝 Demo Credentials:"
echo "   Username: demo_user"
echo "   Password: any_password"
echo ""
echo "🔧 Management Commands:"
echo "   Stop services:    docker-compose down"
echo "   View logs:        docker-compose logs -f"
echo "   Restart:          docker-compose restart"
echo "   Update:           ./deploy.sh"
echo ""
print_status "LifeCare AI is now running in production mode!"

# Optional: Open browser
if command -v xdg-open &> /dev/null; then
    print_info "Opening LifeCare AI in browser..."
    xdg-open http://localhost:3000
elif command -v open &> /dev/null; then
    print_info "Opening LifeCare AI in browser..."
    open http://localhost:3000
fi