"""
Database Setup Script for Campus Event Management Platform
Run this script first to create the database and populate it with sample data
"""

import sqlite3
import os

DATABASE = 'campus_events.db'

def create_database():
    """Create database and tables with sample data"""
    print("Creating database and tables...")
    
    # Remove existing database if it exists
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
        print("Removed existing database.")
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Read and execute schema
    try:
        with open('schema.sql', 'r') as f:
            schema_sql = f.read()
            cursor.executescript(schema_sql)
            conn.commit()
            print("Database created successfully!")
            print("Sample data loaded!")
    except FileNotFoundError:
        print("Error: schema.sql file not found!")
        print("Make sure schema.sql is in the same directory.")
        return False
    except Exception as e:
        print(f"Error creating database: {e}")
        return False
    finally:
        conn.close()
    
    return True

def verify_database():
    """Verify database was created correctly"""
    print("\nVerifying database creation...")
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Check if tables exist
        tables = cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """).fetchall()
        
        print(f"Created tables: {[table[0] for table in tables]}")
        
        # Check sample data
        counts = {
            'colleges': cursor.execute("SELECT COUNT(*) FROM colleges").fetchone()[0],
            'students': cursor.execute("SELECT COUNT(*) FROM students").fetchone()[0],
            'events': cursor.execute("SELECT COUNT(*) FROM events").fetchone()[0],
            'registrations': cursor.execute("SELECT COUNT(*) FROM registrations").fetchone()[0],
            'attendance': cursor.execute("SELECT COUNT(*) FROM attendance").fetchone()[0],
            'feedback': cursor.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
        }
        
        print("\nSample data loaded:")
        for table, count in counts.items():
            print(f"  {table}: {count} records")
        
        return True
        
    except Exception as e:
        print(f"Error verifying database: {e}")
        return False
    finally:
        conn.close()

def main():
    print("=" * 60)
    print(" CAMPUS EVENT MANAGEMENT - DATABASE SETUP")
    print("=" * 60)
    
    if create_database():
        if verify_database():
            print("\n" + "=" * 60)
            print(" DATABASE SETUP COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("\nYou can now run:")
            print("  python sample_queries.py    # To see reports")
            print("  python app.py              # To start the API server")
            print("  python test_api.py         # To test the API")
            print("  python generate_reports.py # To generate report files")
        else:
            print("\nDatabase verification failed!")
    else:
        print("\nDatabase creation failed!")

if __name__ == "__main__":
    main()