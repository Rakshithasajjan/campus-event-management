<<<<<<< HEAD
# Campus Event Management Platform

## My Personal Understanding of the Project

Having worked on this Campus Event Management Platform, I understand this system as a comprehensive solution that bridges the gap between event organizers (college staff) and participants (students). The core problem we're solving is the inefficient manual process of event management that most educational institutions face.

From my perspective, the most critical challenge was designing a scalable system that could handle multiple colleges while maintaining data integrity and providing meaningful insights through reports. I decided to use a centralized database approach rather than separate databases per college because it enables better cross-college analytics and simpler maintenance, which aligns with the scale mentioned in the assignment (50 colleges).

The reporting system is what makes this platform valuable - it transforms raw registration and attendance data into actionable insights. For instance, the event popularity report helps colleges understand which types of events resonate with students, while the student participation report can identify highly engaged students who might be good candidates for leadership roles or special programs.

I chose Flask over more complex frameworks because the assignment emphasizes simplicity and completeness over complexity. SQLite provides the perfect balance of functionality and simplicity for this scale, and the RESTful API design ensures the system can easily integrate with both web admin portals and mobile student apps as mentioned in the scenario.

The database design focuses heavily on relationships and constraints to prevent data inconsistencies - things like duplicate registrations or invalid feedback ratings. This attention to data integrity is crucial for generating reliable reports that administrators can trust for decision-making.

## Features

- **Event Management**: Create and manage campus events with different types (Workshop, Fest, Seminar, Hackathon)
- **Student Registration**: Register students for events with capacity management
- **Attendance Tracking**: Mark student attendance for registered events
- **Feedback System**: Collect and manage student feedback (1-5 rating scale)
- **Comprehensive Reporting**: Generate detailed reports on event popularity, student participation, and engagement metrics
- **Multi-College Support**: Centralized system supporting multiple colleges with unified event IDs

## System Architecture

### Database Design
- **Centralized SQLite Database**: Single database for all colleges enabling cross-college analytics
- **Referential Integrity**: Proper foreign key relationships preventing data inconsistencies
- **Indexed Tables**: Optimized queries with strategic indexes on frequently accessed columns

### API Design
- **RESTful Endpoints**: Standard HTTP methods with JSON responses
- **Resource-Based URLs**: Intuitive endpoint structure following REST conventions
- **Error Handling**: Comprehensive error responses with appropriate HTTP status codes

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Quick Start

1. **Clone/Download the project files**
   ```bash
   # Create project directory
   mkdir campus-event-management
   cd campus-event-management
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   # The database will be automatically created when you first run the app
   python app.py
   ```

4. **Run sample queries (optional)**
   ```bash
   python sample_queries.py
   ```

## Running the Application

### Start the Flask Server
```bash
python app.py
```

The server will start on `http://localhost:5000`

### Test the API
Visit `http://localhost:5000` in your browser to see the API status.

## API Endpoints

### Events
- `POST /api/events` - Create new event
- `GET /api/events` - List all events (supports filtering by type and college)
- `GET /api/events/{id}` - Get specific event details

### Registrations  
- `POST /api/events/{event_id}/register` - Register student for event
- `GET /api/events/{event_id}/registrations` - Get event registrations

### Attendance
- `POST /api/registrations/{registration_id}/attendance` - Mark attendance
- `GET /api/events/{event_id}/attendance` - Get attendance list

### Feedback
- `POST /api/registrations/{registration_id}/feedback` - Submit feedback

### Reports
- `GET /api/reports/event-popularity` - Event popularity report
- `GET /api/reports/student-participation` - Student participation report  
- `GET /api/reports/top-students` - Top 3 most active students

## Sample API Usage

### Create an Event
```bash
curl -X POST http://localhost:5000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "name": "React Workshop",
    "description": "Learn React fundamentals", 
    "event_type": "Workshop",
    "college_id": 1,
    "event_date": "2025-09-15",
    "max_capacity": 50
  }'
```

### Register Student
```bash
curl -X POST http://localhost:5000/api/events/1/register \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1}'
```

### Get Event Popularity Report
```bash
curl http://localhost:5000/api/reports/event-popularity
```

## Database Schema

The system uses 6 main tables:
- **colleges**: College information
- **students**: Student profiles linked to colleges  
- **events**: Event details with college association
- **registrations**: Student-event registration records
- **attendance**: Attendance tracking for registrations
- **feedback**: Student feedback with 1-5 ratings

## Sample Data

The system comes pre-loaded with sample data:
- 3 colleges
- 8 students across colleges
- 6 events of different types
- Sample registrations, attendance, and feedback records

## Reports Generated

### 1. Event Popularity Report
Shows events ranked by registration count with:
- Total registrations and attendance
- Attendance percentage
- Average feedback rating

### 2. Student Participation Report  
Shows student engagement with:
- Total registrations per student
- Events actually attended
- Average feedback ratings given

### 3. Top Students Report
Identifies the 3 most active students based on:
- Number of events attended
- Overall participation metrics
- Engagement quality

### 4. Event Type Analysis
Analyzes performance by event type:
- Total events per type
- Registration and attendance patterns
- Rating comparisons across types

## File Structure

```
campus-event-management/
├── app.py                 # Main Flask application
├── schema.sql            # Database schema definition
├── sample_queries.py     # Sample queries and test script
├── requirements.txt      # Python dependencies
├── README.md            # This documentation
└── campus_events.db     # SQLite database (created automatically)
```

## Testing

Run the sample queries script to test all functionality:

```bash
python sample_queries.py
```

This will:
- Execute all report queries
- Display sample data
- Test API endpoints (if server is running)
- Show system statistics

## Scalability Considerations

**Current Scale**: Designed for 50 colleges × 500 students × 20 events per semester
- Total capacity: ~25,000 students, ~1,000 events, ~100,000 registrations

**Performance Optimizations**:
- Database indexes on frequently queried columns
- Efficient JOIN operations in reports
- Minimal API payload sizes
- Prepared statement usage

**Future Enhancements**:
- Database partitioning for larger scales
- Caching layer for frequently accessed data
- Background job processing for heavy reports
- API authentication and rate limiting

## Error Handling

The system includes comprehensive error handling for:
- Duplicate registrations
- Capacity limit violations  
- Invalid data submissions
- Missing resource references
- Database constraint violations

## Edge Cases Handled

1. **Duplicate Registrations**: Database constraints prevent duplicates
2. **Capacity Limits**: Registration validates against max_capacity
3. **Invalid Ratings**: Database constraints ensure 1-5 range
4. **Missing Data**: Reports handle null values gracefully
5. **Cross-College Operations**: Global event IDs prevent conflicts

---

This system provides a solid foundation for campus event management with room for future enhancements based on specific institutional needs.
=======
# Campus-Event-Management-Platform
>>>>>>> 0794a6a98b26c8f13fb66131f9700e316788456f
