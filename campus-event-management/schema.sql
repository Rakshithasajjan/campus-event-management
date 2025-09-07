-- Campus Event Management Platform Database Schema

-- Colleges Table
CREATE TABLE IF NOT EXISTS colleges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Students Table
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    college_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (college_id) REFERENCES colleges(id)
);

-- Events Table
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    event_type TEXT NOT NULL CHECK (event_type IN ('Workshop', 'Fest', 'Seminar', 'Hackathon')),
    college_id INTEGER NOT NULL,
    event_date DATE NOT NULL,
    max_capacity INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (college_id) REFERENCES colleges(id)
);

-- Registrations Table
CREATE TABLE IF NOT EXISTS registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (event_id) REFERENCES events(id),
    UNIQUE(student_id, event_id)
);

-- Attendance Table
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_id INTEGER NOT NULL,
    attended BOOLEAN DEFAULT FALSE,
    marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (registration_id) REFERENCES registrations(id),
    UNIQUE(registration_id)
);

-- Feedback Table
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
    comments TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (registration_id) REFERENCES registrations(id),
    UNIQUE(registration_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_students_college_id ON students(college_id);
CREATE INDEX IF NOT EXISTS idx_events_college_id ON events(college_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date);
CREATE INDEX IF NOT EXISTS idx_registrations_student_id ON registrations(student_id);
CREATE INDEX IF NOT EXISTS idx_registrations_event_id ON registrations(event_id);
CREATE INDEX IF NOT EXISTS idx_attendance_registration_id ON attendance(registration_id);
CREATE INDEX IF NOT EXISTS idx_feedback_registration_id ON feedback(registration_id);

-- Insert sample data for testing
INSERT OR IGNORE INTO colleges (id, name, location) VALUES 
(1, 'ABC Engineering College', 'Mumbai'),
(2, 'XYZ Institute of Technology', 'Bangalore'),
(3, 'DEF University', 'Delhi');

INSERT OR IGNORE INTO students (id, name, email, college_id) VALUES 
(1, 'Rahul Sharma', 'rahul@abc.edu', 1),
(2, 'Priya Patel', 'priya@abc.edu', 1),
(3, 'Amit Kumar', 'amit@xyz.edu', 2),
(4, 'Sneha Singh', 'sneha@xyz.edu', 2),
(5, 'Vikram Gupta', 'vikram@def.edu', 3),
(6, 'Kavya Rao', 'kavya@def.edu', 3),
(7, 'Arjun Nair', 'arjun@abc.edu', 1),
(8, 'Meera Joshi', 'meera@xyz.edu', 2);

INSERT OR IGNORE INTO events (id, name, description, event_type, college_id, event_date, max_capacity) VALUES 
(1, 'React Workshop', 'Learn React fundamentals', 'Workshop', 1, '2025-09-15', 50),
(2, 'Tech Fest 2025', 'Annual technical festival', 'Fest', 1, '2025-09-20', 200),
(3, 'AI/ML Seminar', 'Introduction to Machine Learning', 'Seminar', 2, '2025-09-18', 75),
(4, 'Code Challenge', '48-hour coding competition', 'Hackathon', 2, '2025-09-25', 100),
(5, 'Web Development Workshop', 'Full-stack development', 'Workshop', 3, '2025-09-22', 60),
(6, 'Innovation Summit', 'Startup and innovation talks', 'Seminar', 3, '2025-09-30', 150);

-- Sample registrations
INSERT OR IGNORE INTO registrations (student_id, event_id, registered_at) VALUES 
(1, 1, '2025-09-01 10:00:00'),
(2, 1, '2025-09-01 11:00:00'),
(3, 3, '2025-09-02 09:00:00'),
(4, 3, '2025-09-02 10:00:00'),
(5, 5, '2025-09-03 08:00:00'),
(1, 2, '2025-09-01 15:00:00'),
(3, 4, '2025-09-02 14:00:00'),
(7, 1, '2025-09-04 12:00:00'),
(8, 3, '2025-09-05 13:00:00');

-- Sample attendance (some attended, some didn't)
INSERT OR IGNORE INTO attendance (registration_id, attended, marked_at) VALUES 
(1, 1, '2025-09-15 09:00:00'),
(2, 1, '2025-09-15 09:05:00'),
(3, 1, '2025-09-18 08:30:00'),
(4, 0, '2025-09-18 08:30:00'),
(5, 1, '2025-09-22 09:00:00'),
(7, 1, '2025-09-25 10:00:00'),
(9, 1, '2025-09-15 09:10:00');

-- Sample feedback
INSERT OR IGNORE INTO feedback (registration_id, rating, comments, submitted_at) VALUES 
(1, 5, 'Excellent workshop! Very informative.', '2025-09-15 18:00:00'),
(2, 4, 'Good content, could use more hands-on examples.', '2025-09-15 19:00:00'),
(3, 5, 'Great speaker and relevant topics.', '2025-09-18 17:00:00'),
(5, 4, 'Well organized event.', '2025-09-22 16:00:00'),
(9, 3, 'Average experience, room was too crowded.', '2025-09-15 20:00:00');