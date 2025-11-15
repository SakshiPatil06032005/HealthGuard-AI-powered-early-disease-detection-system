# 🚀 How to Run the AI Disease Prediction System - COMPLETE GUIDE

**Last Updated:** November 13, 2025  
**Server Status:** ✅ RUNNING on http://localhost:3000

---

## ⚡ QUICK START (Copy & Paste This)

```powershell
Push-Location -LiteralPath "C:\Users\Asus\OneDrive\Desktop\AI-Powered-Early-Disease-Prediction-System-main_(2)[1]\AI-Powered-Early-Disease-Prediction-System-main"; python run.py
```

**Then open browser and go to:**
```
http://localhost:3000
```

**Login with:**
- Username: `mahima`
- Password: `mahima`

---

## 📍 Important: Path Information

### **Why the strange path?**
Your project folder is stored in OneDrive, which creates a **"junction" folder** with special characters. This requires using PowerShell's `-LiteralPath` parameter.

### **The actual path structure:**
```
C:\Users\Asus\OneDrive\Desktop\
└── AI-Powered-Early-Disease-Prediction-System-main_(2)[1]    ← OneDrive Junction
    └── AI-Powered-Early-Disease-Prediction-System-main       ← Actual Project
        ├── run.py                                             ← The file we run
        ├── app/
        ├── requirements.txt
        ├── app.db
        └── ... (other project files)
```

---

## 🔧 STEP-BY-STEP GUIDE

### **Step 1: Open PowerShell**
- Press `Win + R`
- Type `powershell`
- Press `Enter`

### **Step 2: Navigate to the Project**
Copy and paste this command:

```powershell
Push-Location -LiteralPath "C:\Users\Asus\OneDrive\Desktop\AI-Powered-Early-Disease-Prediction-System-main_(2)[1]\AI-Powered-Early-Disease-Prediction-System-main"
```

**Verify you're in the right place:**
```powershell
pwd
```

Should show:
```
C:\Users\Asus\OneDrive\Desktop\AI-Powered-Early-Disease-Prediction-System-main_(2)[1]\AI-Powered-Early-Disease-Prediction-System-main
```

### **Step 3: Install Dependencies (First time only)**
```powershell
pip install -r requirements.txt
```

### **Step 4: Run the Application**
```powershell
python run.py
```

### **Step 5: Open in Browser**
Once you see this message:
```
🌐 Server: http://localhost:3000
```

Open your browser and go to:
```
http://localhost:3000
```

---

## 🟢 Successful Startup Message

When running correctly, you'll see:

```
INFO:app:✅ Database tables created/verified successfully
⚠️ Model not found - using dummy model for demo
INFO:app:✅ Disease prediction model initialized
✅ Gemini API initialized for medicine recommendations
⚠️ TensorFlow not available - using fallback image analysis

AI-Powered Disease Prediction System
===================================
🌐 Server: http://localhost:3000
👤 Demo login:
   Username: mahima
   Password: mahima

 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:3000
 * Running on http://127.0.0.1:3000
 * Running on http://10.198.142.230:3000
WARNING:werkzeug: * Debugger is active!
INFO:werkzeug: * Debugger PIN: 320-917-488
```

✅ **All good!** The warnings are normal and expected.

---

## 🌐 Access URLs

| URL | Purpose |
|-----|---------|
| `http://localhost:3000` | Main application (local computer) |
| `http://127.0.0.1:3000` | Main application (alternative local) |
| `http://10.198.142.230:3000` | Access from other computers on network |

---

## 👤 Demo Login

**Role:** Patient  
**Username:** `mahima`  
**Password:** `mahima`

After login, you'll see the patient dashboard with:
- ✅ Symptom Checker
- ✅ X-Ray Analysis  
- ✅ MRI Analysis
- ✅ View History

---

## 🛑 Stopping the Server

In PowerShell, press:
```
Ctrl + C
```

You'll see:
```
KeyboardInterrupt
```

The server will stop.

---

## ❌ Troubleshooting

### **Problem: "Cannot find path" error**
**Solution:** Use the `-LiteralPath` parameter (as shown above). The special characters `(2)[1]` need this.

### **Problem: "ModuleNotFoundError" or "No module named"**
**Solution:** Install dependencies:
```powershell
pip install -r requirements.txt
```

### **Problem: Port 3000 already in use**
**Solution 1:** Wait a few seconds and the app will find an alternative port  
**Solution 2:** Close other programs using port 3000  
**Solution 3:** The app will display which port it's using

### **Problem: Python not found**
**Solution:** Make sure Python is installed:
```powershell
python --version
```

If not found, install Python from python.org

### **Problem: "onedrive\tempstate\downloads" permission error**
**Solution:** This is an OneDrive sync issue. The app handles this automatically.

---

## 📂 File Structure

```
AI-Powered-Early-Disease-Prediction-System-main/
│
├── run.py                           ← 🟢 START HERE
├── requirements.txt                 ← Dependencies
├── app.db                           ← Database (auto-created)
│
├── app/
│   ├── __init__.py                 ← App initialization
│   ├── run.py (internal)
│   ├── config.py                   ← Configuration
│   ├── models.py                   ← Database models
│   │
│   ├── routes.py                   ← Main routes
│   ├── dashboard_routes.py         ← Dashboard routes
│   ├── auth_routes.py              ← Login/Auth
│   │
│   ├── advanced_disease_model.py   ← 🆕 Symptom predictor
│   ├── advanced_image_predictor.py ← 🆕 Image analysis
│   ├── medicine_recommender.py     ← 🆕 Medicine suggestions
│   ├── report_generator.py         ← 🆕 PDF reports
│   │
│   ├── templates/                  ← HTML files
│   │   ├── home.html
│   │   ├── dashboards/
│   │   │   ├── patient_dashboard.html
│   │   │   ├── xray_prediction.html      ← 🆕
│   │   │   ├── mri_prediction.html       ← 🆕
│   │   │   └── prediction_history.html   ← 🆕
│   │   └── ...
│   │
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   ├── images/
│   │   └── ...
│   │
│   └── model_train/                ← ML training files
│
├── uploads/                        ← Image uploads (auto-created)
├── instance/                       ← Flask instance folder
│
└── Documentation/
    ├── README.md
    ├── ENHANCEMENT_SUMMARY.md
    └── ...
```

---

## 🎯 Next Steps After Running

1. **Login** with `mahima` / `mahima`
2. **Click "Symptom Checker"** to predict diseases from symptoms
3. **Click "X-Ray Analysis"** to upload and analyze X-ray images
4. **Click "MRI Analysis"** to upload and analyze MRI images
5. **Click "View History"** to see all past predictions
6. **Download Reports** as PDF for any prediction

---

## 💡 Tips

- **Live Reload:** The server automatically reloads when you modify code (debug mode enabled)
- **Database:** `app.db` is automatically created and persists data
- **Logs:** Check the PowerShell window for error messages
- **API Key:** Gemini API is already configured for medicine suggestions

---

## 🔗 Important URLs

**Admin/Doctor Login:**
```
http://localhost:3000/admin/login
http://localhost:3000/doctor/login
```

**Patient Dashboard:**
```
http://localhost:3000/dashboard/patient
```

**Logout:**
```
http://localhost:3000/logout
```

---

## 📞 Support

If you encounter issues:

1. **Check the terminal output** for error messages
2. **Verify Python installation:** `python --version`
3. **Verify dependencies:** `pip list`
4. **Restart the server:** `Ctrl + C` then run again
5. **Check firewall:** Port 3000 might be blocked

---

**Happy Testing! 🎉**

For feature details, see `ENHANCEMENT_SUMMARY.md`
