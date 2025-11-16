# 📊 DATABASE DOCUMENTATION - AI Disease Prediction System

## 🗄️ **DATABASE TYPE**

### **Primary Database: SQLite**
- **Type:** Relational Database (SQL)
- **File:** `app.db`
- **Size:** Lightweight, embedded database
- **Access:** Local file-based storage

### **Alternative Database: MySQL** (Configured but not active)
- **Type:** Optional production database
- **Connection String:** `mysql+pymysql://root:password@localhost/disease_prediction`
- **Status:** Commented out in config, ready to enable

---

## 📁 **DATABASE LOCATION**

### **SQLite Database File Path:**
```
Project Root/
└── instance/
    └── app.db

Full Path Example:
C:\Users\xh977\OneDrive\Desktop\Final Project (3)\Final Project\AI_Beta Project\
AI-Powered-Early-Disease-Prediction-System-main\
instance\app.db
```

### **Configuration Location:**
```
app/config.py (Lines 23-24)

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

---

## 📋 **DATABASE TABLES**

### **1. USERS Table** (`users`)
**Purpose:** Store all user accounts with authentication

**Columns:**
```
├── id (Integer) - Primary Key
├── username (String) - Unique username
├── email (String) - Unique email address
├── password_hash (String) - Hashed password (pbkdf2:sha256)
├── role (String) - User role (admin, doctor, patient, asha_worker)
├── created_at (DateTime) - Account creation timestamp
└── updated_at (DateTime) - Last update timestamp
```

**Example Data:**
```
ID | Username  | Email           | Role    | Created_At
1  | admin     | admin@...       | admin   | 2025-11-16
2  | mahima    | mahima@...      | patient | 2025-11-16
3  | doctor1   | doctor@...      | doctor  | 2025-11-16
```

---

### **2. ADMINS Table** (`admins`)
**Purpose:** Store administrator profile information

**Columns:**
```
├── id (Integer) - Primary Key
├── user_id (Integer) - Foreign Key → users.id
├── full_name (String) - Administrator name
├── phone (String) - Contact number
└── created_at (DateTime) - Creation timestamp
```

**Relationships:**
- Foreign Key: `user_id` references `users.id`

---

### **3. DOCTORS Table** (`doctors`)
**Purpose:** Store doctor profile and specialization data

**Columns:**
```
├── id (Integer) - Primary Key
├── user_id (Integer) - Foreign Key → users.id
├── full_name (String) - Doctor name
├── specialization (String) - Medical specialization (e.g., Radiologist)
├── phone (String) - Contact number
├── license_number (String) - Medical license (unique)
└── created_at (DateTime) - Creation timestamp
```

**Relationships:**
- Foreign Key: `user_id` references `users.id`
- One-to-Many: Linked to `doctor_patient` table
- One-to-Many: Linked to `predictions` table

---

### **4. PATIENTS Table** (`patients`)
**Purpose:** Store patient health information and medical records

**Columns:**
```
├── id (Integer) - Primary Key
├── user_id (Integer) - Foreign Key → users.id (NULLABLE - for Asha-managed patients)
├── full_name (String) - Patient name
├── age (Integer) - Patient age
├── gender (String) - Gender (M/F/Other)
├── phone (String) - Contact number
├── address (String) - Residential address
├── region (String) - Geographic region (for filtering)
├── medical_history (Text) - Previous medical conditions
├── diagnosed_disease (String) - Current/known diagnosis
├── asha_worker_id (Integer) - Foreign Key → asha_workers.id (NULLABLE)
└── created_at (DateTime) - Record creation timestamp
```

**Relationships:**
- Foreign Key: `user_id` references `users.id` (nullable)
- Foreign Key: `asha_worker_id` references `asha_workers.id` (nullable)
- Many-to-Many: Linked to `doctors` via `doctor_patient` table
- One-to-Many: Linked to `predictions` table

---

### **5. ASHA_WORKERS Table** (`asha_workers`)
**Purpose:** Store Asha Worker (Community Health Worker) information

**Columns:**
```
├── id (Integer) - Primary Key
├── user_id (Integer) - Foreign Key → users.id (UNIQUE)
├── full_name (String) - Worker name
├── asha_worker_id (String) - Official ID (unique)
├── region (String) - Assigned region/area
├── phone (String) - Contact number
└── created_at (DateTime) - Creation timestamp
```

**Relationships:**
- Foreign Key: `user_id` references `users.id`
- One-to-Many: Linked to `patients` table (can manage multiple patients)

---

### **6. DOCTOR_PATIENT Table** (`doctor_patient`)
**Purpose:** Many-to-Many relationship between doctors and patients

**Columns:**
```
├── id (Integer) - Primary Key
├── doctor_id (Integer) - Foreign Key → doctors.id
├── patient_id (Integer) - Foreign Key → patients.id
└── assigned_date (DateTime) - When doctor was assigned to patient
```

**Constraints:**
- Unique constraint: (doctor_id, patient_id) - no duplicate assignments

**Purpose:** Allows one doctor to have multiple patients and one patient to have multiple doctors

---

### **7. PREDICTIONS Table** (`predictions`)
**Purpose:** Store medical predictions from X-ray, MRI, and symptom analysis

**Columns:**
```
├── id (Integer) - Primary Key
├── patient_id (Integer) - Foreign Key → patients.id
├── doctor_id (Integer) - Foreign Key → doctors.id
├── prediction_type (String) - Type ('xray', 'mri', 'symptoms')
├── image_path (String) - Path to uploaded image file
├── predicted_disease (String) - Primary disease predicted
├── confidence (Float) - Confidence percentage (0-100)
├── heatmap_path (String) - Path to Grad-CAM heatmap
├── symptoms (Text) - JSON format: symptoms selected
├── predicted_diseases (Text) - JSON format: all diseases with probabilities
├── notes (Text) - Additional notes/medicine recommendations (JSON)
└── created_at (DateTime) - Prediction timestamp
```

**Relationships:**
- Foreign Key: `patient_id` references `patients.id`
- Foreign Key: `doctor_id` references `doctors.id`

**Data Example:**
```json
{
  "predicted_disease": "Pneumonia",
  "confidence": 0.87,
  "prediction_type": "xray",
  "predicted_diseases": [
    {"disease": "Pneumonia", "confidence": 87.3, "severity": "high"},
    {"disease": "Tuberculosis", "confidence": 12.1, "severity": "moderate"}
  ],
  "notes": {
    "medicines": [...],
    "report_path": "path/to/report.pdf"
  }
}
```

---

## 🔗 **DATABASE RELATIONSHIPS**

### **Entity Relationship Diagram:**

```
User (Base Table)
├── id (PK)
├─→ 1-1 Admin (user_id FK)
├─→ 1-1 Doctor (user_id FK)
├─→ 1-1 Patient (user_id FK)
└─→ 1-1 AshaWorker (user_id FK)

Doctor ←→ Patient (Many-to-Many via doctor_patient)
├── Doctor 1-→ Many Predictions
├── Doctor 1-→ Many DoctorPatient
└── DoctorPatient ←→ Patient

Patient
├── user_id FK → User
├── asha_worker_id FK → AshaWorker
├── 1-→ Many Predictions
└── ←→ Many Doctors (via doctor_patient)

AshaWorker
├── user_id FK → User
└── 1-→ Many Patients

Prediction
├── patient_id FK → Patient
└── doctor_id FK → Doctor
```

---

## 💾 **HOW DATABASE IS USED**

### **1. During Application Startup:**
```python
# File: app/__init__.py
# File: app/config.py

with app.app_context():
    db.create_all()  # Creates all tables if they don't exist
    # Creates: users, admins, doctors, patients, asha_workers, 
    #          doctor_patient, predictions tables
```

**Action:** When Flask app starts, SQLAlchemy automatically creates all tables if missing.

---

### **2. User Registration/Login:**
```python
# File: app/auth_routes.py

# Registration:
user = User(username='mahima', email='mahima@email.com', role='patient')
user.set_password('password123')  # Hash password
db.session.add(user)
db.session.commit()

# Login:
user = User.query.filter_by(username='mahima').first()
if user.check_password('password123'):
    session['user_id'] = user.id
    session['role'] = user.role
```

---

### **3. Doctor-Patient Assignment:**
```python
# File: app/dashboard_routes.py

# Assign doctor to patient
assignment = DoctorPatient(doctor_id=doctor.id, patient_id=patient.id)
db.session.add(assignment)
db.session.commit()

# Query patient's doctors
doctors = db.session.query(Doctor).join(
    DoctorPatient, Doctor.id == DoctorPatient.doctor_id
).filter(DoctorPatient.patient_id == patient_id).all()
```

---

### **4. Medical Predictions (X-ray/MRI/Symptoms):**
```python
# File: app/dashboard_routes.py

# Save X-ray prediction
prediction = Prediction(
    patient_id=patient.id,
    doctor_id=doctor.id,
    prediction_type='xray',
    image_path='XRAY_20251116_123456_image.jpg',
    predicted_disease='Pneumonia',
    confidence=0.876,
    predicted_diseases=json.dumps([
        {'disease': 'Pneumonia', 'confidence': 87.6, 'severity': 'high'},
        {'disease': 'TB', 'confidence': 8.2, 'severity': 'moderate'}
    ]),
    notes=json.dumps({'medicines': [...], 'report_path': '...'})
)
db.session.add(prediction)
db.session.commit()

# Query patient's predictions
predictions = Prediction.query.filter_by(patient_id=patient_id).order_by(
    Prediction.created_at.desc()
).all()
```

---

### **5. Dashboard Queries:**
```python
# File: app/dashboard_routes.py

# Get total statistics
total_users = User.query.count()
total_predictions = Prediction.query.count()
predictions_today = Prediction.query.filter(
    func.date(Prediction.created_at) == datetime.now().date()
).count()

# Get disease distribution
diseases = db.session.query(
    Prediction.predicted_disease,
    func.count(Prediction.id)
).group_by(Prediction.predicted_disease).all()

# Get doctor's patients
doctor = Doctor.query.get(doctor_id)
assigned_patients = db.session.query(Patient).join(
    DoctorPatient, Patient.id == DoctorPatient.patient_id
).filter(DoctorPatient.doctor_id == doctor_id).all()
```

---

## 🔐 **DATABASE SECURITY**

### **Implemented Security Measures:**

1. **Password Hashing:**
   ```python
   user.set_password('password123')  # Uses pbkdf2:sha256 with 1,000,000 iterations
   ```

2. **SQL Injection Prevention:**
   ```python
   # SQLAlchemy ORM prevents SQL injection
   user = User.query.filter_by(username=username).first()  # Safe
   # NOT: SELECT * FROM users WHERE username = 'username'  # Unsafe
   ```

3. **Foreign Key Constraints:**
   - All foreign keys enforce referential integrity
   - Cannot add orphan records

4. **Unique Constraints:**
   - username (unique)
   - email (unique)
   - license_number (unique for doctors)
   - asha_worker_id (unique for Asha workers)

5. **NOT NULL Constraints:**
   - Ensures data quality
   - Prevents incomplete records

---

## 🔄 **DATABASE MIGRATIONS**

### **Migration Scripts Available:**

1. **`migrate_database.py`** - Add Asha Worker support
   ```bash
   python migrate_database.py
   ```
   Adds columns: `asha_worker_id`, `region` to patients table

2. **`fix_patient_user_id.py`** - Make user_id nullable
   ```bash
   python fix_patient_user_id.py
   ```
   Allows patients without user accounts

3. **`check_database.py`** - Inspect database structure
   ```bash
   python check_database.py
   ```
   Lists all tables and columns

---

## 📊 **DATABASE OPERATIONS**

### **Supported Operations:**

| Operation | Code | File |
|-----------|------|------|
| Create Account | `db.session.add(user)` | auth_routes.py |
| Login | `User.query.filter_by(username=...)` | auth_routes.py |
| Save Prediction | `db.session.add(prediction)` | dashboard_routes.py |
| Query Predictions | `Prediction.query.filter_by(...)` | dashboard_routes.py |
| Assign Doctor | `db.session.add(doctor_patient)` | dashboard_routes.py |
| Get Statistics | `db.session.query(...).count()` | dashboard_routes.py |

---

## ⚙️ **DATABASE CONFIGURATION**

### **In `app/config.py`:**

```python
# SQLite (Default)
SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'

# MySQL (Alternative - uncomment to use)
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost/disease_prediction'

# ORM Settings
SQLALCHEMY_TRACK_MODIFICATIONS = False  # Don't track object changes
SQLALCHEMY_ECHO = False                  # Don't log SQL queries
```

### **To Switch to MySQL:**
1. Edit `app/config.py`
2. Comment out SQLite line
3. Uncomment MySQL line
4. Update connection credentials
5. Restart Flask app

---

## 📈 **DATABASE SIZE & PERFORMANCE**

### **SQLite Considerations:**
- ✅ Good for development
- ✅ Lightweight (single file)
- ✅ No server required
- ❌ Limited concurrent users
- ❌ Slower with large datasets

### **When to Upgrade to MySQL:**
- Production deployment
- Expected 100+ concurrent users
- Large dataset (>10GB)
- Need for horizontal scaling

---

## 🔍 **CHECKING DATABASE STATUS**

### **View Database Contents:**
```python
python check_database.py
```

Output shows:
- All table names
- All columns in each table
- Data types for each column
- Total row count per table

### **View Specific Table:**
```python
from app import create_app, db
from app.models import User, Prediction

app = create_app()
with app.app_context():
    # Count users
    users = User.query.all()
    print(f"Users: {len(users)}")
    
    # Count predictions
    preds = Prediction.query.all()
    print(f"Predictions: {len(preds)}")
    
    # List all predictions
    for pred in preds:
        print(f"- {pred.predicted_disease}: {pred.confidence}%")
```

---

## 📂 **BACKUP & RECOVERY**

### **Backup SQLite Database:**
```bash
# Manual backup
copy instance\app.db instance\app_backup_20251116.db

# Python backup
import shutil
shutil.copy2('instance/app.db', 'instance/app_backup.db')
```

### **Restore from Backup:**
```bash
copy instance\app_backup.db instance\app.db
```

### **Backup Scripts:**
- `migrate_database.py` automatically creates backup when migrating
- Use `fix_patient_user_id.py` which also backs up database

---

## 🎯 **SUMMARY**

| Aspect | Details |
|--------|---------|
| **Database Type** | SQLite (default), MySQL (optional) |
| **Location** | `instance/app.db` |
| **Number of Tables** | 7 main tables |
| **Total Records** | Variable (demo: ~20-50 records) |
| **ORM Used** | SQLAlchemy |
| **Security** | Password hashing, SQL injection prevention, constraints |
| **Relationships** | Complex relationships with foreign keys |
| **Backup** | Manual copy or script-based |
| **Migration** | Scripts available for schema updates |

---

**Database Documentation Version:** 1.0  
**Last Updated:** November 16, 2025  
**System:** AI-Powered Early Disease Prediction System
