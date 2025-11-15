"""
Fix script to make patients.user_id nullable
This allows Asha Workers to add patients without creating user accounts for them
"""
import sqlite3
import os
import shutil
from datetime import datetime

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')

print(f"Fixing database: {db_path}")

if not os.path.exists(db_path):
    print("❌ Database file not found. Please run the application first to create the database.")
    exit(1)

# Create a backup
backup_path = db_path.replace('.db', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
shutil.copy2(db_path, backup_path)
print(f"✅ Backup created: {backup_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check current patients table schema
    cursor.execute("PRAGMA table_info(patients)")
    columns = cursor.fetchall()
    print("\nCurrent patients table schema:")
    for col in columns:
        print(f"  {col[1]}: {col[2]}, NOT NULL: {col[3]}")
    
    # Check if user_id is NOT NULL
    user_id_col = [col for col in columns if col[1] == 'user_id']
    if user_id_col and user_id_col[0][3] == 1:  # notnull flag
        print("\n⚠️  user_id is currently NOT NULL. Fixing...")
        
        # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
        # Step 1: Create new table with correct schema
        cursor.execute("""
            CREATE TABLE patients_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                full_name VARCHAR(120) NOT NULL,
                age INTEGER,
                gender VARCHAR(10),
                phone VARCHAR(20),
                address VARCHAR(255),
                region VARCHAR(100),
                medical_history TEXT,
                diagnosed_disease VARCHAR(255),
                asha_worker_id INTEGER,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (asha_worker_id) REFERENCES asha_workers(id)
            )
        """)
        print("✅ Created new patients table with nullable user_id")
        
        # Step 2: Copy data from old table to new table
        cursor.execute("""
            INSERT INTO patients_new 
            SELECT id, user_id, full_name, age, gender, phone, address, 
                   region, medical_history, diagnosed_disease, asha_worker_id, created_at
            FROM patients
        """)
        print("✅ Copied all existing patient data")
        
        # Step 3: Drop old table
        cursor.execute("DROP TABLE patients")
        print("✅ Dropped old patients table")
        
        # Step 4: Rename new table to patients
        cursor.execute("ALTER TABLE patients_new RENAME TO patients")
        print("✅ Renamed new table to patients")
        
        # Step 5: Recreate indexes if any existed
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_patients_user_id ON patients(user_id) WHERE user_id IS NOT NULL")
        print("✅ Recreated indexes")
        
        # Commit changes
        conn.commit()
        print("\n✅ Database fix completed successfully!")
        print("✅ patients.user_id is now nullable")
        print("✅ Asha Workers can now add patients without user accounts")
        
    else:
        print("\n✅ user_id is already nullable. No changes needed.")
    
    # Verify the fix
    cursor.execute("PRAGMA table_info(patients)")
    columns = cursor.fetchall()
    print("\nUpdated patients table schema:")
    for col in columns:
        print(f"  {col[1]}: {col[2]}, NOT NULL: {col[3]}")
    
except Exception as e:
    conn.rollback()
    print(f"\n❌ Fix failed: {e}")
    import traceback
    traceback.print_exc()
    print(f"\nDatabase backup available at: {backup_path}")
    print("You can restore it if needed by copying it back to app.db")

finally:
    conn.close()

print("\n" + "="*60)
print("IMPORTANT: Restart your Flask application for changes to take effect")
print("="*60)
