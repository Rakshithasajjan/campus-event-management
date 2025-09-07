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
4. 
Core Entities:

Colleges: College information

Students: Student profiles linked to colleges

Events: Event details with college association

Registrations: Student event registrations

Attendance: Attendance records

Feedback: Student feedback for attended events


project structure:

<img width="1024" height="1024" alt="Image" src="https://github.com/user-attachments/assets/f9d9247f-2396-44ed-a3f0-c6ed622e1484" />

er diagram:

<img width="1400" height="1200" alt="Image" src="https://github.com/user-attachments/assets/e5b266b0-103a-4c57-abc1-165db851745a" />

<img width="1200" height="1600" alt="Image" src="https://github.com/user-attachments/assets/ac9a09e7-1d83-40a8-a3b3-7e264b9688eb" />

<img width="2000" height="800" alt="Image" src="https://github.com/user-attachments/assets/a41fd526-e554-427a-af4a-ca29a66f4c4b" />

<img width="2000" height="1200" alt="Image" src="https://github.com/user-attachments/assets/1252c5f7-89ba-466b-a3b3-2dae8ea41fa6" />

