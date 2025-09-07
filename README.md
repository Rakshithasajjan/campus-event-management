# Campus-Event-Management-Platform
Campus Event Management Platform - Design Document
1. Project Overview
A basic event reporting system for a Campus Event Management Platform that serves ~50 colleges, each with ~500 students and ~20 events per semester.
2. Assumptions & Decisions
Key Assumptions:

Event IDs should be unique across colleges to prevent conflicts
Single centralized database for all colleges (easier management, better analytics)
Each student belongs to one college
Events can have multiple types (Workshop, Fest, Seminar, Hackathon)
Attendance is binary (present/absent)
Feedback is optional and rated 1-5
Students can register for multiple events
One registration per student per event (no duplicates)

Technical Decisions:

Database: SQLite for simplicity and portability
Backend: Python with Flask (lightweight, easy to understand)
API: RESTful endpoints
Data Format: JSON for API responses

3. Data to Track
Core Entities:

Colleges: College information
Students: Student profiles linked to colleges
Events: Event details with college association
Registrations: Student event registrations
Attendance: Attendance records
Feedback: Student feedback for attended events

