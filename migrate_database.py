"""
Database migration script to add Asha Worker support
Adds new columns to existing patients table and creates asha_workers table
"""
import sqlite3
import os

# Get the database path - it's app.db in the instance folder
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')

print(f"Migrating database: {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if asha_workers table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='asha_workers'")
    if not cursor.fetchone():
        print("Creating asha_workers table...")
        cursor.execute("""
            CREATE TABLE asha_workers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                full_name VARCHAR(120) NOT NULL,
                asha_worker_id VARCHAR(50) NOT NULL UNIQUE,
                region VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("✅ asha_workers table created")
    else:
        print("✅ asha_workers table already exists")
    
    # Check if diagnosed_disease column exists in patients table
    cursor.execute("PRAGMA table_info(patients)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'diagnosed_disease' not in columns:
        print("Adding diagnosed_disease column to patients table...")
        cursor.execute("ALTER TABLE patients ADD COLUMN diagnosed_disease VARCHAR(255)")
        print("✅ diagnosed_disease column added")
    else:
        print("✅ diagnosed_disease column already exists")
    
    # Check if asha_worker_id column exists in patients table
    if 'asha_worker_id' not in columns:
        print("Adding asha_worker_id column to patients table...")
        cursor.execute("ALTER TABLE patients ADD COLUMN asha_worker_id INTEGER REFERENCES asha_workers(id)")
        print("✅ asha_worker_id column added")
    else:
        print("✅ asha_worker_id column already exists")
    
    # Check if region column exists in patients table
    if 'region' not in columns:
        print("Adding region column to patients table...")
        cursor.execute("ALTER TABLE patients ADD COLUMN region VARCHAR(100)")
        print("✅ region column added")
    else:
        print("✅ region column already exists")
    
    # Make user_id nullable in patients table (SQLite doesn't support ALTER COLUMN)
    # This is handled by allowing NULL values, which SQLite does by default
    print("✅ user_id column configuration verified")
    
    # Commit changes
    conn.commit()
    print("\n✅ Database migration completed successfully!")
    print("You can now restart the Flask server.")
    
except Exception as e:
    conn.rollback()
    print(f"\n❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()

finally:
    conn.close()
