from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)

# Database setup
DATABASE = 'campus_events.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.close()

# Initialize database if it doesn't exist
if not os.path.exists(DATABASE):
    init_db()

@app.route('/')
def index():
    return jsonify({"message": "Campus Event Management API", "status": "running"})

# Event endpoints
@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.get_json()
    
    required_fields = ['name', 'event_type', 'college_id', 'event_date']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO events (name, description, event_type, college_id, event_date, max_capacity)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data['name'],
        data.get('description', ''),
        data['event_type'],
        data['college_id'],
        data['event_date'],
        data.get('max_capacity', 100)
    ))
    
    event_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({"event_id": event_id, "message": "Event created successfully"}), 201

@app.route('/api/events', methods=['GET'])
def get_events():
    event_type = request.args.get('event_type')
    college_id = request.args.get('college_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT e.*, c.name as college_name 
        FROM events e 
        JOIN colleges c ON e.college_id = c.id
        WHERE 1=1
    """
    params = []
    
    if event_type:
        query += " AND e.event_type = ?"
        params.append(event_type)
    
    if college_id:
        query += " AND e.college_id = ?"
        params.append(college_id)
    
    query += " ORDER BY e.event_date DESC"
    
    events = cursor.execute(query, params).fetchall()
    conn.close()
    
    events_list = [dict(event) for event in events]
    return jsonify({"events": events_list})

@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    event = cursor.execute("""
        SELECT e.*, c.name as college_name 
        FROM events e 
        JOIN colleges c ON e.college_id = c.id 
        WHERE e.id = ?
    """, (event_id,)).fetchone()
    
    if not event:
        conn.close()
        return jsonify({"error": "Event not found"}), 404
    
    # Get registration count
    reg_count = cursor.execute(
        "SELECT COUNT(*) as count FROM registrations WHERE event_id = ?",
        (event_id,)
    ).fetchone()['count']
    
    conn.close()
    
    event_dict = dict(event)
    event_dict['registration_count'] = reg_count
    
    return jsonify({"event": event_dict})

# Registration endpoints
@app.route('/api/events/<int:event_id>/register', methods=['POST'])
def register_student(event_id):
    data = request.get_json()
    
    if 'student_id' not in data:
        return jsonify({"error": "Missing student_id"}), 400
    
    student_id = data['student_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if event exists
    event = cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if not event:
        conn.close()
        return jsonify({"error": "Event not found"}), 404
    
    # Check if student exists
    student = cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if not student:
        conn.close()
        return jsonify({"error": "Student not found"}), 404
    
    # Check current registrations vs capacity
    current_registrations = cursor.execute(
        "SELECT COUNT(*) as count FROM registrations WHERE event_id = ?",
        (event_id,)
    ).fetchone()['count']
    
    if current_registrations >= event['max_capacity']:
        conn.close()
        return jsonify({"error": "Event is at full capacity"}), 400
    
    try:
        cursor.execute("""
            INSERT INTO registrations (student_id, event_id)
            VALUES (?, ?)
        """, (student_id, event_id))
        
        registration_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            "registration_id": registration_id,
            "message": "Registration successful"
        }), 201
        
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Student already registered for this event"}), 400

@app.route('/api/events/<int:event_id>/registrations', methods=['GET'])
def get_event_registrations(event_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    registrations = cursor.execute("""
        SELECT r.id, r.registered_at, s.name, s.email, s.college_id,
               COALESCE(a.attended, 0) as attended,
               f.rating, f.comments
        FROM registrations r
        JOIN students s ON r.student_id = s.id
        LEFT JOIN attendance a ON r.id = a.registration_id
        LEFT JOIN feedback f ON r.id = f.registration_id
        WHERE r.event_id = ?
        ORDER BY r.registered_at
    """, (event_id,)).fetchall()
    
    conn.close()
    
    registrations_list = [dict(reg) for reg in registrations]
    return jsonify({"registrations": registrations_list})

# Attendance endpoints
@app.route('/api/registrations/<int:registration_id>/attendance', methods=['POST'])
def mark_attendance(registration_id):
    data = request.get_json()
    attended = data.get('attended', True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if registration exists
    registration = cursor.execute(
        "SELECT * FROM registrations WHERE id = ?",
        (registration_id,)
    ).fetchone()
    
    if not registration:
        conn.close()
        return jsonify({"error": "Registration not found"}), 404
    
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO attendance (registration_id, attended)
            VALUES (?, ?)
        """, (registration_id, attended))
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Attendance marked successfully"})
        
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

# Feedback endpoints
@app.route('/api/registrations/<int:registration_id>/feedback', methods=['POST'])
def submit_feedback(registration_id):
    data = request.get_json()
    
    if 'rating' not in data:
        return jsonify({"error": "Missing rating"}), 400
    
    rating = data['rating']
    comments = data.get('comments', '')
    
    if rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be between 1 and 5"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if registration exists and student attended
    registration = cursor.execute("""
        SELECT r.*, a.attended
        FROM registrations r
        LEFT JOIN attendance a ON r.id = a.registration_id
        WHERE r.id = ?
    """, (registration_id,)).fetchone()
    
    if not registration:
        conn.close()
        return jsonify({"error": "Registration not found"}), 404
    
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO feedback (registration_id, rating, comments)
            VALUES (?, ?, ?)
        """, (registration_id, rating, comments))
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Feedback submitted successfully"})
        
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

# Report endpoints
@app.route('/api/reports/event-popularity', methods=['GET'])
def event_popularity_report():
    event_type = request.args.get('event_type')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT e.id, e.name, e.event_type, e.event_date, c.name as college_name,
               COUNT(r.id) as total_registrations,
               COUNT(CASE WHEN a.attended = 1 THEN 1 END) as total_attendance,
               CASE 
                 WHEN COUNT(r.id) > 0 THEN 
                   ROUND(COUNT(CASE WHEN a.attended = 1 THEN 1 END) * 100.0 / COUNT(r.id), 2)
                 ELSE 0 
               END as attendance_percentage
        FROM events e
        JOIN colleges c ON e.college_id = c.id
        LEFT JOIN registrations r ON e.id = r.event_id
        LEFT JOIN attendance a ON r.id = a.registration_id
        WHERE 1=1
    """
    
    params = []
    if event_type:
        query += " AND e.event_type = ?"
        params.append(event_type)
    
    query += """
        GROUP BY e.id
        ORDER BY total_registrations DESC, total_attendance DESC
    """
    
    events = cursor.execute(query, params).fetchall()
    conn.close()
    
    events_list = [dict(event) for event in events]
    return jsonify({"event_popularity_report": events_list})

@app.route('/api/reports/student-participation', methods=['GET'])
def student_participation_report():
    college_id = request.args.get('college_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT s.id, s.name, s.email, c.name as college_name,
               COUNT(r.id) as total_registrations,
               COUNT(CASE WHEN a.attended = 1 THEN 1 END) as events_attended,
               AVG(CASE WHEN f.rating IS NOT NULL THEN f.rating END) as avg_feedback_rating
        FROM students s
        JOIN colleges c ON s.college_id = c.id
        LEFT JOIN registrations r ON s.id = r.student_id
        LEFT JOIN attendance a ON r.id = a.registration_id
        LEFT JOIN feedback f ON r.id = f.registration_id
        WHERE 1=1
    """
    
    params = []
    if college_id:
        query += " AND s.college_id = ?"
        params.append(college_id)
    
    query += """
        GROUP BY s.id
        HAVING COUNT(r.id) > 0
        ORDER BY events_attended DESC, total_registrations DESC
    """
    
    students = cursor.execute(query, params).fetchall()
    conn.close()
    
    students_list = []
    for student in students:
        student_dict = dict(student)
        if student_dict['avg_feedback_rating']:
            student_dict['avg_feedback_rating'] = round(student_dict['avg_feedback_rating'], 2)
        students_list.append(student_dict)
    
    return jsonify({"student_participation_report": students_list})

@app.route('/api/reports/top-students', methods=['GET'])
def top_students_report():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    students = cursor.execute("""
        SELECT s.id, s.name, s.email, c.name as college_name,
               COUNT(r.id) as total_registrations,
               COUNT(CASE WHEN a.attended = 1 THEN 1 END) as events_attended,
               AVG(CASE WHEN f.rating IS NOT NULL THEN f.rating END) as avg_feedback_rating
        FROM students s
        JOIN colleges c ON s.college_id = c.id
        LEFT JOIN registrations r ON s.id = r.student_id
        LEFT JOIN attendance a ON r.id = a.registration_id
        LEFT JOIN feedback f ON r.id = f.registration_id
        GROUP BY s.id
        HAVING COUNT(CASE WHEN a.attended = 1 THEN 1 END) > 0
        ORDER BY events_attended DESC, total_registrations DESC
        LIMIT 3
    """).fetchall()
    
    conn.close()
    
    students_list = []
    for student in students:
        student_dict = dict(student)
        if student_dict['avg_feedback_rating']:
            student_dict['avg_feedback_rating'] = round(student_dict['avg_feedback_rating'], 2)
        students_list.append(student_dict)
    
    return jsonify({"top_3_students": students_list})

if __name__ == '__main__':
    app.run(debug=True, port=5000)