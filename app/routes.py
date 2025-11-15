"""
Author: Patan Musthakheem
Date & Time: 20-03-2025 1:59 AM
Updated with role-based access control
"""

from flask import Flask, Blueprint, render_template, request, session, send_file, Response, redirect, url_for, flash
from datetime import datetime, timedelta
from collections import Counter
from sqlalchemy import func

import os
from werkzeug.utils import secure_filename
from . import utils
from . import api
from . import generate_heatmap
from . import chat
from .models import User, Patient, Prediction, db
from .auth import get_current_user, login_required, role_required



routes = Blueprint("routes", __name__)

# Upload directory constant
UPLOAD_DIR = os.path.abspath("uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_dashboard_stats():
    """Get statistics for the dashboard."""
    # Get total counts
    total_predictions = Prediction.query.count()
    total_patients = Patient.query.count()
    
    # Get predictions made today
    today = datetime.now().date()
    predictions_today = Prediction.query.filter(
        func.date(Prediction.created_at) == today
    ).count()
    
    # Get disease distribution
    disease_predictions = Prediction.query.with_entities(Prediction.predicted_disease).all()
    disease_distribution = Counter([pred[0] for pred in disease_predictions if pred[0]])
    
    # Get weekly trend (last 7 days)
    weekly_trend = {}
    for i in range(7):
        date = today - timedelta(days=i)
        count = Prediction.query.filter(
            func.date(Prediction.created_at) == date
        ).count()
        weekly_trend[date.strftime('%Y-%m-%d')] = count
    
    # Recent predictions with patient info
    recent_predictions = (
        Prediction.query
        .join(Patient)
        .order_by(Prediction.created_at.desc())
        .limit(10)
        .all()
    )
    
    return {
        'total_predictions': total_predictions,
        'total_patients': total_patients,
        'predictions_today': predictions_today,
        'disease_distribution': disease_distribution,
        'weekly_trend': weekly_trend,
        'recent_predictions': recent_predictions
    }

@routes.route("/", methods=["GET"])
def index():
    """Homepage with navigation"""
    return render_template("index.html")

@routes.route("/login", methods=["GET"])
def login():
    """Login portal - redirect based on login status or show role selection"""
    user = get_current_user()
    
    if user:
        # Redirect to appropriate dashboard if already logged in
        if user.role == 'admin':
            return redirect(url_for('dashboards.admin_dashboard'))
        elif user.role == 'doctor':
            return redirect(url_for('dashboards.doctor_dashboard'))
        elif user.role == 'patient':
            return redirect(url_for('dashboards.patient_dashboard'))
        elif user.role == 'asha_worker':
            return redirect(url_for('dashboards.asha_worker_dashboard'))    
    
    # Show role selection page
    return render_template("home.html")

@routes.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return render_template("admin-login.html")
    
    # Handle POST
    try:
        admin_id = request.form.get('adminID', '').strip()
        admin_pass = request.form.get('adminPASS', '').strip()
        
        # Look up user by username
        user = User.query.filter_by(username=admin_id).first()
        
        if user and user.role == 'admin' and user.check_password(admin_pass):
            # Valid admin login
            session['LOGGED_IN'] = True
            session['user_id'] = user.id
            session['user_role'] = 'admin'
            session['username'] = user.username
            return redirect(url_for('dashboards.admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')
            return render_template("admin-login.html")
    except Exception as e:
        flash(f'Login error: {str(e)}', 'danger')
        return render_template("admin-login.html")

@routes.route("/dashboard")
def dashboard():
    if not session.get('LOGGED_IN'):
        return render_template("error.html", message="Please Log In First")
    stats = get_dashboard_stats()
    return render_template("dashboard.html", stats=stats)




# For Doctor

@routes.route("/doctor-login", methods=["GET", "POST"])
def doctor_login():
    if request.method == "GET":
        return render_template('doc-login.html')
    
    # Handle POST
    try:
        doctor_id = request.form.get('doctorId', '').strip()
        doctor_pass = request.form.get('doctorPass', '').strip()
        
        # Look up user by username
        user = User.query.filter_by(username=doctor_id).first()
        
        if user and user.role == 'doctor' and user.check_password(doctor_pass):
            # Valid doctor login
            session['LOGGED_IN'] = True
            session['user_id'] = user.id
            session['user_role'] = 'doctor'
            session['username'] = user.username
            return redirect(url_for('dashboards.doctor_dashboard'))
        else:
            flash('Invalid doctor credentials', 'danger')
            return render_template('doc-login.html')
    except Exception as e:
        flash(f'Login error: {str(e)}', 'danger')
        return render_template('doc-login.html')

@routes.route("/doctor-login/doctor-dashboard/doctor-upload-xray", methods=["GET", "POST"])
def doctor_upload_xray():
    if not session.get('LOGGED_IN'):
        return render_template("error.html", message="Please Log In First")
    if request.method == "GET":
        return render_template("doc-upload.html")
    else:
        # TODO load the file
        if 'file' not in request.files:
            return "No File found"
        file = request.files['file']
        if file.filename == '':
            return "No Selected File"
        if file:
            try:
                # Use a secure filename and ensure uploads directory exists
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_DIR, filename)
                file.save(file_path)
                predictor = api.XRayPredictor()
                with open(file_path, "rb") as f:
                    image_bytes = f.read()
                result = predictor.predict(image_bytes)
                # nsure 'prediction' key exists
                disease_detected = result.get('prediction', [None])[0]
                if not disease_detected:
                    return "Error: No disease detected", 400

                # Get patient info from form
                patient_name = request.form.get('patient_name', 'Unknown')
                patient_age = request.form.get('patient_age', 0)
                patient_gender = request.form.get('patient_gender', 'Unknown')

                # Save to database
                patient = Patient(
                    name=patient_name,
                    age=patient_age,
                    gender=patient_gender
                )
                db.session.add(patient)
                db.session.flush()  # Get patient ID

                # Generate heatmap
                heatmap = generate_heatmap.XRayHeatmapGenerator()
                heatmap_array = heatmap.generate_heatmap(image_bytes)
                heatmap_path = os.path.join(UPLOAD_DIR, f'heatmap_{filename}')
                # overlay_heatmap handles None gracefully
                try:
                    output_path = heatmap.overlay_heatmap(heatmap_array, image_bytes, f'heatmap_{filename}')
                except Exception as e:
                    print(f"Warning: Could not generate heatmap overlay: {e}")
                    output_path = heatmap_path

                # Save prediction
                prediction = Prediction(
                    patient_id=patient.id,
                    image_path=file_path,
                    prediction=disease_detected,
                    confidence=result.get('confidence', 0.0),
                    heatmap_path=heatmap_path,
                    created_by=1  # TODO: Get actual user ID from session
                )
                db.session.add(prediction)
                db.session.commit()

                # Generate LLM-based report
                data_llm = chat.GPT().create_prompt(disease_detected)
                data_llm = data_llm.encode("utf-8", errors="replace").decode("utf-8")
                print(data_llm)

                # Generate PDF
                pdf = utils.generate_pdf(file_path, output_path, data_llm)
                response = Response(pdf, content_type="application/pdf")
                response.headers["Content-Disposition"] = f"attachment; filename=report.pdf"
                return response
            except Exception as e:
                db.session.rollback()
                return f"Error: {str(e)}", 500
    # Fallback - render report generation page
    return render_template("generate-report.html")


@routes.route("/doctor-login/doctor-dashboard/doctor-upload-mri", methods=["GET", "POST"])
def doctor_upload_mri():
    if not session.get('LOGGED_IN'):
        return render_template("error.html", message="Please Log In First")
    if request.method == "GET":
        return render_template("doc-upload.html")
    else:
        # TODO load the file
        if 'file' not in request.files:
            return "No File found"
        file = request.files['file']
        if file.filename == '':
            return "No Selected File"
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_DIR, filename)
            file.save(file_path)
            # TODO PREDICT AND GENERATE REPORT AND SEND BACK
            data = {}
            # TODO: Add MRI prediction pipeline

        return render_template("generate-report.html", data=data)


# For Patient

@routes.route("/doctor-login/doctor-dashboard/doctor-upload-imaging", methods=["GET", "POST"])
def doctor_upload_imaging():
    """Unified route for X-Ray and MRI uploads with image type selection"""
    if not session.get('LOGGED_IN'):
        return render_template("error.html", message="Please Log In First")
    
    if request.method == "GET":
        return render_template("doc-upload-imaging.html")
    
    # Handle POST request
    try:
        # Get image type selection
        image_type = request.form.get('image_type', '').strip().lower()
        
        if image_type not in ['xray', 'mri']:
            return "Error: Please select a valid image type (X-Ray or MRI)", 400
        
        # Check if file exists
        if 'file' not in request.files:
            return "No File found", 400
        
        file = request.files['file']
        if file.filename == '':
            return "No Selected File", 400
        
        if file:
            # Use a secure filename and ensure uploads directory exists
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_DIR, filename)
            file.save(file_path)
            
            # Select appropriate predictor based on image type
            if image_type == 'xray':
                predictor = api.XRayPredictor()
            else:  # mri
                predictor = api.MRIPredictor()
            
            with open(file_path, "rb") as f:
                image_bytes = f.read()
            
            result = predictor.predict(image_bytes)
            
            # Ensure 'prediction' key exists
            disease_detected = result.get('prediction', [None])[0]
            if not disease_detected:
                return "Error: No disease detected", 400

            # Get patient info from form
            patient_name = request.form.get('patient_name', 'Unknown')
            patient_age = request.form.get('patient_age', 0)
            patient_gender = request.form.get('patient_gender', 'Unknown')

            # Save to database
            patient = Patient(
                name=patient_name,
                age=patient_age,
                gender=patient_gender
            )
            db.session.add(patient)
            db.session.flush()  # Get patient ID

            # Generate heatmap
            heatmap = generate_heatmap.XRayHeatmapGenerator()
            heatmap_array = heatmap.generate_heatmap(image_bytes)
            heatmap_path = os.path.join(UPLOAD_DIR, f'heatmap_{filename}')
            
            try:
                output_path = heatmap.overlay_heatmap(heatmap_array, image_bytes, f'heatmap_{filename}')
            except Exception as e:
                print(f"Warning: Could not generate heatmap overlay: {e}")
                output_path = heatmap_path

            # Save prediction
            prediction = Prediction(
                patient_id=patient.id,
                image_path=file_path,
                prediction=disease_detected,
                confidence=result.get('confidence', 0.0),
                heatmap_path=heatmap_path,
                created_by=1  # TODO: Get actual user ID from session
            )
            db.session.add(prediction)
            db.session.commit()

            # Generate LLM-based report
            data_llm = chat.GPT().create_prompt(disease_detected)
            data_llm = data_llm.encode("utf-8", errors="replace").decode("utf-8")
            print(data_llm)

            # Generate PDF
            pdf = utils.generate_pdf(file_path, output_path, data_llm)
            response = Response(pdf, content_type="application/pdf")
            response.headers["Content-Disposition"] = f"attachment; filename=report_{image_type}.pdf"
            return response
            
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}", 500
    
    # Fallback
    return render_template("generate-report.html")

# For Patient

@routes.route("/patient-register", methods=["POST"])
def patient_register():
    """Handle patient registration"""
    try:
        # Get form data
        username = request.form.get("username", '').strip()
        full_name = request.form.get("full_name", '').strip()
        email = request.form.get("email", '').strip()
        password = request.form.get("password", '').strip()
        confirm_password = request.form.get("confirm_password", '').strip()
        phone = request.form.get("phone", '').strip()
        age = request.form.get("age", '').strip()
        gender = request.form.get("gender", '').strip()
        
        # Validation
        if not username or not full_name or not email or not password:
            flash('Username, full name, email, and password are required', 'danger')
            return redirect(url_for('routes.patient_login'))
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long', 'danger')
            return redirect(url_for('routes.patient_login'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'danger')
            return redirect(url_for('routes.patient_login'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('routes.patient_login'))
        
        # Email validation (basic)
        if '@' not in email or '.' not in email:
            flash('Invalid email address', 'danger')
            return redirect(url_for('routes.patient_login'))
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('routes.patient_login'))
        
        # Check if email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered. Please use a different email.', 'danger')
            return redirect(url_for('routes.patient_login'))
        
        # Validate phone if provided
        if phone and (len(phone) != 10 or not phone.isdigit()):
            flash('Phone number must be exactly 10 digits', 'danger')
            return redirect(url_for('routes.patient_login'))
        
        # Validate age if provided
        if age:
            try:
                age_int = int(age)
                if age_int < 1 or age_int > 120:
                    flash('Age must be between 1 and 120', 'danger')
                    return redirect(url_for('routes.patient_login'))
            except ValueError:
                flash('Invalid age value', 'danger')
                return redirect(url_for('routes.patient_login'))
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            role='patient'
        )
        new_user.set_password(password)
        
        # Add to database
        db.session.add(new_user)
        db.session.flush()  # Get the user ID
        
        # Create patient profile
        new_patient = Patient(
            user_id=new_user.id,
            full_name=full_name,
            age=int(age) if age else None,
            gender=gender if gender else None,
            phone=phone if phone else None
        )
        
        db.session.add(new_patient)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('routes.patient_login'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Registration error: {str(e)}', 'danger')
        return redirect(url_for('routes.patient_login'))

@routes.route("/patient-login", methods=["GET", "POST"])
def patient_login():
    if request.method == "GET":
        return render_template("patient-login.html")
    
    # Handle POST
    try:
        patient_id = request.form.get("patientID", '').strip()
        patient_pass = request.form.get("patientPASS", '').strip()
        
        # Look up user by username
        user = User.query.filter_by(username=patient_id).first()
        
        if user and user.role == 'patient' and user.check_password(patient_pass):
            # Valid patient login
            session['LOGGED_IN'] = True
            session['user_id'] = user.id
            session['user_role'] = 'patient'
            session['username'] = user.username
            return redirect(url_for('dashboards.patient_dashboard'))
        else:
            flash('Invalid patient credentials', 'danger')
            return render_template("patient-login.html")
    except Exception as e:
        flash(f'Login error: {str(e)}', 'danger')
        return render_template("patient-login.html")
