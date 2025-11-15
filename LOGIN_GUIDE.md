# 🔐 Login & Access Guide

## 📍 Where to Find Login Pages

Your system has **three different login pages** - one for each user role. Here's where they are:

---

## 🏠 Home Page

**URL:** `http://localhost:3000/`

The home page displays:
- System logo and welcome message
- **Three login buttons:**
  1. **Admin Login** - For system administrators
  2. **Doctor Login** - For medical professionals
  3. **Patient Login** - For healthcare consumers
- Quick navigation to register as a patient

---

## 🔓 Accessing Login Pages

### Method 1: From Home Page
1. Open `http://localhost:3000/`
2. Click the role-specific login button
3. Enter credentials and submit

### Method 2: Direct URLs
- **Admin Login:** `http://localhost:3000/admin-login`
- **Doctor Login:** `http://localhost:3000/doctor-login`
- **Patient Login:** `http://localhost:3000/patient-login`

---

## 👥 Demo User Accounts

### 🛡️ **ADMIN Account**
```
Role: Administrator (Full System Access)
Username: admin
Email: admin@healthsystem.com
Password: admin123
```

**Admin Credentials for Login:**
```
Email/Username: admin
Password: admin123
```

---

### 👨‍⚕️ **DOCTOR Accounts** (Choose Any One)

#### Doctor 1: Mahima Sharma
```
Username: mahima
Email: mahima@healthsystem.com
Password: mahima
Specialization: General Practitioner
License: LS-001
```

#### Doctor 2: Dr. Smith
```
Username: drsmith
Email: drsmith@healthsystem.com
Password: doctor123
Specialization: Cardiologist
License: LS-002
```

#### Doctor 3: Dr. Brown
```
Username: drbrown
Email: drbrown@healthsystem.com
Password: doctor123
Specialization: Pulmonologist
License: LS-003
```

**To Login as Doctor:**
1. Go to `http://localhost:3000/doctor-login`
2. Enter username: `mahima`
3. Enter password: `mahima`
4. Click "Login"

---

### 👤 **PATIENT Accounts** (Choose Any One)

#### Patient 1: John Doe
```
Username: john_doe
Email: john.doe@email.com
Password: patient123
Age: 35
Gender: Male
```

#### Patient 2: Jane Smith
```
Username: jane_smith
Email: jane.smith@email.com
Password: patient123
Age: 28
Gender: Female
```

#### Patient 3: Mike Johnson
```
Username: mike_johnson
Email: mike.johnson@email.com
Password: patient123
Age: 45
Gender: Male
```

**To Login as Patient:**
1. Go to `http://localhost:3000/patient-login`
2. Enter username: `john_doe`
3. Enter password: `patient123`
4. Click "Login"

---

## 📝 Signup / Registration

### Who Can Sign Up?
**Only PATIENTS can create new accounts.** Admins and doctors are pre-created by system administrators.

### How to Sign Up as a Patient?

**Step 1: Go to Registration Page**
- Option A: Click "Create Account" on the patient login page
- Option B: Go to `http://localhost:3000/auth/register`

**Step 2: Fill Registration Form**
The registration form requires:
- **Full Name** (Required)
  - Example: `John Smith`
- **Username** (Required, must be unique)
  - Example: `john_smith`
  - Cannot use existing usernames
- **Email** (Required, must be unique)
  - Example: `john.smith@email.com`
  - Must be valid email format
- **Age** (Required)
  - Must be between 1-150 years old
- **Gender** (Required)
  - Options: Male, Female, Other
- **Password** (Required, minimum 6 characters)
  - Example: `SecurePass123`
  - Minimum 6 characters required
- **Confirm Password** (Required)
  - Must match the password field
- **Terms & Conditions** (Required to accept)
  - Check the checkbox to proceed

**Step 3: Submit Form**
- Click "Create Account" button
- Wait for confirmation message
- System validates all fields

**Step 4: Login**
- After successful registration, redirect to login page
- Use your new username and password to login
- You'll be directed to your Patient Dashboard

### Registration Form Validation

The system will show errors if:
- ❌ Username already exists → Try a different username
- ❌ Email already exists → Try a different email
- ❌ Password is too short (< 6 chars) → Use at least 6 characters
- ❌ Passwords don't match → Confirm password must match
- ❌ Email format is invalid → Use format: name@example.com
- ❌ Required fields are empty → Fill all marked fields
- ❌ Age is invalid → Use a number between 1-150

---

## 📊 What You See After Login

### Admin Dashboard
**URL:** `http://localhost:3000/dashboard/admin`

After logging in as admin, you see:
- ✅ System Statistics
  - Total Users Count
  - Total Doctors Count
  - Total Patients Count
  - Total Predictions Count
  - Predictions Made Today
- ✅ Doctor Management List
  - All registered doctors
  - Doctor specialization
  - Contact information
- ✅ Patient Management List
  - All registered patients
  - Patient age and email
  - Contact information
- ✅ Quick Action Buttons
  - Add Doctor
  - Add Patient
  - Generate Report
  - System Settings

---

### Doctor Dashboard
**URL:** `http://localhost:3000/dashboard/doctor`

After logging in as doctor, you see:
- ✅ Doctor Information
  - Full name
  - Medical specialization
  - License number
- ✅ Statistics Cards
  - Number of assigned patients
  - Total predictions made
  - Predictions made today
- ✅ Patient List
  - All your assigned patients
  - Patient age, gender, email
  - Contact phone number
  - "View Records" button for each patient
- ✅ Quick Actions
  - View patient medical histories
  - Analyze X-ray and MRI images
  - Add notes to patient records
  - Generate medical reports

**To View Patient Details:**
1. Find the patient in your list
2. Click "View Records" button
3. See all their medical history and predictions

---

### Patient Dashboard
**URL:** `http://localhost:3000/dashboard/patient`

After logging in as patient, you see:
- ✅ Personal Health Information
  - Your full name
  - Your age
  - Your gender
  - Contact phone
  - Medical history summary
- ✅ Health Statistics
  - Total predictions count
  - Number of assigned doctors
- ✅ Assigned Doctors
  - List of your doctors
  - Doctor specialization
  - Doctor contact information
- ✅ Medical Records
  - All your predictions history
  - Date and time of each prediction
  - Disease results
  - Confidence percentages
  - "View Details" button
- ✅ Quick Actions
  - **Symptom Checker** ← AI Disease Prediction
  - Upload X-ray (integration ready)
  - View History

---

## 🔄 Login & Logout Flow

### Successful Login Flow
```
1. User enters username/password
2. System verifies credentials
3. System checks user role
4. Session is created
5. User is redirected to role-specific dashboard:
   - Admin → /dashboard/admin
   - Doctor → /dashboard/doctor
   - Patient → /dashboard/patient
```

### Logout
```
Click "Logout" button in any dashboard
↓
Session is destroyed
↓
Redirect to home page
↓
Login page is displayed
```

---

## ⚠️ Important Notes

### Session Duration
- Sessions last **24 hours**
- After 24 hours, you need to login again
- Closing the browser doesn't automatically logout

### Password Security
- Passwords are hashed using pbkdf2:sha256
- Never share your password
- Admin cannot see your password
- If forgotten, contact system administrator

### Account Creation
- Only patients can self-register
- Doctors and admins must be created by system administrator
- Existing patients can login immediately after signup

### Browser Compatibility
- Works on Chrome, Firefox, Safari, Edge
- Works on mobile browsers
- Responsive design adapts to screen size

### Multiple Browser Issues
- Don't login on same browser with different accounts simultaneously
- Use different browsers or clear cookies between logins
- Use private/incognito mode for separate sessions

---

## 🆘 Troubleshooting

### Problem: "Invalid Credentials"
**Solution:**
- Double-check your username/email
- Verify your password (case-sensitive)
- Use demo accounts provided above
- Clear browser cookies and try again

### Problem: "User Already Exists" During Signup
**Solution:**
- Use a different username
- Use a different email address
- Check if you already have an account

### Problem: "Session Expired"
**Solution:**
- Login again
- Check if it's been more than 24 hours
- Clear browser cache and cookies

### Problem: Cannot Access Dashboard
**Solution:**
- Ensure you're logged in
- Check browser console for errors
- Try a different browser
- Clear cookies and login again

### Problem: Demo Accounts Not Working
**Solution:**
1. Stop the server: `Ctrl+C`
2. Reset database: Delete `app.db`
3. Run setup: `python setup.py`
4. Start server: `python run.py`
5. Try demo credentials again

---

## 🎯 Quick Start Path

**For First-Time Users:**
1. Open `http://localhost:3000/`
2. Click "Patient Login"
3. Use: `john_doe` / `patient123`
4. Explore Patient Dashboard
5. Click "Symptom Checker" to test disease prediction
6. Logout

**For Testing All Roles:**
1. Login as Patient (john_doe / patient123)
2. Explore Patient Dashboard
3. Logout
4. Login as Doctor (mahima / mahima)
5. View assigned patients
6. Logout
7. Login as Admin (admin / admin123)
8. See system statistics

---

## 📱 URLs Reference

| Feature | URL |
|---------|-----|
| Home Page | `http://localhost:3000/` |
| Admin Login | `http://localhost:3000/admin-login` |
| Doctor Login | `http://localhost:3000/doctor-login` |
| Patient Login | `http://localhost:3000/patient-login` |
| Patient Register | `http://localhost:3000/auth/register` |
| Admin Dashboard | `http://localhost:3000/dashboard/admin` |
| Doctor Dashboard | `http://localhost:3000/dashboard/doctor` |
| Patient Dashboard | `http://localhost:3000/dashboard/patient` |
| Symptom Checker | `http://localhost:3000/dashboard/symptom-prediction` |
| User Profile | `http://localhost:3000/auth/profile` |

---

**Version**: 2.0.0  
**Last Updated**: November 12, 2025  
**Status**: ✅ COMPLETE
