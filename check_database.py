"""
Check what tables exist in the database
"""
import sqlite3
import os

# Get the database path - it's in the instance folder as app.db
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')

print(f"Checking database: {db_path}")

if not os.path.exists(db_path):
    print("❌ Database file does not exist!")
    print("The database will be created when you run the Flask app.")
else:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"\n📊 Found {len(tables)} tables:")
    for table in tables:
        table_name = table[0]
        print(f"\n  📋 Table: {table_name}")
        
        # Get columns for this table
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"     Columns:")
        for col in columns:
            print(f"       - {col[1]} ({col[2]})")
    
    conn.close()
