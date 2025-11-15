# ⚡ Quick Start Guide

## 🚀 Start the Application (Already Running!)

The Flask server is already running at **http://localhost:3000**

### To Access the System

1. **Open your browser** and go to:
   ```
   http://localhost:3000
   ```

2. **Click "Login"** on the homepage

3. **Choose Your Role** to test:

## 👤 Test Accounts

### Admin (System Administrator)
```
Username: admin
Password: admin123
```
**What you'll see**: Admin Dashboard with system statistics, user management, and system overview

### Doctor (Medical Professional)
```
Username: mahima
Password: mahima
```
**What you'll see**: Doctor Dashboard with assigned patients list and medical record management

### Patient (Healthcare Consumer)
```
Username: john_doe
Password: patient123
```
**What you'll see**: Patient Dashboard with health records and symptom checker

---

## 📱 Key Features to Try

### For Patients
1. **Login** as `john_doe` / `patient123`
2. **Click** "Symptom Checker" button
3. **Select** symptoms (e.g., fever, cough, fatigue)
4. **Click** "Check Symptoms" button
5. **View** disease predictions with confidence scores

### For Doctors
1. **Login** as `mahima` / `mahima`
2. **See** list of assigned patients
3. **Click** "View Records" to see patient details
4. **Review** prediction history

### For Admin
1. **Login** as `admin` / `admin123`
2. **View** system statistics
3. **See** total users, doctors, patients
4. **View** doctor and patient lists

---

## 🔑 Additional Demo Accounts

**More Doctors:**
- Username: `drsmith` | Password: `doctor123`
- Username: `drbrown` | Password: `doctor123`

**More Patients:**
- Username: `jane_smith` | Password: `patient123`
- Username: `mike_johnson` | Password: `patient123`

---

## 📝 New User Registration

You can also create your own account:

1. Click **"Register here"** link on login page
2. Fill in your details:
   - Full Name
   - Username
   - Email
   - Age & Gender
   - Password
3. Click **"Create Account"**
4. Login with your new credentials

---

## 🛠️ Stop the Server

To stop the server, press **CTRL+C** in the terminal

---

## 🔧 Restart the Server

If you need to restart:

```bash
cd "C:\Users\xh977\OneDrive\Desktop\Hackthon\AI-Powered-Early-Disease-Prediction-System-main"
.\venv\Scripts\python.exe run.py
```

---

## 📊 What's Included

✅ **Three Role-Based Dashboards**
- Admin: System overview
- Doctor: Patient management
- Patient: Health records

✅ **User Authentication**
- Secure login/registration
- Password protection
- Session management

✅ **AI Symptom Checker**
- 20+ symptoms
- 5 predicted diseases
- Confidence scoring

✅ **Medical Database**
- User profiles
- Patient records
- Prediction history
- Doctor assignments

✅ **Professional UI**
- Responsive design
- Medical branding
- Easy navigation
- Tailwind CSS styling

---

## 🎯 Workflow Example: Patient Using Symptom Checker

```
1. Patient logs in
   └─→ Patient Dashboard loads

2. Patient clicks "Symptom Checker"
   └─→ Symptom selection page opens

3. Patient selects symptoms:
   ✓ Fever
   ✓ Cough
   ✓ Shortness of breath
   ✗ Nausea

4. Patient clicks "Check Symptoms"
   └─→ AI analyzes selected symptoms

5. Results display:
   🟢 Pneumonia (68%)
   🟡 COVID-19 (42%)
   🟠 Flu (35%)
   🔵 Bronchitis (28%)

6. Patient can:
   ✓ View full prediction details
   ✓ Save prediction to history
   ✓ Share with doctor
```

---

## 🔐 Security Notes

⚠️ **Demo System Features:**
- Passwords hashed and secure
- Role-based access control active
- Session timeouts enabled
- SQL injection prevention (SQLAlchemy ORM)

✅ **Your Data:**
- Stored locally in SQLite database
- Only accessible via login
- Different permissions per role

---

## 📞 Troubleshooting

### Issue: Can't access http://localhost:3000
**Solution:**
- Make sure server is still running
- Check terminal for error messages
- Try `http://127.0.0.1:3000` instead

### Issue: Forgot password
**Solution:**
- Currently a demo system
- Re-run setup to reset demo data:
  ```bash
  python -c "from setup import setup_demo_data; setup_demo_data()"
  ```

### Issue: Database error
**Solution:**
- Delete `app.db` file
- Restart the server
- Database will auto-recreate with demo data

### Issue: Symptoms not predicting correctly
**Solution:**
- This is expected! The demo uses rule-based logic
- Multiple symptoms together give better results
- Try: fever + cough + shortness of breath for pneumonia

---

## 🎓 System Architecture

```
┌─────────────────────────────────────────┐
│         User Browser                     │
│    (http://localhost:3000)               │
└──────────────────┬──────────────────────┘
                   │
                   ↓
        ┌──────────────────────┐
        │  Flask Application   │
        │  (run.py on port 3000)
        └──────────┬───────────┘
                   │
        ┌──────────┴──────────┐
        ↓                     ↓
    ┌────────┐           ┌──────────┐
    │ Routes │           │ Database │
    │        │           │ (SQLite) │
    │• Auth  │           │          │
    │• Admin │           │ Users    │
    │• Doctor│           │ Doctors  │
    │• Patient           │ Patients │
    │• Symptom           │ Records  │
    └────────┘           └──────────┘
        │
        ├─→ AI Models
        │   • Gemini (Reports)
        │   • Disease Prediction
        │   • Image Analysis
        │
        └─→ Templates
            • HTML Pages
            • Tailwind CSS
            • Charts.js
```

---

## 📚 Files You Might Find Interesting

### Core Application Files
- `run.py` - Starts the server
- `app/__init__.py` - Flask app setup
- `app/models.py` - Database models (User, Doctor, Patient, etc.)
- `app/config.py` - Configuration settings

### Routes & Logic
- `app/auth_routes.py` - Login, registration, logout
- `app/dashboard_routes.py` - Admin, doctor, patient dashboards
- `app/disease_model.py` - Symptom-based disease prediction
- `app/api.py` - X-ray analysis API

### Templates (HTML)
- `app/templates/auth/login.html` - Login page
- `app/templates/auth/register.html` - Registration page
- `app/templates/dashboards/admin_dashboard.html` - Admin view
- `app/templates/dashboards/doctor_dashboard.html` - Doctor view
- `app/templates/dashboards/patient_dashboard.html` - Patient view
- `app/templates/dashboards/symptom_prediction.html` - Symptom checker

### Documentation
- `IMPLEMENTATION_GUIDE.md` - Detailed features & setup
- `COMPLETION_SUMMARY.md` - What was built
- `README.md` - General overview

---

## 🎉 You're All Set!

Your AI-Powered Disease Prediction System is ready to use!

### Next Steps:
1. ✅ Server is running
2. ✅ Database is initialized
3. ✅ Demo accounts are created
4. → **Go to http://localhost:3000 and login!**

Enjoy exploring the system! 🏥🤖

---

**System Status**: ✅ **FULLY OPERATIONAL**
**Last Updated**: November 12, 2025
**Version**: 2.0.0
