# 🚢 LifeCare AI - Deployment Guide

This comprehensive guide covers all deployment options for LifeCare AI, from local development to production cloud deployment.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Local Development](#-local-development)
- [Docker Deployment](#-docker-deployment)
- [Cloud Deployment](#-cloud-deployment)
- [Production Configuration](#-production-configuration)
- [Monitoring & Maintenance](#-monitoring--maintenance)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Start

### Option 1: Instant Demo (No Dependencies)

Perfect for immediate testing and demonstration:

```bash
# Clone the repository
git clone <repository-url>
cd lifecare-ai

# Run the simple version
python run_simple.py
```

**What you get:**
- ✅ Fully functional backend API
- ✅ Interactive web interface
- ✅ AI-powered anomaly detection
- ✅ Real-time health monitoring
- ✅ No external dependencies required

### Option 2: One-Click Deployment

For production-ready deployment:

```bash
# Linux/Mac
./deploy.sh

# Windows
deploy.bat
```

---

## 💻 Local Development

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** for version control

### Backend Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize ML model
python init_model.py

# 4. Start development server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm start
```

### Development URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🐳 Docker Deployment

### Single Container Deployment

```bash
# Build the image
docker build -t lifecare-ai .

# Run the container
docker run -d \
  --name lifecare-ai \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  lifecare-ai
```

### Multi-Container Deployment (Recommended)

```bash
# Using Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Compose Configuration

The `docker-compose.yml` includes:

- **Backend Service**: FastAPI application with ML models
- **Frontend Service**: React application with Nginx
- **Database**: PostgreSQL (optional, SQLite by default)
- **Redis**: Caching and session storage (optional)

### Container Health Checks

```bash
# Check container health
docker-compose ps

# View health check logs
docker inspect --format='{{json .State.Health}}' lifecare-backend
```

---

## ☁️ Cloud Deployment

### AWS Deployment

#### Option 1: AWS ECS with Fargate

```bash
# 1. Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker build -t lifecare-ai .
docker tag lifecare-ai:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/lifecare-ai:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/lifecare-ai:latest

# 2. Create ECS cluster
aws ecs create-cluster --cluster-name lifecare-ai-cluster

# 3. Create task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# 4. Create service
aws ecs create-service \
  --cluster lifecare-ai-cluster \
  --service-name lifecare-ai-service \
  --task-definition lifecare-ai:1 \
  --desired-count 2
```

#### Option 2: AWS Lambda (Serverless)

```bash
# Install Serverless Framework
npm install -g serverless

# Deploy to Lambda
serverless deploy --stage prod
```

### Google Cloud Platform

#### Cloud Run Deployment

```bash
# 1. Build and deploy
gcloud run deploy lifecare-ai \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# 2. Set environment variables
gcloud run services update lifecare-ai \
  --set-env-vars DATABASE_URL=postgresql://... \
  --region us-central1
```

#### GKE Deployment

```bash
# 1. Create GKE cluster
gcloud container clusters create lifecare-ai-cluster \
  --num-nodes=3 \
  --zone=us-central1-a

# 2. Deploy application
kubectl apply -f k8s/
```

### Microsoft Azure

#### Azure Container Instances

```bash
# Create resource group
az group create --name lifecare-ai-rg --location eastus

# Deploy container
az container create \
  --resource-group lifecare-ai-rg \
  --name lifecare-ai \
  --image lifecare-ai:latest \
  --ports 8000 \
  --dns-name-label lifecare-ai-demo
```

#### Azure App Service

```bash
# Create App Service plan
az appservice plan create \
  --name lifecare-ai-plan \
  --resource-group lifecare-ai-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group lifecare-ai-rg \
  --plan lifecare-ai-plan \
  --name lifecare-ai-app \
  --deployment-container-image-name lifecare-ai:latest
```

---

## 🔧 Production Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@host:5432/lifecare
REDIS_URL=redis://host:6379/0

# Security
SECRET_KEY=your-super-secret-production-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=LifeCare AI Production
BACKEND_CORS_ORIGINS=["https://your-domain.com","https://api.your-domain.com"]

# ML Configuration
MODEL_PATH=models/anomaly_model.pkl
ENABLE_ML_CACHE=true

# Monitoring
ENABLE_METRICS=true
LOG_LEVEL=INFO
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### Database Setup

#### PostgreSQL (Recommended for Production)

```bash
# 1. Install PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib

# 2. Create database and user
sudo -u postgres psql
CREATE DATABASE lifecare;
CREATE USER lifecare_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE lifecare TO lifecare_user;

# 3. Update environment variables
export DATABASE_URL=postgresql://lifecare_user:secure_password@localhost:5432/lifecare
```

#### Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### SSL/TLS Configuration

#### Using Let's Encrypt with Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Load Balancing

#### Nginx Load Balancer

```nginx
upstream lifecare_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://lifecare_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Application health
curl -f http://localhost:8000/health

# Detailed health check
curl -f http://localhost:8000/health/detailed

# Database connectivity
curl -f http://localhost:8000/health/db
```

### Metrics Collection

#### Prometheus Integration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'lifecare-ai'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: /metrics
```

#### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "LifeCare AI Monitoring",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "http_request_duration_seconds_bucket"
          }
        ]
      }
    ]
  }
}
```

### Logging

#### Centralized Logging with ELK Stack

```yaml
# docker-compose.logging.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.14.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:7.14.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: docker.elastic.co/kibana/kibana:7.14.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

### Backup Strategy

#### Database Backup

```bash
# PostgreSQL backup
pg_dump -h localhost -U lifecare_user lifecare > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U lifecare_user lifecare | gzip > $BACKUP_DIR/lifecare_$DATE.sql.gz

# Keep only last 7 days of backups
find $BACKUP_DIR -name "lifecare_*.sql.gz" -mtime +7 -delete
```

#### ML Model Backup

```bash
# Backup ML models
tar -czf models_backup_$(date +%Y%m%d).tar.gz models/

# Upload to cloud storage (AWS S3 example)
aws s3 cp models_backup_$(date +%Y%m%d).tar.gz s3://lifecare-backups/models/
```

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Backend Won't Start

**Symptoms:**
- Server fails to start
- Port already in use errors
- Import errors

**Solutions:**
```bash
# Check if port is in use
netstat -tulpn | grep :8000
lsof -i :8000

# Kill process using port
kill -9 $(lsof -t -i:8000)

# Check Python dependencies
pip list | grep fastapi
pip install -r requirements.txt --upgrade
```

#### 2. Database Connection Issues

**Symptoms:**
- Database connection timeouts
- Authentication failures
- Migration errors

**Solutions:**
```bash
# Test database connection
python -c "from backend.database import engine; print(engine.execute('SELECT 1').scalar())"

# Reset database
rm lifecare.db  # For SQLite
python -c "from backend.database import create_tables; create_tables()"

# Check PostgreSQL status
sudo systemctl status postgresql
sudo systemctl restart postgresql
```

#### 3. ML Model Issues

**Symptoms:**
- Model loading errors
- Prediction failures
- Memory issues

**Solutions:**
```bash
# Reinitialize ML model
python init_model.py

# Check model file
ls -la models/
file models/anomaly_model.pkl

# Test model loading
python -c "import joblib; model = joblib.load('models/anomaly_model.pkl'); print('Model loaded successfully')"
```

#### 4. Frontend Build Issues

**Symptoms:**
- Build failures
- Module not found errors
- Runtime errors

**Solutions:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be 16+
npm --version
```

### Performance Optimization

#### Backend Optimization

```python
# Use async/await for I/O operations
@app.get("/api/v1/health/readings")
async def get_readings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HealthReading))
    return result.scalars().all()

# Enable response caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="lifecare-cache")
```

#### Database Optimization

```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_health_readings_user_id ON health_readings(user_id);
CREATE INDEX idx_health_readings_timestamp ON health_readings(timestamp);
CREATE INDEX idx_health_readings_is_anomaly ON health_readings(is_anomaly);

-- Optimize queries with EXPLAIN
EXPLAIN ANALYZE SELECT * FROM health_readings WHERE user_id = 'demo_user' ORDER BY timestamp DESC LIMIT 10;
```

#### Frontend Optimization

```javascript
// Use React.memo for expensive components
const HealthChart = React.memo(({ data }) => {
  return <LineChart data={data} />;
});

// Implement virtual scrolling for large lists
import { FixedSizeList as List } from 'react-window';

// Use code splitting
const Dashboard = lazy(() => import('./pages/Dashboard'));
```

### Scaling Considerations

#### Horizontal Scaling

```yaml
# Kubernetes deployment with multiple replicas
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lifecare-ai
spec:
  replicas: 5
  selector:
    matchLabels:
      app: lifecare-ai
  template:
    metadata:
      labels:
        app: lifecare-ai
    spec:
      containers:
      - name: lifecare-backend
        image: lifecare-ai:latest
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

#### Database Scaling

```python
# Read replicas for better performance
from sqlalchemy import create_engine

# Write database
write_engine = create_engine(DATABASE_WRITE_URL)

# Read replicas
read_engines = [
    create_engine(DATABASE_READ_URL_1),
    create_engine(DATABASE_READ_URL_2),
]

# Load balancing for read operations
import random

def get_read_engine():
    return random.choice(read_engines)
```

---

## 📞 Support

### Getting Help

- **Documentation**: Check this deployment guide and the main README
- **GitHub Issues**: Report deployment issues on GitHub
- **Community Discord**: Join our community for real-time help
- **Enterprise Support**: Contact enterprise@lifecare-ai.com for production support

### Deployment Checklist

Before going to production, ensure:

- [ ] Environment variables are properly configured
- [ ] Database is set up with proper backups
- [ ] SSL/TLS certificates are installed
- [ ] Monitoring and logging are configured
- [ ] Health checks are working
- [ ] Load balancing is configured (if needed)
- [ ] Security headers are set
- [ ] Rate limiting is enabled
- [ ] Error tracking is set up (Sentry, etc.)
- [ ] Performance monitoring is active

---

**🏥 LifeCare AI - Deployment Guide**
*For questions or support, contact: support@lifecare-ai.com*