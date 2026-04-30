# Deployment Guide - ACEest Fitness API

## Table of Contents
- [Quick Start](#quick-start)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Environment Configuration](#environment-configuration)
- [Database Migration](#database-migration)
- [Monitoring & Logging](#monitoring--logging)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1-Minute Setup
```bash
# Clone repository
git clone <repo-url>
cd DevOps_Assignment

# Install and run
pip install -r requirements.txt
python app.py

# Test
curl http://localhost:5000/health
```

---

## Local Development

### Setup Development Environment

#### Step 1: Clone Repository
```bash
git clone https://github.com/your-org/aceest-fitness.git
cd aceest-fitness
```

#### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Run Application
```bash
python app.py
```

The API will be available at `http://localhost:5000`

#### Step 5: Test API
```bash
# Health check
curl http://localhost:5000/health

# Login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

### Run Tests
```bash
pytest tests/ -v
pytest --cov=app tests/  # With coverage
```

---

## Docker Deployment

### Build Docker Image
```bash
# Build image
docker build -t aceest:latest .

# Verify
docker images | grep aceest
```

### Run Docker Container
```bash
# Run container
docker run -d \
  -p 5000:5000 \
  -v aceest-db:/app \
  --name aceest-api \
  aceest:latest

# Check status
docker ps

# View logs
docker logs aceest-api

# Test
docker exec aceest-api curl http://localhost:5000/health
```

### Docker Compose (Recommended)
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f aceest-api

# Stop services
docker-compose down

# Clean up volumes
docker-compose down -v
```

### Docker Commands Reference
```bash
# List running containers
docker ps

# View container logs
docker logs <container-id>

# Execute command in container
docker exec <container-id> <command>

# Stop container
docker stop <container-id>

# Remove container
docker rm <container-id>

# Remove image
docker rmi <image-id>

# View image details
docker inspect <image-id>
```

---

## Production Deployment

### Prerequisites
- Linux server (Ubuntu 20.04+, CentOS 8+)
- Docker and Docker Compose installed
- Git installed
- Reverse proxy (Nginx/Apache)
- SSL certificate

### Deployment Steps

#### Step 1: Server Setup
```bash
# Update system
sudo apt-get update && apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version
```

#### Step 2: Clone Repository
```bash
cd /opt
sudo git clone <repo-url>
cd aceest-fitness
sudo chown -R $USER:$USER .
```

#### Step 3: Environment Configuration
```bash
# Copy and edit environment file
cp .env.example .env.production
sudo nano .env.production

# Set production values:
FLASK_ENV=production
DEBUG=False
SECRET_KEY=<generate-strong-key>
DATABASE_URL=aceest_fitness.db
```

#### Step 4: Build and Deploy
```bash
# Build image
docker build -t aceest:1.0 .

# Create docker-compose override for production
sudo cp docker-compose.yml docker-compose.prod.yml

# Edit production compose file
sudo nano docker-compose.prod.yml
# Set restart policy: always
# Configure healthchecks
# Add resource limits
```

#### Step 5: Start Services
```bash
# Start with production compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify
docker-compose ps

# Check logs
docker-compose logs -f aceest-api
```

#### Step 6: Nginx Reverse Proxy Setup
```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/aceest

# Add configuration:
server {
    listen 80;
    server_name api.aceest.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.aceest.com;

    ssl_certificate /etc/letsencrypt/live/api.aceest.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.aceest.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        access_log off;
        proxy_pass http://localhost:5000/health;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/aceest /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Environment Configuration

### Environment Variables

Create `.env` file:
```bash
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-secret-key-here
PORT=5000

# Database
DATABASE_PATH=./aceest_fitness.db
DATABASE_BACKUP_PATH=./backups/

# Security
CORS_ORIGINS=https://app.aceest.com,https://admin.aceest.com
API_KEY_REQUIRED=True

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/aceest.log

# Performance
MAX_CONNECTIONS=100
TIMEOUT=30

# Email (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Load Environment Variables
```python
# In app.py
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
```

---

## Database Migration

### Backup Database
```bash
# Docker backup
docker exec aceest-api cp /app/aceest_fitness.db /app/backups/aceest_$(date +%Y%m%d_%H%M%S).db

# System backup
cp aceest_fitness.db backups/aceest_$(date +%Y%m%d_%H%M%S).db
```

### Database Schema Migration
```bash
# Export schema
sqlite3 aceest_fitness.db ".schema" > schema.sql

# Create backup
sqlite3 aceest_fitness.db ".backup backup.db"

# Restore if needed
sqlite3 aceest_fitness.db ".restore backup.db"
```

### PostgreSQL Migration (Future)
```bash
# When migrating to PostgreSQL:
# 1. Export data from SQLite
sqlite3 aceest_fitness.db ".mode csv" "SELECT * FROM clients;" > clients.csv

# 2. Create PostgreSQL tables
psql -U postgres < schema.sql

# 3. Import data
psql -c "COPY clients FROM 'clients.csv' WITH (FORMAT csv);"
```

---

## Monitoring & Logging

### Container Logs
```bash
# Real-time logs
docker logs -f aceest-api

# Last 100 lines
docker logs --tail=100 aceest-api

# Logs since specific time
docker logs --since=10m aceest-api
```

### Health Monitoring
```bash
# Manual health check
curl http://localhost:5000/health

# Automated monitoring (every 30s)
watch -n 30 'curl -s http://localhost:5000/health | jq'
```

### Container Stats
```bash
# Resource usage
docker stats aceest-api

# Memory usage
docker stats --no-stream aceest-api
```

### Application Logs
```bash
# If logging to file
docker exec aceest-api tail -f /app/logs/aceest.log

# Archive logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find process on port 5000
lsof -i :5000

# Kill process
kill -9 <PID>

# Use different port
docker run -p 5001:5000 aceest:latest
```

### Database Lock
```bash
# Check database locks
lsof | grep aceest_fitness.db

# Restart container
docker restart aceest-api
```

### Container Won't Start
```bash
# Check logs
docker logs aceest-api

# Verify image
docker images

# Rebuild
docker build --no-cache -t aceest:latest .
```

### Out of Memory
```bash
# Check memory usage
docker stats aceest-api

# Set memory limits
docker run -m 512m aceest:latest

# In docker-compose.yml:
services:
  aceest-api:
    deploy:
      resources:
        limits:
          memory: 512M
```

### Network Issues
```bash
# Check network connectivity
docker exec aceest-api ping 8.8.8.8

# Inspect network
docker network inspect bridge

# Restart container
docker restart aceest-api
```

---

## Backup & Recovery

### Automatic Backup Script
```bash
#!/bin/bash
# backup.sh - Daily backup

BACKUP_DIR="/backups/aceest"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="/app/aceest_fitness.db"

mkdir -p $BACKUP_DIR

docker exec aceest-api cp $DB_FILE $BACKUP_DIR/aceest_$DATE.db

# Keep only last 30 days
find $BACKUP_DIR -name "*.db" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/aceest_$DATE.db"
```

### Schedule Backup (Cron)
```bash
# Add to crontab
0 2 * * * /opt/aceest-fitness/backup.sh

# Edit crontab
crontab -e
```

---

## Performance Tuning

### Docker Compose Optimization
```yaml
services:
  aceest-api:
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### Database Optimization
```python
# Add database indexes
CREATE INDEX idx_client_name ON clients(name);
CREATE INDEX idx_progress_client ON progress(client_name);
CREATE INDEX idx_workout_date ON workouts(date);
```

---

## Security Considerations

### SSL/TLS
- Always use HTTPS in production
- Use Let's Encrypt for free certificates
- Keep certificates updated

### API Security
- Change default admin credentials
- Implement rate limiting
- Use strong secret keys
- Enable CORS only for trusted domains

### Database Security
- Regular backups
- Database encryption
- Access controls
- SQL injection prevention (already using parameterized queries)

### Container Security
- Use minimal base images
- Non-root user (already implemented)
- Regular security updates
- Scan for vulnerabilities

---

## Scaling

### Horizontal Scaling
```yaml
# docker-compose.yml with multiple instances
services:
  aceest-api-1:
    build: .
    ports: ["5001:5000"]
  aceest-api-2:
    build: .
    ports: ["5002:5000"]
  aceest-api-3:
    build: .
    ports: ["5003:5000"]
  
  nginx-lb:
    image: nginx:latest
    ports: ["80:80"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Load Balancer Configuration
```bash
# Nginx upstream
upstream aceest-api {
    server aceest-api-1:5000;
    server aceest-api-2:5000;
    server aceest-api-3:5000;
}

server {
    location / {
        proxy_pass http://aceest-api;
    }
}
```

---

## Version Upgrades

### Before Upgrade
1. Backup database
2. Test new version locally
3. Create rollback plan

### Upgrade Steps
```bash
# Pull latest code
git pull origin main

# Test
pytest tests/

# Build new image
docker build -t aceest:2.0 .

# Stop old container
docker stop aceest-api

# Start new container
docker run -d -p 5000:5000 --name aceest-api-new aceest:2.0

# Test new version
curl http://localhost:5000/health

# If successful, remove old
docker rm aceest-api
docker rename aceest-api-new aceest-api
```

---

## Rollback Plan

### Quick Rollback
```bash
# Stop current version
docker stop aceest-api

# Remove current container
docker rm aceest-api

# Run previous stable version
docker run -d -p 5000:5000 --name aceest-api aceest:1.0

# Restore database backup if needed
cp backups/aceest_backup.db aceest_fitness.db
```

---

**Last Updated:** April 2, 2026  
**Version:** 1.0.0  
**Status:** Production Ready
