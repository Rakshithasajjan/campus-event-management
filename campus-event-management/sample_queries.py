"""
Sample queries and test script for the Campus Event Management Platform
Run this script to test database functionality and generate sample reports
"""

import sqlite3
import json
from datetime import datetime

DATABASE = 'campus_events.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_results(title, results):
    print(f"\n{title}:")
    print("-" * len(title))
    if not results:
        print("No data found.")
        return
    
    for i, row in enumerate(results, 1):
        print(f"{i}. {dict(row)}")

def query_event_popularity():
    """Generate Event Popularity Report"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    results = cursor.execute("""
        SELECT e.id, e.name, e.event_type, e.event_date, c.name as college_name,
               COUNT(r.id) as total_registrations,
               COUNT(CASE WHEN a.attended = 1 THEN 1 END) as total_attendance,
               CASE 
                 WHEN COUNT(r.id) > 0 THEN 
                   ROUND(COUNT(CASE WHEN a.attended = 1 THEN 1 END) * 100.0 / COUNT(r.id), 2)
                 ELSE 0 
               END as attendance_percentage,
               AVG(CASE WHEN f.rating IS NOT NULL THEN f.rating END) as avg_rating
        FROM events e
        JOIN colleges c ON e.college_id = c.id
        LEFT JOIN registrations r ON e.id = r.event_id
        LEFT JOIN attendance a ON r.id = a.registration_id
        LEFT JOIN feedback f ON r.id = f.registration_id
        GROUP BY e.id
        ORDER BY total_registrations DESC, total_attendance DESC
    """).fetchall()
    
    conn.close()
    return results

def query_student_participation():
    """Generate Student Participation Report"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    results = cursor.execute("""
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
        HAVING COUNT(r.id) > 0
        ORDER BY events_attended DESC, total_registrations DESC
    """).fetchall()
    
    conn.close()
    return results

def query_top_students():
    """Get Top 3 Most Active Students"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    results = cursor.execute("""
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
    return results

def query_event_type_analysis():
    """Analyze events by type"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    results = cursor.execute("""
        SELECT e.event_type,
               COUNT(e.id) as total_events,
               COUNT(r.id) as total_registrations,
               COUNT(CASE WHEN a.attended = 1 THEN 1 END) as total_attendance,
               AVG(CASE WHEN f.rating IS NOT NULL THEN f.rating END) as avg_rating,
               CASE 
                 WHEN COUNT(r.id) > 0 THEN 
                   ROUND(COUNT(CASE WHEN a.attended = 1 THEN 1 END) * 100.0 / COUNT(r.id), 2)
                 ELSE 0 
               END as attendance_percentage
        FROM events e
        LEFT JOIN registrations r ON e.id = r.event_id
        LEFT JOIN attendance a ON r.id = a.registration_id
        LEFT JOIN feedback f ON r.id = f.registration_id
        GROUP BY e.event_type
        ORDER BY total_registrations DESC
    """).fetchall()
    
    conn.close()
    return results

def query_college_statistics():
    """Get statistics by college"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    results = cursor.execute("""
        SELECT c.name as college_name,
               COUNT(DISTINCT s.id) as total_students,
               COUNT(DISTINCT e.id) as total_events,
               COUNT(r.id) as total_registrations,
               COUNT(CASE WHEN a.attended = 1 THEN 1 END) as total_attendance
        FROM colleges c
        LEFT JOIN students s ON c.id = s.college_id
        LEFT JOIN events e ON c.id = e.college_id
        LEFT JOIN registrations r ON (s.id = r.student_id OR e.id = r.event_id)
        LEFT JOIN attendance a ON r.id = a.registration_id
        GROUP BY c.id
        ORDER BY total_registrations DESC
    """).fetchall()
    
    conn.close()
    return results

def test_api_functionality():
    """Test core API functionality with sample data"""
    import requests
    import time
    
    base_url = "http://localhost:5000"
    
    print("\nTesting API Endpoints...")
    print("-" * 30)
    
    # Test creating a new event
    event_data = {
        "name": "Python Workshop",
        "description": "Learn Python basics",
        "event_type": "Workshop",
        "college_id": 1,
        "event_date": "2025-10-15",
        "max_capacity": 30
    }
    
    try:
        response = requests.post(f"{base_url}/api/events", json=event_data)
        if response.status_code == 201:
            print("✓ Event creation: SUCCESS")
            new_event_id = response.json()['event_id']
        else:
            print(f"✗ Event creation: FAILED ({response.status_code})")
            return
        
        # Test student registration
        registration_data = {"student_id": 1}
        response = requests.post(f"{base_url}/api/events/{new_event_id}/register", json=registration_data)
        if response.status_code == 201:
            print("✓ Student registration: SUCCESS")
            registration_id = response.json()['registration_id']
        else:
            print(f"✗ Student registration: FAILED ({response.status_code})")
            return
        
        # Test attendance marking
        attendance_data = {"attended": True}
        response = requests.post(f"{base_url}/api/registrations/{registration_id}/attendance", json=attendance_data)
        if response.status_code == 200:
            print("✓ Attendance marking: SUCCESS")
        else:
            print(f"✗ Attendance marking: FAILED ({response.status_code})")
        
        # Test feedback submission
        feedback_data = {"rating": 4, "comments": "Good workshop"}
        response = requests.post(f"{base_url}/api/registrations/{registration_id}/feedback", json=feedback_data)
        if response.status_code == 200:
            print("✓ Feedback submission: SUCCESS")
        else:
            print(f"✗ Feedback submission: FAILED ({response.status_code})")
        
        # Test reports
        response = requests.get(f"{base_url}/api/reports/event-popularity")
        if response.status_code == 200:
            print("✓ Event popularity report: SUCCESS")
        else:
            print(f"✗ Event popularity report: FAILED ({response.status_code})")
        
    except requests.exceptions.ConnectionError:
        print("✗ API testing: Server not running. Start the Flask app first with: python app.py")

def main():
    """Run all sample queries and generate reports"""
    
    print_section("CAMPUS EVENT MANAGEMENT PLATFORM - REPORTS")
    
    # Event Popularity Report
    print_section("EVENT POPULARITY REPORT")
    results = query_event_popularity()
    for i, row in enumerate(results, 1):
        row_dict = dict(row)
        print(f"""
{i}. Event: {row_dict['name']} ({row_dict['event_type']})
   College: {row_dict['college_name']}
   Date: {row_dict['event_date']}
   Registrations: {row_dict['total_registrations']}
   Attendance: {row_dict['total_attendance']}
   Attendance %: {row_dict['attendance_percentage']}%
   Avg Rating: {round(row_dict['avg_rating'], 2) if row_dict['avg_rating'] else 'N/A'}
        """)
    
    # Student Participation Report
    print_section("STUDENT PARTICIPATION REPORT")
    results = query_student_participation()
    for i, row in enumerate(results, 1):
        row_dict = dict(row)
        print(f"""
{i}. Student: {row_dict['name']} ({row_dict['email']})
   College: {row_dict['college_name']}
   Total Registrations: {row_dict['total_registrations']}
   Events Attended: {row_dict['events_attended']}
   Avg Feedback Rating: {round(row_dict['avg_feedback_rating'], 2) if row_dict['avg_feedback_rating'] else 'N/A'}
        """)
    
    # Top 3 Students
    print_section("TOP 3 MOST ACTIVE STUDENTS")
    results = query_top_students()
    for i, row in enumerate(results, 1):
        row_dict = dict(row)
        print(f"""
{i}. Student: {row_dict['name']} ({row_dict['email']})
   College: {row_dict['college_name']}
   Total Registrations: {row_dict['total_registrations']}
   Events Attended: {row_dict['events_attended']}
   Avg Feedback Rating: {round(row_dict['avg_feedback_rating'], 2) if row_dict['avg_feedback_rating'] else 'N/A'}
        """)
    
    # Event Type Analysis
    print_section("EVENT TYPE ANALYSIS")
    results = query_event_type_analysis()
    for i, row in enumerate(results, 1):
        row_dict = dict(row)
        print(f"""
{i}. Event Type: {row_dict['event_type']}
   Total Events: {row_dict['total_events']}
   Total Registrations: {row_dict['total_registrations']}
   Total Attendance: {row_dict['total_attendance']}
   Attendance %: {row_dict['attendance_percentage']}%
   Avg Rating: {round(row_dict['avg_rating'], 2) if row_dict['avg_rating'] else 'N/A'}
        """)
    
    # College Statistics
    print_section("COLLEGE STATISTICS")
    results = query_college_statistics()
    for i, row in enumerate(results, 1):
        row_dict = dict(row)
        print(f"""
{i}. College: {row_dict['college_name']}
   Total Students: {row_dict['total_students']}
   Total Events: {row_dict['total_events']}
   Total Registrations: {row_dict['total_registrations']}
   Total Attendance: {row_dict['total_attendance']}
        """)
    
    # Test API functionality
    print_section("API TESTING")
    test_api_functionality()
    
    print_section("REPORTS COMPLETED")
    print("All reports have been generated successfully!")
    print("\nTo test the API manually:")
    print("1. Run: python app.py")
    print("2. Visit: http://localhost:5000")
    print("3. Use the API endpoints for testing")

if __name__ == "__main__":
    main()