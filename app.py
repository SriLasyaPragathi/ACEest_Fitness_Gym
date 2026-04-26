"""
ACEest Fitness & Gym - Flask REST API
A comprehensive fitness and gym management system with role-based access control.
"""

import sqlite3
import json
from datetime import datetime, date
import random
from functools import wraps
import os
from flask import Flask, request, jsonify
from fpdf import FPDF

# Version
__version__ = "1.0.0"

# Application Configuration
DB_NAME = "aceest_fitness.db"
DATABASE_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# ======================== DATABASE INITIALIZATION ========================
def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database schema"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Users table (role-based login)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT
    )
    """)
    
    # Clients table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
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
    )
    """)
    
    # Progress table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        week TEXT,
        adherence INTEGER
    )
    """)
    
    # Workouts table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        date TEXT,
        workout_type TEXT,
        duration_min INTEGER,
        notes TEXT
    )
    """)
    
    # Exercises table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workout_id INTEGER,
        name TEXT,
        sets INTEGER,
        reps INTEGER,
        weight REAL
    )
    """)
    
    # Metrics table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        date TEXT,
        weight REAL,
        waist REAL,
        bodyfat REAL
    )
    """)
    
    # Commit all table creations
    conn.commit()
    
    # Add default admin user if not exists
    cur.execute("SELECT * FROM users WHERE username='admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users VALUES ('admin','admin','Admin')")
        conn.commit()
    
    conn.close()

# ======================== AUTHENTICATION ========================
def authenticate_token(f):
    """Decorator to verify authentication token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        # Check if Bearer prefix exists
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid Bearer token"}), 401
        
        # Extract token after "Bearer "
        token = auth_header[7:]  # Length of "Bearer " is 7
        
        if not token:
            return jsonify({"error": "Missing authentication token"}), 401
        
        # Simple token validation: token format is "username:role"
        try:
            username, role = token.split(':')
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username=?", (username,))
            user = cur.fetchone()
            conn.close()
            
            if not user:
                return jsonify({"error": "Invalid token"}), 401
            
            # Store in request context for use in route
            request.user = {'username': username, 'role': role}
            return f(*args, **kwargs)
        except (ValueError, IndexError):
            return jsonify({"error": "Invalid token format"}), 401
    
    return decorated_function

# ======================== HEALTH CHECK ========================
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "ACEest Fitness API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }), 200

# ======================== AUTHENTICATION ENDPOINTS ========================
@app.route('/api/login', methods=['POST'])
def login():
    """
    User login endpoint
    Request: {"username": "admin", "password": "admin"}
    Returns: {"token": "username:role", "role": "Admin", "username": "admin"}
    """
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Missing username or password"}), 400
    
    username = data['username']
    password = data['password']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cur.fetchone()
    conn.close()
    
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    token = f"{username}:{user['role']}"
    return jsonify({
        "token": token,
        "username": username,
        "role": user['role'],
        "message": "Login successful"
    }), 200

# ======================== CLIENT MANAGEMENT ENDPOINTS ========================
@app.route('/api/clients', methods=['GET'])
@authenticate_token
def get_clients():
    """
    Get all clients
    Returns: List of all clients
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients ORDER BY name")
    clients = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    return jsonify({
        "count": len(clients),
        "clients": clients
    }), 200

@app.route('/api/clients/<int:client_id>', methods=['GET'])
@authenticate_token
def get_client(client_id):
    """
    Get specific client by ID
    Returns: Client details
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients WHERE id=?", (client_id,))
    client = cur.fetchone()
    conn.close()
    
    if not client:
        return jsonify({"error": "Client not found"}), 404
    
    return jsonify(dict(client)), 200

@app.route('/api/clients', methods=['POST'])
@authenticate_token
def create_client():
    """
    Create new client
    Request: {"name": "John Doe", "age": 30, "weight": 80, "height": 180}
    """
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO clients (name, age, height, weight, membership_status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data['name'],
            data.get('age', 0),
            data.get('height', 0),
            data.get('weight', 0),
            'Active'
        ))
        conn.commit()
        client_id = cur.lastrowid
        conn.close()
        
        return jsonify({
            "message": "Client created successfully",
            "client_id": client_id
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Client name already exists"}), 409

@app.route('/api/clients/<int:client_id>', methods=['PUT'])
@authenticate_token
def update_client(client_id):
    """
    Update client information
    """
    data = request.get_json()
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Verify client exists
    cur.execute("SELECT * FROM clients WHERE id=?", (client_id,))
    if not cur.fetchone():
        conn.close()
        return jsonify({"error": "Client not found"}), 404
    
    # Update fields
    update_fields = []
    update_values = []
    
    for field in ['name', 'age', 'height', 'weight', 'program', 'calories', 'target_weight', 'membership_status']:
        if field in data:
            update_fields.append(f"{field}=?")
            update_values.append(data[field])
    
    if update_fields:
        update_values.append(client_id)
        query = f"UPDATE clients SET {', '.join(update_fields)} WHERE id=?"
        cur.execute(query, update_values)
        conn.commit()
    
    conn.close()
    return jsonify({"message": "Client updated successfully"}), 200

@app.route('/api/clients/<int:client_id>', methods=['DELETE'])
@authenticate_token
def delete_client(client_id):
    """
    Delete client
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Verify client exists
    cur.execute("SELECT * FROM clients WHERE id=?", (client_id,))
    if not cur.fetchone():
        conn.close()
        return jsonify({"error": "Client not found"}), 404
    
    cur.execute("DELETE FROM clients WHERE id=?", (client_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Client deleted successfully"}), 200

# ======================== PROGRAM ENDPOINTS ========================
@app.route('/api/programs', methods=['GET'])
@authenticate_token
def get_programs():
    """
    Get available fitness programs
    Returns: List of available programs
    """
    programs = {
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
    return jsonify(programs), 200

@app.route('/api/programs/generate/<int:client_id>', methods=['POST'])
@authenticate_token
def generate_program(client_id):
    """
    Generate AI-style program for client
    Request: {"program_type": "Fat Loss"} (optional, random if not provided)
    """
    data = request.get_json() or {}
    
    program_templates = {
        "Fat Loss": ["Full Body HIIT", "Circuit Training", "Cardio + Weights"],
        "Muscle Gain": ["Push/Pull/Legs", "Upper/Lower Split", "Full Body Strength"],
        "Beginner": ["Full Body 3x/week", "Light Strength + Mobility"]
    }
    
    program_type = data.get('program_type') or random.choice(list(program_templates.keys()))
    
    if program_type not in program_templates:
        return jsonify({"error": "Invalid program type"}), 400
    
    program_detail = random.choice(program_templates[program_type])
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Verify client exists
    cur.execute("SELECT * FROM clients WHERE id=?", (client_id,))
    client = cur.fetchone()
    if not client:
        conn.close()
        return jsonify({"error": "Client not found"}), 404
    
    # Update program
    cur.execute("UPDATE clients SET program=? WHERE id=?", (program_detail, client_id))
    conn.commit()
    conn.close()
    
    return jsonify({
        "message": "Program generated successfully",
        "program_type": program_type,
        "program": program_detail,
        "client_id": client_id
    }), 200

# ======================== CALORIE CALCULATION ENDPOINT ========================
@app.route('/api/calories/<int:client_id>/calculate', methods=['POST'])
@authenticate_token
def calculate_calories(client_id):
    """
    Calculate calories for client based on program
    Request: {"program_type": "Fat Loss"} or uses current program
    Formula: Weight (kg) × Program Factor
    """
    data = request.get_json() or {}
    
    factors = {
        "Fat Loss": 22,
        "Muscle Gain": 35,
        "Beginner": 26
    }
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT weight, program FROM clients WHERE id=?", (client_id,))
    client = cur.fetchone()
    conn.close()
    
    if not client:
        return jsonify({"error": "Client not found"}), 404
    
    weight = client['weight']
    program_type = data.get('program_type') or client['program'] or 'Beginner'
    
    # Validate program type
    if program_type not in factors:
        return jsonify({"error": f"Invalid program type: {program_type}. Must be one of {list(factors.keys())}"}), 400
    
    factor = factors.get(program_type)
    calories = weight * factor
    
    return jsonify({
        "client_id": client_id,
        "weight_kg": weight,
        "program_type": program_type,
        "factor": factor,
        "recommended_calories": int(calories)
    }), 200

# ======================== PROGRESS TRACKING ENDPOINTS ========================
@app.route('/api/progress/<int:client_id>', methods=['GET'])
@authenticate_token
def get_progress(client_id):
    """
    Get client progress history
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Verify client exists
    cur.execute("SELECT name FROM clients WHERE id=?", (client_id,))
    client = cur.fetchone()
    if not client:
        conn.close()
        return jsonify({"error": "Client not found"}), 404
    
    cur.execute(
        "SELECT * FROM progress WHERE client_name=? ORDER BY id DESC",
        (client['name'],)
    )
    progress_data = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    return jsonify({
        "client_id": client_id,
        "count": len(progress_data),
        "progress": progress_data
    }), 200

@app.route('/api/progress/<int:client_id>', methods=['POST'])
@authenticate_token
def add_progress(client_id):
    """
    Add progress record for client
    Request: {"week": "2026-W14", "adherence": 85}
    """
    data = request.get_json()
    
    if not data or 'adherence' not in data:
        return jsonify({"error": "Missing adherence field"}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Verify client exists
    cur.execute("SELECT name FROM clients WHERE id=?", (client_id,))
    client = cur.fetchone()
    if not client:
        conn.close()
        return jsonify({"error": "Client not found"}), 404
    
    week = data.get('week', date.today().isocalendar()[0:2])
    adherence = data['adherence']
    
    cur.execute(
        "INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)",
        (client['name'], str(week), adherence)
    )
    conn.commit()
    progress_id = cur.lastrowid
    conn.close()
    
    return jsonify({
        "message": "Progress recorded successfully",
        "progress_id": progress_id
    }), 201

# ======================== WORKOUT ENDPOINTS ========================
@app.route('/api/workouts/<int:client_id>', methods=['GET'])
@authenticate_token
def get_workouts(client_id):
    """
    Get workouts for client
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Verify client exists
    cur.execute("SELECT name FROM clients WHERE id=?", (client_id,))
    client = cur.fetchone()
    if not client:
        conn.close()
        return jsonify({"error": "Client not found"}), 404
    
    cur.execute(
        "SELECT * FROM workouts WHERE client_name=? ORDER BY date DESC",
        (client['name'],)
    )
    workouts = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    return jsonify({
        "client_id": client_id,
        "count": len(workouts),
        "workouts": workouts
    }), 200

@app.route('/api/workouts/<int:client_id>', methods=['POST'])
@authenticate_token
def add_workout(client_id):
    """
    Add workout for client
    Request: {"date": "2026-04-02", "workout_type": "Strength", "duration_min": 60, "notes": "Good session"}
    """
    data = request.get_json()
    
    if not data or not data.get('workout_type'):
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Verify client exists
    cur.execute("SELECT name FROM clients WHERE id=?", (client_id,))
    client = cur.fetchone()
    if not client:
        conn.close()
        return jsonify({"error": "Client not found"}), 404
    
    cur.execute("""
        INSERT INTO workouts (client_name, date, workout_type, duration_min, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (
        client['name'],
        data.get('date', date.today().isoformat()),
        data['workout_type'],
        data.get('duration_min', 0),
        data.get('notes', '')
    ))
    conn.commit()
    workout_id = cur.lastrowid
    conn.close()
    
    return jsonify({
        "message": "Workout recorded successfully",
        "workout_id": workout_id
    }), 201

# ======================== MEMBERSHIP ENDPOINTS ========================
@app.route('/api/membership/<int:client_id>', methods=['GET'])
@authenticate_token
def get_membership(client_id):
    """
    Get membership status for client
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, membership_status, membership_end FROM clients WHERE id=?", (client_id,))
    client = cur.fetchone()
    conn.close()
    
    if not client:
        return jsonify({"error": "Client not found"}), 404
    
    return jsonify({
        "client_id": client['id'],
        "name": client['name'],
        "membership_status": client['membership_status'],
        "membership_end": client['membership_end']
    }), 200

@app.route('/api/membership/<int:client_id>', methods=['PUT'])
@authenticate_token
def update_membership(client_id):
    """
    Update membership status
    Request: {"membership_status": "Active", "membership_end": "2026-12-31"}
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Missing request body"}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Verify client exists
    cur.execute("SELECT * FROM clients WHERE id=?", (client_id,))
    if not cur.fetchone():
        conn.close()
        return jsonify({"error": "Client not found"}), 404
    
    if 'membership_status' in data:
        cur.execute(
            "UPDATE clients SET membership_status=? WHERE id=?",
            (data['membership_status'], client_id)
        )
    
    if 'membership_end' in data:
        cur.execute(
            "UPDATE clients SET membership_end=? WHERE id=?",
            (data['membership_end'], client_id)
        )
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Membership updated successfully"}), 200

# ======================== REPORT ENDPOINTS ========================
@app.route('/api/reports/<int:client_id>/pdf', methods=['GET'])
@authenticate_token
def generate_pdf_report(client_id):
    """
    Generate PDF report for client
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients WHERE id=?", (client_id,))
    client = cur.fetchone()
    conn.close()
    
    if not client:
        return jsonify({"error": "Client not found"}), 404
    
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"ACEest Client Report - {client['name']}", ln=True)
        pdf.set_font("Arial", "", 12)
        
        columns = ["ID", "Name", "Age", "Height", "Weight", "Program", "Calories", 
                   "Target Weight", "Target Adherence", "Membership", "End Date"]
        
        for i, col in enumerate(columns):
            pdf.cell(0, 10, f"{col}: {client[i]}", ln=True)
        
        pdf_filename = f"{client['name']}_report.pdf"
        pdf.output(pdf_filename)
        
        return jsonify({
            "message": "PDF generated successfully",
            "filename": pdf_filename
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500

# ======================== METRICS ENDPOINTS ========================
@app.route('/api/metrics/<int:client_id>', methods=['GET'])
@authenticate_token
def get_metrics(client_id):
    """
    Get metrics (weight, waist, bodyfat) for client
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Verify client exists
    cur.execute("SELECT name FROM clients WHERE id=?", (client_id,))
    client = cur.fetchone()
    if not client:
        conn.close()
        return jsonify({"error": "Client not found"}), 404
    
    cur.execute(
        "SELECT * FROM metrics WHERE client_name=? ORDER BY date DESC",
        (client['name'],)
    )
    metrics = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    return jsonify({
        "client_id": client_id,
        "count": len(metrics),
        "metrics": metrics
    }), 200

@app.route('/api/metrics/<int:client_id>', methods=['POST'])
@authenticate_token
def add_metrics(client_id):
    """
    Add metrics for client
    Request: {"weight": 80.5, "waist": 90, "bodyfat": 15.5, "date": "2026-04-02"}
    """
    data = request.get_json()
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Verify client exists
    cur.execute("SELECT name FROM clients WHERE id=?", (client_id,))
    client = cur.fetchone()
    if not client:
        conn.close()
        return jsonify({"error": "Client not found"}), 404
    
    cur.execute("""
        INSERT INTO metrics (client_name, date, weight, waist, bodyfat)
        VALUES (?, ?, ?, ?, ?)
    """, (
        client['name'],
        data.get('date', date.today().isoformat()),
        data.get('weight'),
        data.get('waist'),
        data.get('bodyfat')
    ))
    conn.commit()
    metric_id = cur.lastrowid
    conn.close()
    
    return jsonify({
        "message": "Metric recorded successfully",
        "metric_id": metric_id
    }), 201

# ======================== ERROR HANDLERS ========================
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

# ======================== APPLICATION ENTRY POINT ========================

# Initialize database on app startup (for both pytest and flask run)
try:
    init_db()
except Exception as e:
    pass  # Database might already be initialized

if __name__ == "__main__":
    
    # Run Flask app
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
