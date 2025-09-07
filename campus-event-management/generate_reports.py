"""
Report Generation Script for Campus Event Management Platform
This script generates JSON and CSV reports and saves them to the reports/ folder
"""

import sqlite3
import json
import csv
import os
from datetime import datetime

DATABASE = 'campus_events.db'
REPORTS_DIR = 'reports'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_reports_directory():
    """Create reports directory if it doesn't exist"""
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
        print(f"Created {REPORTS_DIR}/ directory")

def generate_event_popularity_report():
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
               AVG(CASE WHEN f.rating IS NOT NULL THEN f.rating END) as avg_rating,
               e.max_capacity,
               ROUND(COUNT(r.id) * 100.0 / e.max_capacity, 2) as capacity_utilization
        FROM events e
        JOIN colleges c ON e.college_id = c.id
        LEFT JOIN registrations r ON e.id = r.event_id
        LEFT JOIN attendance a ON r.id = a.registration_id
        LEFT JOIN feedback f ON r.id = f.registration_id
        GROUP BY e.id
        ORDER BY total_registrations DESC, total_attendance DESC
    """).fetchall()
    
    conn.close()
    
    # Convert to list of dictionaries
    report_data = []
    for row in results:
        row_dict = dict(row)
        if row_dict['avg_rating']:
            row_dict['avg_rating'] = round(row_dict['avg_rating'], 2)
        report_data.append(row_dict)
    
    # Generate JSON report
    json_report = {
        "report_name": "Event Popularity Report",
        "generated_at": datetime.now().isoformat(),
        "total_events": len(report_data),
        "summary": {
            "most_popular_event": report_data[0]['name'] if report_data else "N/A",
            "avg_registrations_per_event": round(sum(r['total_registrations'] for r in report_data) / len(report_data), 2) if report_data else 0,
            "overall_attendance_rate": round(sum(r['total_attendance'] for r in report_data) / sum(r['total_registrations'] for r in report_data) * 100, 2) if sum(r['total_registrations'] for r in report_data) > 0 else 0
        },
        "events": report_data
    }
    
    # Save JSON report
    with open(f'{REPORTS_DIR}/event_popularity.json', 'w') as f:
        json.dump(json_report, f, indent=2)
    
    # Save CSV report
    if report_data:
        with open(f'{REPORTS_DIR}/event_popularity.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=report_data[0].keys())
            writer.writeheader()
            writer.writerows(report_data)
    
    return json_report

def generate_student_participation_report():
    """Generate Student Participation Report"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    results = cursor.execute("""
        SELECT s.id, s.name, s.email, c.name as college_name,
               COUNT(r.id) as total_registrations,
               COUNT(CASE WHEN a.attended = 1 THEN 1 END) as events_attended,
               AVG(CASE WHEN f.rating IS NOT NULL THEN f.rating END) as avg_feedback_rating,
               CASE 
                 WHEN COUNT(r.id) > 0 THEN 
                   ROUND(COUNT(CASE WHEN a.attended = 1 THEN 1 END) * 100.0 / COUNT(r.id), 2)
                 ELSE 0 
               END as personal_attendance_rate,
               COUNT(f.id) as feedback_given_count
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
    
    # Convert to list of dictionaries
    report_data = []
    for row in results:
        row_dict = dict(row)
        if row_dict['avg_feedback_rating']:
            row_dict['avg_feedback_rating'] = round(row_dict['avg_feedback_rating'], 2)
        report_data.append(row_dict)
    
    # Generate JSON report
    json_report = {
        "report_name": "Student Participation Report",
        "generated_at": datetime.now().isoformat(),
        "total_active_students": len(report_data),
        "summary": {
            "most_active_student": report_data[0]['name'] if report_data else "N/A",
            "avg_events_per_student": round(sum(r['events_attended'] for r in report_data) / len(report_data), 2) if report_data else 0,
            "avg_registrations_per_student": round(sum(r['total_registrations'] for r in report_data) / len(report_data), 2) if report_data else 0,
            "students_with_perfect_attendance": len([r for r in report_data if r['personal_attendance_rate'] == 100.0])
        },
        "students": report_data
    }
    
    # Save JSON report
    with open(f'{REPORTS_DIR}/student_participation.json', 'w') as f:
        json.dump(json_report, f, indent=2)
    
    # Save CSV report
    if report_data:
        with open(f'{REPORTS_DIR}/student_participation.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=report_data[0].keys())
            writer.writeheader()
            writer.writerows(report_data)
    
    return json_report

def generate_top_students_report():
    """Generate Top 3 Most Active Students Report"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    results = cursor.execute("""
        SELECT s.id, s.name, s.email, c.name as college_name,
               COUNT(r.id) as total_registrations,
               COUNT(CASE WHEN a.attended = 1 THEN 1 END) as events_attended,
               AVG(CASE WHEN f.rating IS NOT NULL THEN f.rating END) as avg_feedback_rating,
               COUNT(f.id) as feedback_submissions,
               CASE 
                 WHEN COUNT(r.id) > 0 THEN 
                   ROUND(COUNT(CASE WHEN a.attended = 1 THEN 1 END) * 100.0 / COUNT(r.id), 2)
                 ELSE 0 
               END as attendance_rate
        FROM students s
        JOIN colleges c ON s.college_id = c.id
        LEFT JOIN registrations r ON s.id = r.student_id
        LEFT JOIN attendance a ON r.id = a.registration_id
        LEFT JOIN feedback f ON r.id = f.registration_id
        GROUP BY s.id
        HAVING COUNT(CASE WHEN a.attended = 1 THEN 1 END) > 0
        ORDER BY events_attended DESC, total_registrations DESC, feedback_submissions DESC
        LIMIT 3
    """).fetchall()
    
    conn.close()
    
    # Convert to list of dictionaries
    report_data = []
    for i, row in enumerate(results, 1):
        row_dict = dict(row)
        row_dict['rank'] = i
        if row_dict['avg_feedback_rating']:
            row_dict['avg_feedback_rating'] = round(row_dict['avg_feedback_rating'], 2)
        report_data.append(row_dict)
    
    # Generate JSON report
    json_report = {
        "report_name": "Top 3 Most Active Students",
        "generated_at": datetime.now().isoformat(),
        "criteria": "Ranked by events attended, then registrations, then feedback submissions",
        "top_students": report_data
    }
    
    # Save JSON report
    with open(f'{REPORTS_DIR}/top_students.json', 'w') as f:
        json.dump(json_report, f, indent=2)
    
    # Save CSV report
    if report_data:
        with open(f'{REPORTS_DIR}/top_students.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=report_data[0].keys())
            writer.writeheader()
            writer.writerows(report_data)
    
    return json_report

def generate_event_type_analysis():
    """Generate Event Type Analysis Report"""
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
               END as attendance_percentage,
               ROUND(COUNT(r.id) * 1.0 / COUNT(e.id), 2) as avg_registrations_per_event,
               MAX(COUNT(r.id)) OVER (PARTITION BY e.event_type) as max_registrations_for_type
        FROM events e
        LEFT JOIN registrations r ON e.id = r.event_id
        LEFT JOIN attendance a ON r.id = a.registration_id
        LEFT JOIN feedback f ON r.id = f.registration_id
        GROUP BY e.event_type
        ORDER BY total_registrations DESC
    """).fetchall()
    
    conn.close()
    
    # Convert to list of dictionaries
    report_data = []
    for row in results:
        row_dict = dict(row)
        if row_dict['avg_rating']:
            row_dict['avg_rating'] = round(row_dict['avg_rating'], 2)
        report_data.append(row_dict)
    
    # Generate JSON report
    json_report = {
        "report_name": "Event Type Analysis",
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "most_popular_type": report_data[0]['event_type'] if report_data else "N/A",
            "total_event_types": len(report_data),
            "best_attended_type": max(report_data, key=lambda x: x['attendance_percentage'])['event_type'] if report_data else "N/A",
            "highest_rated_type": max([r for r in report_data if r['avg_rating']], key=lambda x: x['avg_rating'], default={}).get('event_type', 'N/A')
        },
        "event_types": report_data
    }
    
    # Save JSON report
    with open(f'{REPORTS_DIR}/event_type_analysis.json', 'w') as f:
        json.dump(json_report, f, indent=2)
    
    # Save CSV report
    if report_data:
        with open(f'{REPORTS_DIR}/event_type_analysis.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=report_data[0].keys())
            writer.writeheader()
            writer.writerows(report_data)
    
    return json_report

def generate_college_statistics():
    """Generate College Statistics Report"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    results = cursor.execute("""
        SELECT c.id as college_id, c.name as college_name, c.location,
               COUNT(DISTINCT s.id) as total_students,
               COUNT(DISTINCT e.id) as total_events_hosted,
               COUNT(DISTINCT CASE WHEN r.student_id IN (SELECT id FROM students WHERE college_id = c.id) THEN r.id END) as registrations_by_students,
               COUNT(DISTINCT CASE WHEN r.event_id IN (SELECT id FROM events WHERE college_id = c.id) THEN r.id END) as registrations_for_events,
               COUNT(DISTINCT CASE WHEN a.attended = 1 AND r.student_id IN (SELECT id FROM students WHERE college_id = c.id) THEN a.id END) as attendance_by_students,
               AVG(CASE WHEN f.rating IS NOT NULL AND r.student_id IN (SELECT id FROM students WHERE college_id = c.id) THEN f.rating END) as avg_feedback_by_students
        FROM colleges c
        LEFT JOIN students s ON c.id = s.college_id
        LEFT JOIN events e ON c.id = e.college_id
        LEFT JOIN registrations r ON (s.id = r.student_id OR e.id = r.event_id)
        LEFT JOIN attendance a ON r.id = a.registration_id
        LEFT JOIN feedback f ON r.id = f.registration_id
        GROUP BY c.id
        ORDER BY total_students DESC
    """).fetchall()
    
    conn.close()
    
    # Convert to list of dictionaries
    report_data = []
    for row in results:
        row_dict = dict(row)
        if row_dict['avg_feedback_by_students']:
            row_dict['avg_feedback_by_students'] = round(row_dict['avg_feedback_by_students'], 2)
        
        # Calculate engagement metrics
        if row_dict['total_students'] > 0:
            row_dict['registrations_per_student'] = round(row_dict['registrations_by_students'] / row_dict['total_students'], 2)
            row_dict['attendance_rate'] = round(row_dict['attendance_by_students'] / row_dict['registrations_by_students'] * 100, 2) if row_dict['registrations_by_students'] > 0 else 0
        else:
            row_dict['registrations_per_student'] = 0
            row_dict['attendance_rate'] = 0
        
        report_data.append(row_dict)
    
    # Generate JSON report
    json_report = {
        "report_name": "College Statistics",
        "generated_at": datetime.now().isoformat(),
        "total_colleges": len(report_data),
        "summary": {
            "largest_college": max(report_data, key=lambda x: x['total_students'])['college_name'] if report_data else "N/A",
            "most_active_college": max(report_data, key=lambda x: x['total_events_hosted'])['college_name'] if report_data else "N/A",
            "total_students_across_colleges": sum(r['total_students'] for r in report_data),
            "total_events_across_colleges": sum(r['total_events_hosted'] for r in report_data)
        },
        "colleges": report_data
    }
    
    # Save JSON report
    with open(f'{REPORTS_DIR}/college_statistics.json', 'w') as f:
        json.dump(json_report, f, indent=2)
    
    # Save CSV report
    if report_data:
        with open(f'{REPORTS_DIR}/college_statistics.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=report_data[0].keys())
            writer.writeheader()
            writer.writerows(report_data)
    
    return json_report

def generate_feedback_analysis():
    """Generate Feedback Analysis Report"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Overall feedback statistics
    overall_stats = cursor.execute("""
        SELECT COUNT(*) as total_feedback,
               AVG(rating) as avg_rating,
               COUNT(CASE WHEN rating = 5 THEN 1 END) as five_star,
               COUNT(CASE WHEN rating = 4 THEN 1 END) as four_star,
               COUNT(CASE WHEN rating = 3 THEN 1 END) as three_star,
               COUNT(CASE WHEN rating = 2 THEN 1 END) as two_star,
               COUNT(CASE WHEN rating = 1 THEN 1 END) as one_star,
               COUNT(CASE WHEN comments IS NOT NULL AND comments != '' THEN 1 END) as with_comments
        FROM feedback
    """).fetchone()
    
    # Feedback by event
    event_feedback = cursor.execute("""
        SELECT e.name as event_name, e.event_type, c.name as college_name,
               COUNT(f.id) as feedback_count,
               AVG(f.rating) as avg_rating,
               GROUP_CONCAT(f.comments, '; ') as sample_comments
        FROM events e
        JOIN colleges c ON e.college_id = c.id
        LEFT JOIN registrations r ON e.id = r.event_id
        LEFT JOIN feedback f ON r.id = f.registration_id
        WHERE f.id IS NOT NULL
        GROUP BY e.id
        ORDER BY avg_rating DESC, feedback_count DESC
    """).fetchall()
    
    conn.close()
    
    # Convert results
    overall_dict = dict(overall_stats)
    if overall_dict['avg_rating']:
        overall_dict['avg_rating'] = round(overall_dict['avg_rating'], 2)
    
    event_feedback_list = []
    for row in event_feedback:
        row_dict = dict(row)
        if row_dict['avg_rating']:
            row_dict['avg_rating'] = round(row_dict['avg_rating'], 2)
        # Limit sample comments length
        if row_dict['sample_comments'] and len(row_dict['sample_comments']) > 200:
            row_dict['sample_comments'] = row_dict['sample_comments'][:200] + "..."
        event_feedback_list.append(row_dict)
    
    # Generate JSON report
    json_report = {
        "report_name": "Feedback Analysis",
        "generated_at": datetime.now().isoformat(),
        "overall_statistics": overall_dict,
        "rating_distribution": {
            "5_star": overall_dict['five_star'],
            "4_star": overall_dict['four_star'],
            "3_star": overall_dict['three_star'],
            "2_star": overall_dict['two_star'],
            "1_star": overall_dict['one_star']
        },
        "event_feedback": event_feedback_list
    }
    
    # Save JSON report
    with open(f'{REPORTS_DIR}/feedback_analysis.json', 'w') as f:
        json.dump(json_report, f, indent=2)
    
    # Save CSV report for event feedback
    if event_feedback_list:
        with open(f'{REPORTS_DIR}/feedback_by_event.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=event_feedback_list[0].keys())
            writer.writeheader()
            writer.writerows(event_feedback_list)
    
    return json_report

def generate_summary_dashboard():
    """Generate Executive Summary Dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Key metrics
    metrics = cursor.execute("""
        SELECT 
            (SELECT COUNT(*) FROM colleges) as total_colleges,
            (SELECT COUNT(*) FROM students) as total_students,
            (SELECT COUNT(*) FROM events) as total_events,
            (SELECT COUNT(*) FROM registrations) as total_registrations,
            (SELECT COUNT(*) FROM attendance WHERE attended = 1) as total_attendance,
            (SELECT COUNT(*) FROM feedback) as total_feedback,
            (SELECT AVG(rating) FROM feedback) as avg_rating,
            (SELECT COUNT(*) FROM registrations) - (SELECT COUNT(*) FROM attendance WHERE attended = 1) as no_shows
    """).fetchone()
    
    conn.close()
    
    metrics_dict = dict(metrics)
    
    # Calculate derived metrics
    attendance_rate = round((metrics_dict['total_attendance'] / metrics_dict['total_registrations']) * 100, 2) if metrics_dict['total_registrations'] > 0 else 0
    feedback_rate = round((metrics_dict['total_feedback'] / metrics_dict['total_attendance']) * 100, 2) if metrics_dict['total_attendance'] > 0 else 0
    avg_registrations_per_event = round(metrics_dict['total_registrations'] / metrics_dict['total_events'], 2) if metrics_dict['total_events'] > 0 else 0
    avg_events_per_student = round(metrics_dict['total_registrations'] / metrics_dict['total_students'], 2) if metrics_dict['total_students'] > 0 else 0
    
    if metrics_dict['avg_rating']:
        metrics_dict['avg_rating'] = round(metrics_dict['avg_rating'], 2)
    
    # Generate dashboard report
    dashboard = {
        "report_name": "Executive Summary Dashboard",
        "generated_at": datetime.now().isoformat(),
        "key_metrics": {
            "platform_overview": {
                "total_colleges": metrics_dict['total_colleges'],
                "total_students": metrics_dict['total_students'],
                "total_events": metrics_dict['total_events']
            },
            "engagement_metrics": {
                "total_registrations": metrics_dict['total_registrations'],
                "total_attendance": metrics_dict['total_attendance'],
                "attendance_rate_percentage": attendance_rate,
                "no_shows": metrics_dict['no_shows']
            },
            "feedback_metrics": {
                "total_feedback_submissions": metrics_dict['total_feedback'],
                "feedback_rate_percentage": feedback_rate,
                "average_rating": metrics_dict['avg_rating']
            },
            "efficiency_metrics": {
                "avg_registrations_per_event": avg_registrations_per_event,
                "avg_events_per_student": avg_events_per_student
            }
        },
        "health_indicators": {
            "engagement_health": "Good" if attendance_rate > 70 else "Needs Improvement" if attendance_rate > 50 else "Poor",
            "feedback_health": "Excellent" if feedback_rate > 80 else "Good" if feedback_rate > 60 else "Needs Improvement",
            "satisfaction_health": "Excellent" if metrics_dict['avg_rating'] and metrics_dict['avg_rating'] >= 4.0 else "Good" if metrics_dict['avg_rating'] and metrics_dict['avg_rating'] >= 3.5 else "Needs Improvement"
        }
    }
    
    # Save dashboard report
    with open(f'{REPORTS_DIR}/summary_dashboard.json', 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    return dashboard

def main():
    """Generate all reports"""
    print("=" * 60)
    print(" GENERATING COMPREHENSIVE REPORTS")
    print("=" * 60)
    
    # Ensure reports directory exists
    ensure_reports_directory()
    
    # Generate all reports
    reports = []
    
    print("\n1. Generating Event Popularity Report...")
    reports.append(generate_event_popularity_report())
    
    print("2. Generating Student Participation Report...")
    reports.append(generate_student_participation_report())
    
    print("3. Generating Top Students Report...")
    reports.append(generate_top_students_report())
    
    print("4. Generating Event Type Analysis...")
    reports.append(generate_event_type_analysis())
    
    print("5. Generating College Statistics...")
    reports.append(generate_college_statistics())
    
    print("6. Generating Feedback Analysis...")
    reports.append(generate_feedback_analysis())
    
    print("7. Generating Summary Dashboard...")
    reports.append(generate_summary_dashboard())
    
    print(f"\n{'='*60}")
    print(" REPORT GENERATION COMPLETED")
    print(f"{'='*60}")
    
    print(f"\nAll reports have been saved to the '{REPORTS_DIR}/' directory:")
    print("JSON Reports:")
    for filename in os.listdir(REPORTS_DIR):
        if filename.endswith('.json'):
            print(f"  - {filename}")
    
    print("\nCSV Reports:")
    for filename in os.listdir(REPORTS_DIR):
        if filename.endswith('.csv'):
            print(f"  - {filename}")
    
    print(f"\nTotal files generated: {len(os.listdir(REPORTS_DIR))}")

if __name__ == "__main__":
    main()