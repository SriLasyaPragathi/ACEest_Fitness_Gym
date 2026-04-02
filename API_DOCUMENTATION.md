# ACEest Fitness API - Comprehensive API Documentation

## Base URL
```
http://localhost:5000  (Development)
https://api.aceest.com (Production)
```

## Response Format
All responses are in JSON format. Standard response structure:
```json
{
  "data": {},
  "message": "Success message",
  "status_code": 200,
  "timestamp": "2026-04-02T10:30:45.123456"
}
```

---

## Authentication

### Token Format
```
Authorization: Bearer <username>:<role>
```

### Login Endpoint
```http
POST /api/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin"
}
```

**Response (200 OK):**
```json
{
  "token": "admin:Admin",
  "username": "admin",
  "role": "Admin",
  "message": "Login successful"
}
```

---

## Client Management Endpoints

### Get All Clients
```http
GET /api/clients
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "count": 5,
  "clients": [
    {
      "id": 1,
      "name": "John Doe",
      "age": 30,
      "height": 180,
      "weight": 85,
      "program": "Fat Loss",
      "calories": 1870,
      "target_weight": 80,
      "target_adherence": 90,
      "membership_status": "Active",
      "membership_end": "2026-12-31"
    }
  ]
}
```

### Get Specific Client
```http
GET /api/clients/{id}
Authorization: Bearer <token>
```

### Create Client
```http
POST /api/clients
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Jane Doe",
  "age": 28,
  "height": 165,
  "weight": 70,
  "program": "Muscle Gain"
}
```

**Response (201 Created):**
```json
{
  "message": "Client created successfully",
  "client_id": 101
}
```

### Update Client
```http
PUT /api/clients/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "age": 31,
  "weight": 83,
  "membership_status": "Inactive"
}
```

### Delete Client
```http
DELETE /api/clients/{id}
Authorization: Bearer <token>
```

---

## Program Endpoints

### Get Available Programs
```http
GET /api/programs
Authorization: Bearer <token>
```

**Response:**
```json
{
  "Fat Loss": {
    "factor": 22,
    "description": "High cardio focus",
    "examples": ["Full Body HIIT", "Circuit Training", "Cardio + Weights"]
  },
  "Muscle Gain": {
    "factor": 35,
    "description": "Heavy strength focus",
    "examples": ["Push/Pull/Legs", "Upper/Lower Split", "Full Body Strength"]
  },
  "Beginner": {
    "factor": 26,
    "description": "Circuit training focus",
    "examples": ["Full Body 3x/week", "Light Strength + Mobility"]
  }
}
```

### Generate Program for Client
```http
POST /api/programs/generate/{client_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "program_type": "Fat Loss"
}
```

**Response:**
```json
{
  "message": "Program generated successfully",
  "program_type": "Fat Loss",
  "program": "Circuit Training",
  "client_id": 1
}
```

---

## Calories Endpoint

### Calculate Recommended Calories
```http
POST /api/calories/{client_id}/calculate
Authorization: Bearer <token>
Content-Type: application/json

{
  "program_type": "Fat Loss"
}
```

**Formula:** Weight (kg) × Program Factor

**Response:**
```json
{
  "client_id": 1,
  "weight_kg": 85,
  "program_type": "Fat Loss",
  "factor": 22,
  "recommended_calories": 1870
}
```

---

## Progress Tracking Endpoints

### Get Client Progress
```http
GET /api/progress/{client_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "client_id": 1,
  "count": 3,
  "progress": [
    {
      "id": 1,
      "client_name": "John Doe",
      "week": "2026-W14",
      "adherence": 95
    },
    {
      "id": 2,
      "client_name": "John Doe",
      "week": "2026-W13",
      "adherence": 88
    }
  ]
}
```

### Add Progress Record
```http
POST /api/progress/{client_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "week": "2026-W14",
  "adherence": 92
}
```

**Response:**
```json
{
  "message": "Progress recorded successfully",
  "progress_id": 5
}
```

---

## Workout Tracking Endpoints

### Get Client Workouts
```http
GET /api/workouts/{client_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "client_id": 1,
  "count": 10,
  "workouts": [
    {
      "id": 1,
      "client_name": "John Doe",
      "date": "2026-04-02",
      "workout_type": "Strength",
      "duration_min": 60,
      "notes": "Good session, increased weight on squats"
    }
  ]
}
```

### Add Workout
```http
POST /api/workouts/{client_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "date": "2026-04-02",
  "workout_type": "Strength",
  "duration_min": 60,
  "notes": "Good pump, focus on chest"
}
```

**Valid Workout Types:**
- Strength
- Hypertrophy
- Cardio
- Mobility

---

## Metrics Endpoints

### Get Client Metrics
```http
GET /api/metrics/{client_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "client_id": 1,
  "count": 5,
  "metrics": [
    {
      "id": 1,
      "client_name": "John Doe",
      "date": "2026-04-02",
      "weight": 84.5,
      "waist": 89,
      "bodyfat": 14.5
    }
  ]
}
```

### Add Metrics
```http
POST /api/metrics/{client_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "weight": 84.5,
  "waist": 89,
  "bodyfat": 14.5,
  "date": "2026-04-02"
}
```

---

## Membership Endpoints

### Get Membership Status
```http
GET /api/membership/{client_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "client_id": 1,
  "name": "John Doe",
  "membership_status": "Active",
  "membership_end": "2026-12-31"
}
```

### Update Membership
```http
PUT /api/membership/{client_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "membership_status": "Inactive",
  "membership_end": "2026-06-30"
}
```

---

## Reports Endpoint

### Generate PDF Report
```http
GET /api/reports/{client_id}/pdf
Authorization: Bearer <token>
```

**Response:** PDF file download
- Filename: `{client_name}_report.pdf`
- Content-Type: `application/pdf`

---

## Health Check

### Health Status
```http
GET /health
```

**No authentication required**

**Response (200 OK):**
```json
{
  "status": "ok",
  "service": "ACEest Fitness API",
  "version": "1.0.0",
  "timestamp": "2026-04-02T10:30:45.123456"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required fields"
}
```

### 401 Unauthorized
```json
{
  "error": "Missing authentication token"
}
```

### 404 Not Found
```json
{
  "error": "Client not found"
}
```

### 409 Conflict
```json
{
  "error": "Client name already exists"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Missing/invalid token |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Duplicate resource |
| 500 | Internal Server Error |

---

## Rate Limiting (Future)
Currently no rate limiting. Will be implemented in production:
- 100 requests per minute per IP
- 1000 requests per hour per authenticated user

---

## Pagination (Future)
Future versions will support pagination:
```http
GET /api/clients?page=1&limit=10
```

---

## Filtering & Sorting (Future)
Future versions will support filtering and sorting:
```http
GET /api/clients?membership_status=Active&sort=name
GET /api/workouts/1?date_from=2026-01-01&date_to=2026-04-02
```

---

## Example cURL Commands

### Login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

### Get Clients
```bash
TOKEN="admin:Admin"
curl http://localhost:5000/api/clients \
  -H "Authorization: Bearer $TOKEN"
```

### Create Client
```bash
curl -X POST http://localhost:5000/api/clients \
  -H "Authorization: Bearer admin:Admin" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Smith",
    "age": 28,
    "height": 165,
    "weight": 65
  }'
```

---

## Version History

### v1.0.0 (April 2, 2026)
- Initial release
- Basic CRUD operations for clients
- Progress tracking
- Workout logging
- Membership management
- Token-based authentication

---

## Support & Contact
For API issues, please open an issue on GitHub or contact: devops@aceest.com
