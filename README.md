# ACEest Fitness & Gym Management System

A comprehensive, production-ready Flask REST API for fitness gym management with role-based access control, client management, workout tracking, and advanced reporting capabilities.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running Locally](#running-locally)
- [Docker Deployment](#docker-deployment)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Testing](#testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Database Schema](#database-schema)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

### Core Functionality
- **Role-Based Authentication:** Admin and User roles with token-based authentication
- **Client Management:** Complete CRUD operations for fitness clients
- **Program Management:** AI-style fitness program generation (Fat Loss, Muscle Gain, Beginner)
- **Calorie Calculation:** Automatic calorie recommendations based on program and weight
- **Progress Tracking:** Weekly adherence tracking and historical data
- **Workout Logging:** Comprehensive workout and exercise tracking
- **Membership Management:** Status tracking and renewal dates
- **Metrics Logging:** Weight, waist, and body fat tracking
- **PDF Reports:** Generate professional client reports

### Technical Features
- RESTful API design with JSON responses
- SQLite database with normalized schema
- Request validation and error handling
- Health check endpoint for monitoring
- Proper HTTP status codes
- CORS-ready for frontend integration
- Docker containerization with multi-stage build
- Docker Compose for local orchestration

---

## 🏗️ Architecture

```
ACEest Fitness API
├── Flask REST API (Port 5000)
├── SQLite Database (aceest_fitness.db)
├── Role-Based Authentication
├── 6 Database Tables
│   ├── users
│   ├── clients
│   ├── progress
│   ├── workouts
│   ├── exercises
│   └── metrics
└── Docker Containerization
```

---

## 📦 Prerequisites

### For Local Development
- Python 3.8 or higher
- pip (Python package manager)
- Git
- Docker (optional, for containerization)
- Docker Compose (optional)

### For Testing
- pytest
- pytest-cov (code coverage)
- flake8 (code linting)

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd DevOps_Assignment
```

### 2. Create Virtual Environment (Recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
python -c "import flask; print('Flask version:', flask.__version__)"
```

---

## 🏃 Running Locally

### 1. Start the Flask Application
```bash
python app.py
```

Expected output:
```
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in production.
 * Running on http://0.0.0.0:5000
Press CTRL+C to quit
```

### 2. Test the Health Endpoint
```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "ok",
  "service": "ACEest Fitness API",
  "version": "1.0.0",
  "timestamp": "2026-04-02T10:30:45.123456"
}
```

### 3. Login to Get Authentication Token
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

Response:
```json
{
  "token": "admin:Admin",
  "username": "admin",
  "role": "Admin",
  "message": "Login successful"
}
```

### 4. Use the API with Token
```bash
curl http://localhost:5000/api/clients \
  -H "Authorization: Bearer admin:Admin"
```

---

## 🐳 Docker Deployment

### Build Docker Image
```bash
# Build image with tag
docker build -t aceest:latest .

# Verify image
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

# Check container status
docker ps | grep aceest

# View logs
docker logs aceest-api

# Stop container
docker stop aceest-api
```

### Using Docker Compose (Recommended)
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

### Verify Container Health
```bash
docker inspect --format='{{.State.Health.Status}}' aceest-api
curl http://localhost:5000/health
```

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/login` | User authentication |
| GET | `/health` | Health check |

### Clients
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/clients` | Get all clients |
| GET | `/api/clients/<id>` | Get specific client |
| POST | `/api/clients` | Create new client |
| PUT | `/api/clients/<id>` | Update client |
| DELETE | `/api/clients/<id>` | Delete client |

### Programs & Calories
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/programs` | Get available programs |
| POST | `/api/programs/generate/<id>` | Generate AI program |
| POST | `/api/calories/<id>/calculate` | Calculate calories |

### Progress & Workouts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/progress/<id>` | Get client progress |
| POST | `/api/progress/<id>` | Add progress record |
| GET | `/api/workouts/<id>` | Get client workouts |
| POST | `/api/workouts/<id>` | Add workout |

### Metrics & Membership
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/metrics/<id>` | Get client metrics |
| POST | `/api/metrics/<id>` | Add metrics |
| GET | `/api/membership/<id>` | Get membership status |
| PUT | `/api/membership/<id>` | Update membership |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reports/<id>/pdf` | Generate PDF report |

---

## 🔐 Authentication

### Token Format
```
Authorization: Bearer <username>:<role>

Example:
Authorization: Bearer admin:Admin
```

### Default Credentials
- **Username:** `admin`
- **Password:** `admin`
- **Role:** `Admin`

### Adding New Users
```bash
# Direct database insertion (development only)
sqlite3 aceest_fitness.db "INSERT INTO users VALUES ('user1','pass123','User')"
```

---

## 🧪 Testing

### Run All Tests
```bash
pytest -v
```

### Run Tests with Coverage
```bash
pytest --cov=. --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_app.py -v
```

### Run Linting
```bash
flake8 app.py tests/
pylint app.py
```

### Run Tests in Docker
```bash
docker run --rm aceest:latest pytest
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
The `.github/workflows/main.yml` file defines the automated pipeline:

**Triggers:** Push or Pull Request to main/develop branches

**Stages:**
1. **Build & Lint**
   - Checkout code
   - Setup Python 3.11
   - Install dependencies
   - Run flake8 linting
   - Run pytest tests

2. **Docker Image**
   - Build Docker image
   - Tag with git SHA
   - (Optional) Push to registry

3. **Integration Tests**
   - Run Docker container
   - Execute tests in container
   - Verify health endpoint

### Jenkins Pipeline
Configure Jenkins to pull from GitHub and execute:
```bash
# Stage 1: Clone & Install
git clone <repo>
pip install -r requirements.txt

# Stage 2: Test & Lint
pytest --cov=.
flake8 app.py

# Stage 3: Build Docker
docker build -t aceest:${BUILD_ID} .

# Stage 4: Run Container Tests
docker run --rm aceest:${BUILD_ID} pytest
```

---

## 💾 Database Schema

### Users Table
```sql
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    password TEXT,
    role TEXT
);
```

### Clients Table
```sql
CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    age INTEGER,
    height REAL,
    weight REAL,
    program TEXT,
    calories INTEGER,
    target_weight REAL,
    target_adherence INTEGER,
    membership_status TEXT,
    membership_end TEXT
);
```

### Progress Table
```sql
CREATE TABLE progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT,
    week TEXT,
    adherence INTEGER
);
```

### Workouts Table
```sql
CREATE TABLE workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT,
    date TEXT,
    workout_type TEXT,
    duration_min INTEGER,
    notes TEXT
);
```

### Exercises Table
```sql
CREATE TABLE exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER,
    name TEXT,
    sets INTEGER,
    reps INTEGER,
    weight REAL
);
```

### Metrics Table
```sql
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT,
    date TEXT,
    weight REAL,
    waist REAL,
    bodyfat REAL
);
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process on port 5000
netstat -ano | findstr :5000  # Windows
lsof -i :5000  # macOS/Linux

# Kill process
taskkill /PID <PID> /F  # Windows
kill -9 <PID>  # macOS/Linux
```

### Database Lock Issues
```bash
# Remove database and recreate
rm aceest_fitness.db
python app.py  # Recreates clean database
```

### Docker Image Build Fails
```bash
# Clear Docker cache
docker system prune -a

# Rebuild
docker build --no-cache -t aceest:latest .
```

### Tests Failing
```bash
# Verify dependencies
pip install -r requirements.txt --force-reinstall

# Run with verbose output
pytest -vvs

# Check Python version
python --version  # Should be 3.8+
```

### Health Check Failing
```bash
# Check if Flask is running
curl http://localhost:5000/health

# View Flask logs
docker logs aceest-api

# Verify network connectivity in Docker
docker exec aceest-api curl localhost:5000/health
```

---

## 📚 Example API Usage

### Complete Workflow Example

#### 1. Login
```bash
RESPONSE=$(curl -s -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}')
TOKEN=$(echo $RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)
```

#### 2. Create Client
```bash
curl -X POST http://localhost:5000/api/clients \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "age": 30,
    "weight": 85,
    "height": 180
  }'
```

#### 3. Get Clients
```bash
curl http://localhost:5000/api/clients \
  -H "Authorization: Bearer $TOKEN"
```

#### 4. Generate Program
```bash
curl -X POST http://localhost:5000/api/programs/generate/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"program_type": "Fat Loss"}'
```

#### 5. Calculate Calories
```bash
curl http://localhost:5000/api/calories/1/calculate \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📝 Notes

- The API uses SQLite for development/testing. Consider PostgreSQL for production.
- Passwords are stored in plain text for development only. Use hashing (bcrypt) in production.
- The default admin credentials should be changed in production.
- Enable HTTPS/TLS for production deployments.
- Implement rate limiting for API endpoints in production.
- Add database migrations for schema changes.

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and commit: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit a pull request

---

## 📄 License

This project is part of the ACEest Fitness & Gym modernization initiative.

---

## 📧 Support

For issues or questions, please open an issue in the GitHub repository or contact the DevOps team.

---

**Last Updated:** April 2, 2026  
**Version:** 1.0.0  
**Python:** 3.11+  
**Flask:** 2.3.3+
