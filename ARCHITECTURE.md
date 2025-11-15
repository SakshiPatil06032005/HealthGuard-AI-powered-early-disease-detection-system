# 🏗️ System Architecture & Integration Guide

## 📋 Complete System Overview

### Technology Stack
```
Frontend Layer
└─ Tailwind CSS + HTML5 + JavaScript
   └─ Responsive Design (Mobile, Tablet, Desktop)

Application Layer
└─ Flask 3.0.0 (Python Web Framework)
   ├─ URL Routing & Request Handling
   ├─ Session Management
   ├─ Template Rendering (Jinja2)
   └─ Blueprint Organization

Business Logic Layer
├─ Authentication (auth.py, auth_routes.py)
├─ Authorization (RBAC decorators)
├─ Dashboard Routes (dashboard_routes.py)
├─ Disease Prediction (disease_model.py)
├─ X-ray Analysis (api.py)
├─ AI Integration (chat.py)
├─ Report Generation (utils.py)
└─ Heatmap Creation (generate_heatmap.py)

Data Layer
├─ SQLAlchemy ORM (Object-Relational Mapping)
├─ SQLite Database (app.db)
│  ├─ users table
│  ├─ admins table
│  ├─ doctors table
│  ├─ patients table
│  ├─ doctor_patient table
│  └─ predictions table
└─ MySQL Ready (PyMySQL driver installed)

AI/ML Layer
├─ Google Generative AI (Gemini 2.0 Flash)
│  └─ Medical Report Generation
├─ scikit-learn (Machine Learning)
│  └─ Future: Disease Prediction Model
├─ OpenCV (Image Processing)
│  └─ X-ray Analysis & Pattern Detection
└─ NumPy & Pandas (Data Processing)
```

---

## 🔐 Authentication Flow

```
                    ┌─────────────────────┐
                    │   User Access       │
                    │ http://localhost:3000
                    └────────────┬────────┘
                                 │
                    ┌────────────▼───────────┐
                    │  Is User Logged In?   │
                    │  (session check)      │
                    └────────────┬───────────┘
                                 │
                ┌────────────────┴────────────────┐
                │                                 │
                ▼ NO                              ▼ YES
        ┌──────────────────┐            ┌──────────────────┐
        │  Show Login Page │            │  Check User Role │
        │  or Register     │            │  (admin/doctor/  │
        └─────────┬────────┘            │   patient)       │
                  │                     └────────┬─────────┘
        ┌─────────▼────────┐                     │
        │  Authenticate    │        ┌────────────┼────────────┐
        │  • Email/Username│        │            │            │
        │  • Password      │        ▼            ▼            ▼
        │  • Hash Check    │    ┌─────────┐ ┌─────────┐ ┌──────────┐
        └────────┬─────────┘    │ Admin   │ │ Doctor  │ │ Patient  │
                 │              │ DBoard  │ │ DBoard  │ │ DBoard   │
        ┌────────▼────────┐    └─────────┘ └─────────┘ └──────────┘
        │ Create Session  │
        │ • user_id       │
        │ • username      │
        │ • user_role     │
        │ • expiry        │
        └────────┬────────┘
                 │
        ┌────────▼─────────────┐
        │ Redirect to Role     │
        │ Specific Dashboard   │
        └──────────────────────┘
```

---

## 👥 Role-Based Access Control (RBAC)

### Role Hierarchy
```
                    ┌───────────────────┐
                    │      ADMIN        │
                    │ (Full System Access)
                    │  • User Management
                    │  • Statistics View
                    │  • System Config
                    └───────────────────┘

                    ┌───────────────────┐
                    │     DOCTOR        │
                    │ (Clinic Access)    
                    │  • Patient List
                    │  • Medical Records
                    │  • Predictions View
                    └───────────────────┘

                    ┌───────────────────┐
                    │     PATIENT       │
                    │ (Personal Access)  
                    │  • Own Dashboard
                    │  • Symptom Checker
                    │  • Medical History
                    └───────────────────┘
```

### Access Control Rules
```
                        Admin   Doctor  Patient
Admin Dashboard          ✅      ❌       ❌
Doctor Dashboard         ❌      ✅       ❌
Patient Dashboard        ❌      ❌       ✅
View All Users          ✅      ❌       ❌
View Own Profile        ✅      ✅       ✅
Use Symptom Checker     ❌      ✅       ✅
View Patient Records    ❌      ✅       ❌
Manage Users            ✅      ❌       ❌
```

---

## 🔄 Request Processing Pipeline

```
HTTP Request
    │
    ▼
┌─────────────────────────┐
│ URL Routing             │
│ (Route Matching)        │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Session Check           │
│ (@login_required)       │
└────────┬────────────────┘
         │ ✓ User Logged In
         ▼
┌─────────────────────────┐
│ Role Verification       │
│ (@role_required)        │
└────────┬────────────────┘
         │ ✓ Correct Role
         ▼
┌─────────────────────────┐
│ Execute Route Handler   │
│ (Query DB, Process)     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Render Template         │
│ (Jinja2 → HTML)         │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ HTTP Response           │
│ (200 OK / 403 Forbidden)
└─────────────────────────┘
```

---

## 📊 Database Schema Relationships

```
                    ┌──────────────┐
                    │    Users     │
                    │              │
                    │ • id (PK)    │
                    │ • username   │
                    │ • email      │
                    │ • password_hash
                    │ • role       │
                    │ • created_at │
                    └────────┬─────┘
                    │        │
            ┌───────┼────┬───┼────┬──────┐
            │       │    │   │    │      │
            ▼ 1:1   ▼    ▼   ▼ 1:1 ▼    ▼ 1:1
      ┌──────────┐ ┌──────────┐ ┌──────────┐
      │ Admins   │ │ Doctors  │ │ Patients │
      │          │ │          │ │          │
      │ • id(PK) │ │ • id(PK) │ │ • id(PK) │
      │ • user_id│ │ • user_id│ │ • user_id│
      │ • name   │ │ • name   │ │ • name   │
      │ • phone  │ │ • spec   │ │ • age    │
      │          │ │ • license│ │ • gender │
      └──────────┘ │          │ │ • address
                   └────┬─────┘ └────┬────┘
                        │            │
                        │            │
                  ┌─────▼────────────▼────┐
                  │  DoctorPatient (M:N)  │
                  │  (Junction Table)     │
                  │                       │
                  │ • id (PK)             │
                  │ • doctor_id (FK)      │
                  │ • patient_id (FK)     │
                  │ • assigned_date       │
                  └───────────────────────┘
                        │
                        │
                        ▼
                  ┌─────────────────┐
                  │  Predictions    │
                  │                 │
                  │ • id (PK)       │
                  │ • patient_id(FK)│
                  │ • doctor_id(FK) │
                  │ • type          │
                  │ • disease       │
                  │ • confidence    │
                  │ • created_at    │
                  └─────────────────┘
```

---

## 🎯 Disease Prediction Flow

```
Patient Input (Symptoms)
    │
    ├─ Fever: ✓
    ├─ Cough: ✓
    ├─ Shortness of Breath: ✓
    ├─ Chest Pain: ❌
    └─ ... (20 more symptoms)
    │
    ▼
┌──────────────────────────────┐
│ Disease Predictor Model      │
│ (disease_model.py)           │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Rule-Based Scoring           │
│ (Demo Implementation)        │
│                              │
│ Scoring System:              │
│ • Fever +15 for COVID-19     │
│ • Cough +15 for Flu          │
│ • SOB +20 for Pneumonia      │
│ • Chest Pain +15 for Pneumonia
│ (Multiple rules applied)     │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Calculate Percentages        │
│ (Normalize Scores)           │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Generate Predictions         │
│                              │
│ 1. Pneumonia      68%   ████░
│ 2. COVID-19       42%   ██░░░
│ 3. Flu            35%   ██░░░
│ 4. Bronchitis     28%   █░░░░
│ 5. Common Cold    22%   █░░░░
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Store Prediction             │
│ (Save to Database)           │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Display Results              │
│ (With Disclaimer)            │
└──────────────────────────────┘
```

---

## 🔗 API Endpoints Structure

### Authentication Routes (`/auth`)
```
POST   /auth/login              Login user
GET    /auth/login              Show login form
POST   /auth/register           Register new patient
GET    /auth/register           Show registration form
POST   /auth/logout             Logout user
GET    /auth/profile            View user profile
POST   /auth/api/check-username Check username availability
POST   /auth/api/check-email    Check email availability
```

### Dashboard Routes (`/dashboard`)
```
GET    /dashboard/admin                     Admin dashboard
GET    /dashboard/doctor                    Doctor dashboard
GET    /dashboard/patient                   Patient dashboard
POST   /dashboard/symptom-prediction        Submit symptoms
GET    /dashboard/symptom-prediction        Show symptom form
GET    /dashboard/doctor/patients/<id>      Patient detail
GET    /dashboard/patient/predictions/<id>  Prediction detail
GET    /api/admin/stats                     Admin stats API
GET    /api/doctor/stats                    Doctor stats API
```

### Main Routes
```
GET    /                        Home page
```

---

## 🛡️ Security Implementation

### Password Security
```
User Input Password
    │
    ▼
┌────────────────────────────┐
│ Password Validation        │
│ • Min 6 characters         │
│ • Not empty                │
│ • Confirm match            │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ Hash Password              │
│ Method: pbkdf2:sha256      │
│ Salt: Random               │
│ Iterations: Default        │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ Store in Database          │
│ (Hashed Password Only)     │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ User Login                 │
│ • Enter password           │
│ • Hash it same way         │
│ • Compare hashes           │
│ • Match = Login Success    │
└────────────────────────────┘
```

### Session Security
```
Session Created
    │
    ├─ user_id: 1
    ├─ username: "john_doe"
    ├─ user_role: "patient"
    │
    ▼
┌────────────────────────────┐
│ Session Cookies            │
│ • HTTPONLY: True           │
│ • SAMESITE: Lax            │
│ • Secure: False (dev)      │
│ • Expires: 24 hours        │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ Stored Server-Side         │
│ (Not in Cookie)            │
│ (Safe from tampering)      │
└────────────────────────────┘
```

---

## 📈 Database Query Flow

### Example: Get Patient's Doctors
```
Route: /dashboard/patient (GET)
         │
         ▼
┌────────────────────────────────┐
│ Get Current Patient            │
│ patient = get_current_patient()│
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Query Database                 │
│ SELECT doctors.*               │
│ FROM doctors                   │
│ JOIN doctor_patient            │
│   ON doctors.id = doctor_patient.doctor_id
│ WHERE doctor_patient.patient_id = ?
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Process Results                │
│ Convert to Python Objects      │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Render Template                │
│ Pass doctors to HTML           │
│ {% for doctor in doctors %}    │
│   {{ doctor.full_name }}       │
│ {% endfor %}                   │
└────────┬───────────────────────┘
         │
         ▼
        HTML Response
```

---

## 🚀 Deployment Architecture

### Current (Development)
```
┌─────────────────┐
│  Developer PC   │
│  (Windows 10)   │
└────────┬────────┘
         │
         ├─ Flask Server (localhost:3000)
         ├─ SQLite Database (app.db)
         ├─ Virtual Environment (venv)
         └─ Static Files (CSS, JS, Images)
```

### Future (Production)
```
┌──────────────────────────┐
│   Internet Users         │
│   (HTTPS)                │
└────────┬─────────────────┘
         │
         ▼
    ┌─────────────────┐
    │  Reverse Proxy  │
    │  (Nginx/Apache) │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────────┐
    │ Application Server  │
    │ (Gunicorn/uWSGI)    │
    └────────┬────────────┘
             │
             ▼
    ┌─────────────────────┐
    │  Flask Application  │
    │  (run.py)           │
    └────────┬────────────┘
             │
        ┌────┴────┐
        ▼         ▼
    ┌────────┐ ┌──────────┐
    │ MySQL  │ │ Redis    │
    │Database│ │ Cache    │
    └────────┘ └──────────┘
```

---

## 🎓 Learning Resources

### Understanding the System

1. **Authentication Flow**
   - Read: `app/auth.py` & `app/auth_routes.py`
   - Understand: Password hashing, sessions

2. **Role-Based Access**
   - Read: Decorators in `app/auth.py`
   - Try: Login as different roles

3. **Database Design**
   - Read: `app/models.py`
   - Understand: Relationships and foreign keys

4. **Disease Prediction**
   - Read: `app/disease_model.py`
   - Understand: Rule-based scoring system

5. **Web Application Flow**
   - Read: `app/routes.py` & `app/dashboard_routes.py`
   - Understand: Request → Response cycle

---

## 🔧 Customization Guide

### Adding New Symptom
1. Edit `app/disease_model.py`
2. Add to `self.feature_names` list
3. Add scoring rules in `_demo_predict()`
4. Update template checkboxes

### Adding New Disease
1. Edit `app/disease_model.py`
2. Add to disease list in `_demo_predict()`
3. Create scoring rules
4. Test with symptom combinations

### Changing Database
1. Edit `app/config.py`
2. Uncomment MySQL line
3. Comment SQLite line
4. Create MySQL database
5. Restart app

### Custom Styling
1. Edit Tailwind classes in templates
2. Or add custom CSS to `app/static/css/`
3. Link in template `<link>` tag

---

## 📞 System Support

### Common Customizations

**Change Port**
- Edit `run.py` → app.run(port=5000)

**Change Theme Color**
- Search "from-blue" in templates
- Replace with your color

**Add New Role**
- Add to `UserRole` enum in `models.py`
- Create new model/dashboard
- Create new decorator

**Add Prediction Type**
- Edit `Prediction` model
- Add logic in `disease_model.py`
- Create new route/template

---

## ✅ Architecture Validation

```
✓ Modular design (blueprints)
✓ Separation of concerns (MVC pattern)
✓ Scalable (easy to add features)
✓ Secure (RBAC, password hashing)
✓ Maintainable (clear structure)
✓ Documented (comments & guides)
✓ Testable (modular functions)
✓ Production-ready (error handling)
```

---

This completes the comprehensive system architecture overview! 🎉
