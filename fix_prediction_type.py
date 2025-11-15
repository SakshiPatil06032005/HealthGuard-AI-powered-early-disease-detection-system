"""
Fix prediction_type column to allow NULL values
"""
import sqlite3
import shutil
from datetime import datetime

# Paths
DB_PATH = "instance/app.db"
BACKUP_PATH = f"instance/app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

print("🔧 Fixing prediction_type NOT NULL constraint...")

# Create backup
print(f"📦 Creating backup: {BACKUP_PATH}")
shutil.copy2(DB_PATH, BACKUP_PATH)
print("✅ Backup created successfully")

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # Check current schema
    cursor.execute("PRAGMA table_info(predictions)")
    columns = cursor.fetchall()
    print("\n📋 Current predictions table schema:")
    for col in columns:
        print(f"  {col[1]}: {col[2]} (NOT NULL: {col[3]})")
    
    # Create new table with nullable prediction_type
    print("\n🔨 Creating new table with nullable prediction_type...")
    cursor.execute("""
        CREATE TABLE predictions_new (
            id INTEGER PRIMARY KEY,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            prediction_type VARCHAR(50),  -- Made nullable
            image_path VARCHAR(255),
            predicted_disease VARCHAR(100),
            confidence FLOAT,
            heatmap_path VARCHAR(255),
            symptoms TEXT,
            predicted_diseases TEXT,
            report_path VARCHAR(255),
            notes TEXT,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (doctor_id) REFERENCES doctors (id)
        )
    """)
    
    # Copy data from old table
    print("📤 Copying existing data...")
    cursor.execute("""
        INSERT INTO predictions_new 
        SELECT * FROM predictions
    """)
    
    # Drop old table
    print("🗑️ Removing old table...")
    cursor.execute("DROP TABLE predictions")
    
    # Rename new table
    print("✏️ Renaming new table...")
    cursor.execute("ALTER TABLE predictions_new RENAME TO predictions")
    
    # Verify the change
    cursor.execute("PRAGMA table_info(predictions)")
    columns = cursor.fetchall()
    print("\n📋 New predictions table schema:")
    for col in columns:
        print(f"  {col[1]}: {col[2]} (NOT NULL: {col[3]})")
    
    # Check prediction_type specifically
    prediction_type_col = [col for col in columns if col[1] == 'prediction_type'][0]
    if prediction_type_col[3] == 0:  # NOT NULL is 0 (False)
        print("\n✅ SUCCESS! prediction_type is now nullable")
    else:
        print("\n⚠️ WARNING: prediction_type is still NOT NULL")
    
    # Commit changes
    conn.commit()
    print("\n✅ Database migration completed successfully!")
    print(f"📁 Backup saved at: {BACKUP_PATH}")
    
except Exception as e:
    print(f"\n❌ Error during migration: {e}")
    conn.rollback()
    print("🔄 Changes rolled back")
    raise
finally:
    conn.close()

print("\n🎉 Done! You can now restart the application.")
