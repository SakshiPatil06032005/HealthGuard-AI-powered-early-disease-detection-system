# 🏥 AI-Powered Early Disease Prediction System

A comprehensive Flask-based medical AI system for disease prediction using X-ray analysis, MRI imaging, and symptom-based AI diagnosis.

## ✨ Features

### 🎯 Core Functionality
- **X-ray Analysis**: AI-powered analysis of chest X-rays with Grad-CAM heatmaps
- **Symptom Checker**: Rule-based disease prediction from selected symptoms
- **Medical Reports**: Automated PDF report generation with AI analysis
- **Disease Pattern Recognition**: Pattern analysis for pneumonia and consolidation detection

### 👥 Role-Based Access Control
- **Admin**: System administration, user management, statistics dashboard
- **Doctor**: Patient management, medical record review, X-ray analysis
- **Patient**: Personal health records, symptom checker, prediction history

### 🔐 Authentication & Security
- Secure user registration and login
- Password hashing with Werkzeug security
- Role-based access control with decorators
- Session management with timeouts

### 📊 Dashboards
- **Admin Dashboard**: System statistics, user management, analytics
- **Doctor Dashboard**: Patient list, medical records, prediction history
- **Patient Dashboard**: Personal health data, symptom checker, medical history

### 🤖 AI/ML Capabilities
- **Gemini 2.0 Flash Integration**: Medical report generation and analysis
- **Disease Prediction Model**: Demo with rule-based symptom analysis
- **Pattern Analysis**: Image processing for disease detection
- **Heatmap Generation**: Visualization of AI decision-making

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda
- Medical X-ray sample images (optional)

### Installation

1. **Clone and Setup**
```bash
cd "C:\Users\xh977\OneDrive\Desktop\Hackthon\AI-Powered-Early-Disease-Prediction-System-main"
python -m venv venv
.\venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Initialize Database**
```bash
python -c "from setup import setup_demo_data; setup_demo_data()"
```

4. **Start Application**
```bash
python run.py
```

5. **Access System**
- Open browser: `http://localhost:3000`
- Dashboard: `http://localhost:3000/dashboard`

## 🔑 Demo Credentials

### Admin Access
```
Username: admin
Password: admin123
```

### Doctor Access
```
Username: mahima
Password: mahima

Username: drsmith
Password: doctor123

Username: drbrown
Password: doctor123
```

### Patient Access
```
Username: john_doe
Password: patient123

Username: jane_smith
Password: patient123

Username: mike_johnson
Password: patient123
```

## 📁 Project Structure

```
app/
├── __init__.py                 # Flask app factory
├── config.py                   # Configuration settings
├── models.py                   # Database models (User, Doctor, Patient, etc.)
├── auth.py                     # Authentication utilities & decorators
├── auth_routes.py              # Authentication routes (login, register, logout)
├── dashboard_routes.py         # Dashboard routes (admin, doctor, patient)
├── routes.py                   # Main routes
├── disease_model.py            # Disease prediction model
├── api.py                      # X-ray prediction API
├── chat.py                     # Gemini AI integration
├── generate_heatmap.py         # Grad-CAM heatmap generation
├── utils.py                    # Utility functions (PDF generation, etc.)
├── static/
│   ├── css/                    # Stylesheets
│   ├── js/                     # JavaScript files
│   ├── images/                 # Static images
│   └── heatmaps/               # Generated heatmaps
├── templates/
│   ├── auth/
│   │   ├── login.html          # Login page
│   │   ├── register.html       # Registration page
│   │   └── profile.html        # User profile
│   ├── dashboards/
│   │   ├── admin_dashboard.html
│   │   ├── doctor_dashboard.html
│   │   ├── patient_dashboard.html
│   │   ├── doctor_patient_detail.html
│   │   ├── patient_prediction_detail.html
│   │   └── symptom_prediction.html
│   └── home.html               # Home page
└── models/
    ├── chest_xray_model.keras
    └── disease_predictor.pkl

run.py                          # Application entry point
setup.py                        # Database initialization script
requirements.txt                # Python dependencies
```

## 🔄 API Endpoints

### Authentication Routes
- `GET/POST /auth/login` - User login
- `GET/POST /auth/register` - New user registration
- `POST /auth/logout` - User logout
- `GET /auth/profile` - View user profile

### Dashboard Routes
- `GET /dashboard/admin` - Admin dashboard (Admin only)
- `GET /dashboard/doctor` - Doctor dashboard (Doctor only)
- `GET /dashboard/patient` - Patient dashboard (Patient only)
- `GET /dashboard/symptom-prediction` - Symptom checker
- `POST /dashboard/symptom-prediction` - Submit symptom check

### API Endpoints
- `POST /api/xray-predict` - X-ray prediction
- `POST /api/generate-report` - Generate medical report
- `GET /api/admin/stats` - Admin statistics
- `GET /api/doctor/stats` - Doctor statistics

## 🎨 Frontend Features

### Responsive Design
- Tailwind CSS for styling
- Mobile-friendly layouts
- Dark mode support (optional)

### Interactive Elements
- Chart.js for data visualization
- Dynamic symptom selection
- Real-time prediction display
- File upload functionality

## 🔧 Configuration

Edit `app/config.py` to configure:

```python
# Database
SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
# For MySQL: 'mysql+pymysql://root:password@localhost/disease_prediction'

# API Keys
GEMINI_API_KEY = 'your-api-key-here'

# Security
SECRET_KEY = 'your-secret-key'
SESSION_COOKIE_HTTPONLY = True
```

## 📊 Database Models

### User
- Core authentication model
- Roles: admin, doctor, patient
- Fields: username, email, password_hash, role, created_at

### Admin
- System administrator
- Fields: full_name, phone, created_at

### Doctor
- Medical professional
- Fields: full_name, specialization, license_number, phone
- Relations: many patients, many predictions

### Patient
- Healthcare consumer
- Fields: full_name, age, gender, phone, address, medical_history
- Relations: many doctors, many predictions

### Prediction
- Medical prediction record
- Fields: patient_id, doctor_id, prediction_type, predicted_disease, confidence, symptoms, report_path
- Types: 'xray', 'mri', 'symptoms'

### DoctorPatient
- Association table for doctor-patient relationships
- Enables doctor assignment to patients

## 🤖 AI Integration

### Gemini 2.0 Flash
- Medical report generation
- Disease analysis and explanation
- Fallback to demo text if API unavailable

### Disease Prediction
- Rule-based symptom analysis
- Demo model with expandable symptom list
- Support for ML model integration (scikit-learn)

### Image Analysis
- X-ray preprocessing with OpenCV
- Pattern detection for pneumonia
- Grad-CAM heatmap visualization

## 📝 Medical Features

### Supported Symptoms
- Respiratory: fever, cough, shortness of breath, chest pain
- General: fatigue, headache, muscle pain, chills
- GI: nausea, vomiting, diarrhea
- ENT: sore throat, loss of smell/taste, runny nose
- Allergies: sneezing, itchy eyes, watery eyes

### Predicted Diseases
- Pneumonia
- COVID-19
- Influenza (Flu)
- Common Cold
- Bronchitis

## 🔒 Security Features

- Password hashing with `pbkdf2:sha256`
- SQL injection prevention with SQLAlchemy ORM
- CSRF protection ready
- Session timeouts
- Role-based access control
- Secure file upload handling

## 📈 Performance

- SQLite database for rapid development
- MySQL support for production
- Efficient image processing with OpenCV
- Caching strategies for AI predictions
- Optimized SQL queries

## 🛠️ Troubleshooting

### Port 3000 Already in Use
```bash
# Change port in run.py or use:
python run.py --port 5000
```

### Database Errors
```bash
# Reset database:
rm app.db
python -c "from setup import setup_demo_data; setup_demo_data()"
```

### Gemini API Issues
- Verify API key in `config.py`
- Check internet connection
- System uses demo text as fallback

### File Upload Issues
- Ensure `uploads/` directory exists
- Check file permissions
- Verify ALLOWED_EXTENSIONS in config

## 🚀 Deployment

### For Production
1. Set `DEBUG = False` in config
2. Use environment variables for secrets
3. Deploy with gunicorn/uWSGI
4. Use MySQL instead of SQLite
5. Enable HTTPS
6. Set up reverse proxy (Nginx)

### Example Gunicorn Command
```bash
gunicorn -w 4 -b 0.0.0.0:3000 run:app
```

## 📚 Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Flask 3.0.0 |
| ORM | SQLAlchemy 3.1.1 |
| Database | SQLite/MySQL |
| Frontend | Tailwind CSS, Chart.js |
| AI/ML | Google Generative AI (Gemini) |
| Image Processing | OpenCV 4.8+ |
| ML Model | scikit-learn, joblib |
| Reports | FPDF |

## 📝 Future Enhancements

- [ ] Advanced ML disease prediction model training
- [ ] Integration with wearable devices
- [ ] Telemedicine video consultation
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Electronic Health Records (EHR) integration
- [ ] Multi-language support
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Unit and integration tests
- [ ] Docker containerization

## 📞 Support & Contact

For issues, feature requests, or contributions:
1. Check existing issues
2. Create detailed bug reports
3. Submit pull requests
4. Contact development team

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details

## ⚠️ Medical Disclaimer

**IMPORTANT:** This system is designed for **educational and research purposes only**. It should NOT be used for:
- Actual medical diagnosis
- Clinical decision-making
- Patient treatment
- Medical advice

Always consult with qualified healthcare professionals for medical diagnosis and treatment.

---

**Version**: 2.0.0  
**Last Updated**: November 12, 2025  
**Status**: Active Development ✓
