"""
API Testing Script for Campus Event Management Platform
This script tests all API endpoints with sample data
"""

import requests
import json
import time
from datetime import datetime, date

BASE_URL = "http://localhost:5000"

def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Test a single API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data)
        elif method.upper() == 'DELETE':
            response = requests.delete(url)
        
        success = response.status_code == expected_status
        status_icon = "✓" if success else "✗"
        
        print(f"{status_icon} {method} {endpoint} - Status: {response.status_code}")
        
        if success and response.content:
            try:
                result = response.json()
                return result
            except:
                return response.text
        elif not success:
            print(f"   Error: {response.text}")
            
        return None
        
    except requests.exceptions.ConnectionError:
        print(f"✗ Connection Error: Make sure the server is running on {BASE_URL}")
        return None
    except Exception as e:
        print(f"✗ Error testing {endpoint}: {str(e)}")
        return None

def run_comprehensive_tests():
    """Run comprehensive API tests"""
    
    print("=" * 60)
    print(" CAMPUS EVENT MANAGEMENT API TESTING")
    print("=" * 60)
    
    # Test basic connectivity
    print("\n1. Testing Basic Connectivity")
    print("-" * 30)
    test_endpoint('GET', '/')
    
    # Test getting events
    print("\n2. Testing Event Endpoints")
    print("-" * 30)
    events_result = test_endpoint('GET', '/api/events')
    
    # Test creating a new event
    new_event_data = {
        "name": "API Test Workshop",
        "description": "Testing event creation via API",
        "event_type": "Workshop",
        "college_id": 1,
        "event_date": "2025-10-30",
        "max_capacity": 25
    }
    
    create_result = test_endpoint('POST', '/api/events', new_event_data, 201)
    new_event_id = None
    if create_result:
        new_event_id = create_result.get('event_id')
        print(f"   Created event with ID: {new_event_id}")
    
    # Test getting specific event
    if new_event_id:
        test_endpoint('GET', f'/api/events/{new_event_id}')
    
    # Test filtering events
    test_endpoint('GET', '/api/events?event_type=Workshop')
    test_endpoint('GET', '/api/events?college_id=1')
    
    # Test registration endpoints
    print("\n3. Testing Registration Endpoints")
    print("-" * 30)
    
    if new_event_id:
        # Test student registration
        registration_data = {"student_id": 1}
        reg_result = test_endpoint('POST', f'/api/events/{new_event_id}/register', 
                                  registration_data, 201)
        
        registration_id = None
        if reg_result:
            registration_id = reg_result.get('registration_id')
            print(f"   Created registration with ID: {registration_id}")
        
        # Test duplicate registration (should fail)
        test_endpoint('POST', f'/api/events/{new_event_id}/register', 
                     registration_data, 400)
        
        # Register another student
        reg_data_2 = {"student_id": 2}
        reg_result_2 = test_endpoint('POST', f'/api/events/{new_event_id}/register', 
                                    reg_data_2, 201)
        
        # Get event registrations
        test_endpoint('GET', f'/api/events/{new_event_id}/registrations')
        
        # Test attendance endpoints
        print("\n4. Testing Attendance Endpoints")
        print("-" * 30)
        
        if registration_id:
            # Mark attendance
            attendance_data = {"attended": True}
            test_endpoint('POST', f'/api/registrations/{registration_id}/attendance', 
                         attendance_data)
            
            # Update attendance
            attendance_data_update = {"attended": False}
            test_endpoint('POST', f'/api/registrations/{registration_id}/attendance', 
                         attendance_data_update)
            
            # Mark attendance for second student
            if reg_result_2:
                reg_id_2 = reg_result_2.get('registration_id')
                test_endpoint('POST', f'/api/registrations/{reg_id_2}/attendance', 
                             {"attended": True})
        
        # Test feedback endpoints
        print("\n5. Testing Feedback Endpoints")
        print("-" * 30)
        
        if registration_id:
            # Submit feedback
            feedback_data = {
                "rating": 4,
                "comments": "Great workshop, learned a lot!"
            }
            test_endpoint('POST', f'/api/registrations/{registration_id}/feedback', 
                         feedback_data)
            
            # Test invalid rating
            invalid_feedback = {"rating": 6, "comments": "Invalid rating test"}
            test_endpoint('POST', f'/api/registrations/{registration_id}/feedback', 
                         invalid_feedback, 400)
            
            # Update feedback
            updated_feedback = {
                "rating": 5,
                "comments": "Updated: Excellent workshop!"
            }
            test_endpoint('POST', f'/api/registrations/{registration_id}/feedback', 
                         updated_feedback)
    
    # Test report endpoints
    print("\n6. Testing Report Endpoints")
    print("-" * 30)
    
    # Event popularity report
    popularity_result = test_endpoint('GET', '/api/reports/event-popularity')
    if popularity_result:
        print(f"   Found {len(popularity_result.get('event_popularity_report', []))} events in popularity report")
    
    # Filtered event popularity report
    test_endpoint('GET', '/api/reports/event-popularity?event_type=Workshop')
    
    # Student participation report
    participation_result = test_endpoint('GET', '/api/reports/student-participation')
    if participation_result:
        print(f"   Found {len(participation_result.get('student_participation_report', []))} students in participation report")
    
    # Filtered student participation report
    test_endpoint('GET', '/api/reports/student-participation?college_id=1')
    
    # Top students report
    top_result = test_endpoint('GET', '/api/reports/top-students')
    if top_result:
        print(f"   Found {len(top_result.get('top_3_students', []))} students in top students report")
    
    # Test error cases
    print("\n7. Testing Error Cases")
    print("-" * 30)
    
    # Non-existent event
    test_endpoint('GET', '/api/events/99999', expected_status=404)
    
    # Invalid student registration
    test_endpoint('POST', '/api/events/1/register', {"student_id": 99999}, 404)
    
    # Non-existent registration for attendance
    test_endpoint('POST', '/api/registrations/99999/attendance', {"attended": True}, 404)
    
    # Non-existent registration for feedback
    test_endpoint('POST', '/api/registrations/99999/feedback', {"rating": 5}, 404)
    
    print("\n" + "=" * 60)
    print(" API TESTING COMPLETED")
    print("=" * 60)

def display_sample_data():
    """Display some sample data from the API"""
    
    print("\n" + "=" * 60)
    print(" SAMPLE DATA FROM API")
    print("=" * 60)
    
    # Get and display events
    print("\nSample Events:")
    events_result = test_endpoint('GET', '/api/events')
    if events_result and 'events' in events_result:
        for event in events_result['events'][:3]:  # Show first 3
            print(f"  - {event['name']} ({event['event_type']}) - {event['event_date']}")
    
    # Get and display event popularity report
    print("\nEvent Popularity Report (Top 3):")
    popularity_result = test_endpoint('GET', '/api/reports/event-popularity')
    if popularity_result and 'event_popularity_report' in popularity_result:
        for i, event in enumerate(popularity_result['event_popularity_report'][:3], 1):
            print(f"  {i}. {event['name']} - {event['total_registrations']} registrations, "
                  f"{event['attendance_percentage']}% attendance")
    
    # Get and display top students
    print("\nTop 3 Most Active Students:")
    top_result = test_endpoint('GET', '/api/reports/top-students')
    if top_result and 'top_3_students' in top_result:
        for i, student in enumerate(top_result['top_3_students'], 1):
            print(f"  {i}. {student['name']} - {student['events_attended']} events attended")

def main():
    """Main testing function"""
    
    print("Starting API Testing...")
    print("Make sure the Flask server is running: python app.py")
    print()
    
    # Wait a moment for user to start server if needed
    input("Press Enter to continue with testing...")
    
    # Run comprehensive tests
    run_comprehensive_tests()
    
    # Display sample data
    display_sample_data()
    
    print("\n\nTesting completed! Check the output above for any failures.")
    print("If you see connection errors, make sure to run 'python app.py' first.")

if __name__ == "__main__":
    main()