"""
Role-based dashboard routes for Admin, Doctor, and Patient
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify, send_file
from datetime import datetime, timedelta
from collections import Counter
from sqlalchemy import func
import json
import os
import logging
from werkzeug.utils import secure_filename

# Setup logger
logger = logging.getLogger(__name__)

from app.auth import login_required, role_required, get_current_user, get_current_doctor, get_current_patient, get_current_admin, get_current_asha_worker
from app.models import db, User, Doctor, Patient, Prediction, DoctorPatient, Admin, AshaWorker
from app.advanced_disease_model import advanced_predictor
from app.medicine_recommender import medicine_recommender
from app.advanced_image_predictor import image_predictor
from app.report_generator import report_generator
from app.voice_processor import voice_processor
from app.symptom_extractor import symptom_extractor

# Enhanced AI components
try:
    from app.enhanced_predictor import EnhancedXRayPredictor
    from app.enhanced_report_generator import EnhancedReportGenerator
    enhanced_predictor = EnhancedXRayPredictor()
    enhanced_report_gen = EnhancedReportGenerator()
    USE_ENHANCED = True
except ImportError:
    enhanced_predictor = None
    enhanced_report_gen = None
    USE_ENHANCED = False

# Comprehensive predictor with 40+ diseases
try:
    from app.prediction_adapter import prediction_adapter
    comprehensive_predictor = prediction_adapter
    USE_COMPREHENSIVE = True
    logger.info(f"✅ Comprehensive predictor loaded with {comprehensive_predictor.comprehensive_predictor.disease_count} diseases")
except ImportError:
    comprehensive_predictor = None
    USE_COMPREHENSIVE = False
    logger.warning("⚠️ Comprehensive predictor not available")

dashboards = Blueprint('dashboards', __name__, url_prefix='/dashboard')

def get_admin_stats():
    """Get statistics for admin dashboard"""
    return {
        'total_users': User.query.count(),
        'total_doctors': Doctor.query.count(),
        'total_patients': Patient.query.count(),
        'total_predictions': Prediction.query.count(),
        'predictions_today': Prediction.query.filter(
            func.date(Prediction.created_at) == datetime.now().date()
        ).count(),
    }

def get_doctor_stats(doctor_id):
    """Get statistics for doctor dashboard"""
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return {}
    
    # Get assigned patients
    assigned_patients = db.session.query(Patient).join(
        DoctorPatient, Patient.id == DoctorPatient.patient_id
    ).filter(DoctorPatient.doctor_id == doctor_id).all()
    
    patient_ids = [p.id for p in assigned_patients]
    
    predictions_query = Prediction.query.filter(
        Prediction.patient_id.in_(patient_ids) if patient_ids else False
    )
    
    return {
        'full_name': doctor.full_name,
        'specialization': doctor.specialization,
        'assigned_patients': len(assigned_patients),
        'total_predictions': predictions_query.count(),
        'predictions_today': predictions_query.filter(
            func.date(Prediction.created_at) == datetime.now().date()
        ).count(),
        'patients': assigned_patients,
    }

def get_patient_stats(patient_id):
    """Get statistics for patient dashboard"""
    patient = Patient.query.get(patient_id)
    if not patient:
        return {}
    
    predictions = Prediction.query.filter_by(patient_id=patient_id).order_by(
        Prediction.created_at.desc()
    ).all()
    
    return {
        'full_name': patient.full_name,
        'age': patient.age,
        'gender': patient.gender,
        'total_predictions': len(predictions),
        'recent_predictions': predictions[:5],
        'all_predictions': predictions,
    }

@dashboards.route('/admin', methods=['GET'])
@login_required
@role_required('admin')
def admin_dashboard():
    """Admin dashboard"""
    admin = get_current_admin()
    stats = get_admin_stats()
    
    # Get all doctors and patients
    doctors = Doctor.query.all()
    patients = Patient.query.all()
    
    return render_template('dashboards/admin_dashboard.html', 
                         admin=admin,
                         stats=stats,
                         doctors=doctors,
                         patients=patients)

@dashboards.route('/doctor', methods=['GET'])
@login_required
@role_required('doctor')
def doctor_dashboard():
    """Doctor dashboard"""
    doctor = get_current_doctor()
    if not doctor:
        flash('Doctor profile not found', 'danger')
        return redirect(url_for('routes.index'))
    
    stats = get_doctor_stats(doctor.id)
    
    return render_template('dashboards/doctor_dashboard.html', 
                         doctor=doctor,
                         stats=stats)

@dashboards.route('/patient', methods=['GET'])
@login_required
@role_required('patient')
def patient_dashboard():
    """Patient dashboard"""
    patient = get_current_patient()
    if not patient:
        flash('Patient profile not found', 'danger')
        return redirect(url_for('routes.index'))
    
    stats = get_patient_stats(patient.id)
    
    # Get assigned doctors
    doctors = db.session.query(Doctor).join(
        DoctorPatient, Doctor.id == DoctorPatient.doctor_id
    ).filter(DoctorPatient.patient_id == patient.id).all()
    
    return render_template('dashboards/patient_dashboard.html', 
                         patient=patient,
                         stats=stats,
                         doctors=doctors)

@dashboards.route('/doctor/patients/<int:patient_id>', methods=['GET'])
@login_required
@role_required('doctor')
def doctor_view_patient(patient_id):
    """View specific patient details as doctor"""
    doctor = get_current_doctor()
    patient = Patient.query.get(patient_id)
    
    if not patient:
        flash('Patient not found', 'danger')
        return redirect(url_for('dashboards.doctor_dashboard'))
    
    # Check if doctor is assigned to this patient
    assignment = DoctorPatient.query.filter_by(
        doctor_id=doctor.id,
        patient_id=patient_id
    ).first()
    
    if not assignment:
        flash('You are not assigned to this patient', 'danger')
        return redirect(url_for('dashboards.doctor_dashboard'))
    
    predictions = Prediction.query.filter_by(patient_id=patient_id).order_by(
        Prediction.created_at.desc()
    ).all()
    
    return render_template('dashboards/doctor_patient_detail.html',
                         patient=patient,
                         predictions=predictions,
                         doctor=doctor)

@dashboards.route('/patient/predictions/<int:prediction_id>', methods=['GET'])
@login_required
@role_required('patient')
def patient_view_prediction(prediction_id):
    """View specific prediction as patient"""
    patient = get_current_patient()
    prediction = Prediction.query.get(prediction_id)
    
    if not prediction or prediction.patient_id != patient.id:
        flash('Prediction not found or access denied', 'danger')
        return redirect(url_for('dashboards.patient_dashboard'))
    
    return render_template('dashboards/patient_prediction_detail.html',
                         prediction=prediction,
                         patient=patient)

@dashboards.route('/patient/medical-chatbot', methods=['GET'])
@login_required
@role_required('patient')
def medical_chatbot():
    """Medical ChatBot for patients"""
    patient = get_current_patient()
    if not patient:
        flash('Patient profile not found', 'danger')
        return redirect(url_for('routes.index'))
    
    return render_template('dashboards/medical_chatbot.html', patient=patient)

@dashboards.route('/api/admin/stats', methods=['GET'])
@login_required
@role_required('admin')
def api_admin_stats():
    """Get admin statistics for charts"""
    stats = get_admin_stats()
    
    # Get disease distribution
    diseases = db.session.query(
        Prediction.predicted_disease,
        func.count(Prediction.id)
    ).group_by(Prediction.predicted_disease).all()
    
    disease_dist = {d[0] or 'Unknown': d[1] for d in diseases}
    
    # Get weekly trend
    trend = {}
    for i in range(7, 0, -1):
        date = datetime.now().date() - timedelta(days=i)
        count = Prediction.query.filter(
            func.date(Prediction.created_at) == date
        ).count()
        trend[date.strftime('%a')] = count
    
    return jsonify({
        'stats': stats,
        'disease_distribution': disease_dist,
        'weekly_trend': trend,
    })

@dashboards.route('/api/doctor/stats', methods=['GET'])
@login_required
@role_required('doctor')
def api_doctor_stats():
    """Get doctor statistics for charts"""
    doctor = get_current_doctor()
    stats = get_doctor_stats(doctor.id)
    
    # Get disease distribution for this doctor's patients
    patient_ids = [p.id for p in stats.get('patients', [])]
    diseases = []
    
    if patient_ids:
        diseases = db.session.query(
            Prediction.predicted_disease,
            func.count(Prediction.id)
        ).filter(Prediction.patient_id.in_(patient_ids)).group_by(
            Prediction.predicted_disease
        ).all()
    
    disease_dist = {d[0] or 'Unknown': d[1] for d in diseases}
    
    return jsonify({
        'stats': stats,
        'disease_distribution': disease_dist,
    })

@dashboards.route('/symptom-prediction', methods=['GET', 'POST'])
@login_required
@role_required('patient', 'doctor')
def symptom_prediction():
    """Symptom-based disease prediction with medicine suggestions"""
    user = get_current_user()
    symptoms = advanced_predictor.get_symptom_list()
    grouped_symptoms = advanced_predictor.get_grouped_symptoms()
    predictions = None
    medicine_suggestions = None
    selected_disease = None
    
    if request.method == 'POST':
        selected_symptoms = request.form.getlist('symptoms')
        
        # Convert selected symptoms to underscored format for matching
        normalized_selected = [s.lower().replace(' ', '_') for s in selected_symptoms]
        
        # Create symptoms dict with all possible symptoms, marking selected ones
        symptoms_dict = {}
        for symptom in symptoms:
            normalized_symptom = symptom.lower().replace(' ', '_')
            symptoms_dict[normalized_symptom] = (normalized_symptom in normalized_selected)
        
        # Get predictions (returns list of tuples: disease, confidence, severity)
        predictions = advanced_predictor.predict_disease(symptoms_dict)
        
        # Initialize variables
        selected_disease = None
        medicine_suggestions = None
        
        # Get medicine suggestions for top prediction if available
        if predictions and predictions[0][0] != 'Please select at least one symptom':
            selected_disease = predictions[0][0]
            severity = predictions[0][2]  # 'low', 'moderate', or 'high'
            # Pass selected symptoms to get personalized recommendations from Gemini
            medicine_suggestions = medicine_recommender.get_medicine_suggestions(
                selected_disease, 
                severity, 
                symptoms=selected_symptoms
            )
        
        # Save to database if patient
        if user.role == 'patient':
            patient = user.patient
            top_prediction = predictions[0][0] if predictions else 'Unknown'
            top_confidence = predictions[0][1] if predictions else 0
            
            prediction = Prediction(
                patient_id=patient.id,
                doctor_id=1,  # TODO: assign to actual doctor
                prediction_type='symptoms',
                predicted_disease=top_prediction,
                confidence=top_confidence,
                symptoms=json.dumps(selected_symptoms),
                predicted_diseases=json.dumps([
                    {'disease': p[0], 'confidence': p[1], 'severity': p[2]}
                    for p in predictions
                ]),
                notes=json.dumps(medicine_suggestions) if medicine_suggestions else None,
            )
            db.session.add(prediction)
            db.session.commit()
            
            flash('Prediction saved successfully', 'success')
        
        return render_template('dashboards/symptom_prediction.html',
                             symptoms=symptoms,
                             grouped_symptoms=grouped_symptoms,
                             selected_symptoms=selected_symptoms,
                             predictions=predictions,
                             medicine_suggestions=medicine_suggestions,
                             selected_disease=selected_disease,
                             user=user)
    
    return render_template('dashboards/symptom_prediction.html',
                         symptoms=symptoms,
                         grouped_symptoms=grouped_symptoms,
                         user=user)

# ==================== IMAGE-BASED PREDICTION ROUTES ====================

UPLOAD_DIR = os.path.abspath('uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_image_type(image_bytes):
    """
    Automatically detect whether an image is X-Ray or MRI
    Uses simple heuristics based on image characteristics
    
    Returns: 'xray' or 'mri'
    """
    try:
        from PIL import Image
        import io
        import numpy as np
        
        # Load image
        img = Image.open(io.BytesIO(image_bytes)).convert('L')  # Convert to grayscale
        img_array = np.array(img)
        
        # Calculate image statistics
        mean_intensity = np.mean(img_array)
        std_intensity = np.std(img_array)
        
        # X-rays typically have:
        # - Higher contrast (bones are very bright, soft tissue is dark)
        # - Lower mean intensity (mostly dark with bright spots)
        # - Higher standard deviation
        
        # MRIs typically have:
        # - More uniform intensity distribution
        # - Higher mean intensity overall
        # - Lower standard deviation (more homogeneous)
        
        # Simple classification based on intensity characteristics
        # These thresholds are heuristic and may need adjustment
        if std_intensity > 60 and mean_intensity < 100:
            return 'xray'
        elif mean_intensity >= 100 or std_intensity <= 60:
            return 'mri'
        else:
            # Default to xray if uncertain
            return 'xray'
    
    except Exception as e:
        print(f"Image type detection error: {e}")
        # Default to xray if detection fails
        return 'xray'

@dashboards.route('/medical-imaging-prediction', methods=['GET', 'POST'])
@login_required
@role_required('patient', 'doctor')
def medical_imaging_prediction():
    """Unified X-ray/MRI image analysis with automatic type detection"""
    user = get_current_user()
    predictions = None
    analysis_details = None
    medicine_suggestions = None
    uploaded_filename = None
    detected_type = None
    
    if request.method == 'POST':
        # Check if file was uploaded
        if 'medical_image' not in request.files:
            flash('No image file selected', 'warning')
            return redirect(request.url)
        
        file = request.files['medical_image']
        
        if file.filename == '':
            flash('No image file selected', 'warning')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Only PNG, JPG, JPEG, and PDF are allowed', 'danger')
            return redirect(request.url)
        
        try:
            # Read file
            image_bytes = file.read()
            
            # Automatically detect image type (X-Ray or MRI)
            detected_type = detect_image_type(image_bytes)
            
            # Analyze using appropriate predictor
            if USE_ENHANCED and enhanced_predictor:
                analysis_result = enhanced_predictor.predict(image_bytes)
            else:
                analysis_result = image_predictor.analyze_xray(image_bytes)
            
            if analysis_result.get('success'):
                predictions = analysis_result.get('predictions', [])
                analysis_details = analysis_result
                analysis_details['detected_type'] = detected_type  # Add detected type to results
                
                # Get detected diseases with details
                detected_diseases = analysis_result.get('detected_diseases', [])
                
                # Get medicine suggestions for top prediction
                if detected_diseases:
                    top_disease = detected_diseases[0]['disease']
                    severity = detected_diseases[0].get('severity', 'moderate')
                    medicine_suggestions = medicine_recommender.get_medicine_suggestions(top_disease, severity)
                
                # Save to database if patient
                if user.role == 'patient':
                    patient = user.patient
                    
                    # Save uploaded file
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    prefix = 'XRAY_' if detected_type == 'xray' else 'MRI_'
                    filename = prefix + timestamp + filename
                    filepath = os.path.join(UPLOAD_DIR, filename)
                    file.seek(0)  # Reset file pointer
                    file.save(filepath)
                    uploaded_filename = filename
                    
                    # Create prediction record
                    top_disease = detected_diseases[0]['disease'] if detected_diseases else 'Unknown'
                    top_confidence = detected_diseases[0].get('confidence', 0) if detected_diseases else 0
                    
                    prediction = Prediction(
                        patient_id=patient.id,
                        doctor_id=1,  # TODO: assign to actual doctor
                        image_path=filename,
                        predicted_disease=top_disease,
                        confidence=top_confidence,
                        predicted_diseases=json.dumps(detected_diseases),
                        notes=json.dumps(medicine_suggestions) if medicine_suggestions else None,
                    )
                    db.session.add(prediction)
                    db.session.commit()
                    
                    # Auto-generate PDF report
                    if USE_ENHANCED and enhanced_report_gen:
                        try:
                            patient_info = {
                                'name': patient.full_name,
                                'id': f'P{patient.id}',
                                'age': patient.age if patient.age else 'N/A',
                                'gender': patient.gender if patient.gender else 'N/A',
                                'scan_type': 'Chest X-Ray' if detected_type == 'xray' else 'MRI Scan',
                                'doctor_name': 'HealthGuard System',
                                'institution': 'HealthGuard Medical Center',
                                'report_id': f'{"XR" if detected_type == "xray" else "MR"}{prediction.id}'
                            }
                            
                            report_path = enhanced_report_gen.generate_xray_report(
                                patient_info=patient_info,
                                prediction_result=analysis_result,
                                image_path=filepath,
                                heatmap_path=None  # TODO: Generate heatmap
                            )
                            
                            if report_path:
                                # Store report path in prediction notes
                                prediction.notes = json.dumps({
                                    'medicines': medicine_suggestions,
                                    'report_path': report_path
                                })
                                db.session.commit()
                                flash('Medical imaging analysis completed, saved, and report generated!', 'success')
                        except Exception as e:
                            print(f"Report generation failed: {e}")
                            flash('Medical imaging analysis completed and saved (report generation failed)', 'warning')
                    else:
                        flash('Medical imaging analysis completed and saved', 'success')
            else:
                flash(f"Analysis failed: {analysis_result.get('error', 'Unknown error')}", 'danger')
        
        except Exception as e:
            flash(f'Error processing image: {str(e)}', 'danger')
            import traceback
            traceback.print_exc()
    
    return render_template('dashboards/medical_imaging_prediction.html',
                         predictions=predictions,
                         analysis_details=analysis_details,
                         medicine_suggestions=medicine_suggestions,
                         uploaded_filename=uploaded_filename,
                         detected_type=detected_type,
                         user=user)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@dashboards.route('/xray-prediction', methods=['GET', 'POST'])
@login_required
@role_required('patient', 'doctor')
def xray_prediction():
    """X-ray image analysis and disease prediction"""
    user = get_current_user()
    predictions = None
    analysis_details = None
    medicine_suggestions = None
    uploaded_filename = None
    
    if request.method == 'POST':
        # Check if file was uploaded
        if 'xray_image' not in request.files:
            flash('No image file selected', 'warning')
            return redirect(request.url)
        
        file = request.files['xray_image']
        
        if file.filename == '':
            flash('No image file selected', 'warning')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Only PNG, JPG, JPEG, and PDF are allowed', 'danger')
            return redirect(request.url)
        
        try:
            # Read file and analyze
            image_bytes = file.read()
            
            # Use comprehensive predictor for enhanced disease detection
            if USE_COMPREHENSIVE and comprehensive_predictor:
                analysis_result = comprehensive_predictor.predict(image_bytes)
                logger.info(f"✅ Using comprehensive predictor ({comprehensive_predictor.comprehensive_predictor.disease_count} diseases)")
            elif USE_ENHANCED and enhanced_predictor:
                analysis_result = enhanced_predictor.predict(image_bytes)
                logger.info("Using enhanced predictor")
            else:
                analysis_result = image_predictor.analyze_xray(image_bytes)
                logger.info("Using basic image predictor")
            
            if analysis_result.get('success'):
                # Handle comprehensive predictor format (returns 'diseases_detected') and old formats
                detected_diseases = analysis_result.get('diseases_detected', analysis_result.get('predictions', analysis_result.get('detected_diseases', [])))
                predictions = detected_diseases  # For template compatibility
                analysis_details = analysis_result
                
                # Get medicine suggestions for top prediction
                if detected_diseases:
                    top_disease = detected_diseases[0].get('disease', 'Unknown')
                    severity = detected_diseases[0].get('severity', 'moderate')
                    medicine_suggestions = medicine_recommender.get_medicine_suggestions(top_disease, severity)
                
                # Save to database if patient
                if user.role == 'patient':
                    patient = user.patient
                    
                    # Save uploaded file
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = 'XRAY_' + timestamp + filename
                    filepath = os.path.join(UPLOAD_DIR, filename)
                    file.seek(0)  # Reset file pointer
                    file.save(filepath)
                    uploaded_filename = filename
                    
                    # Create prediction record
                    top_disease = detected_diseases[0].get('disease', 'Unknown') if detected_diseases else 'Unknown'
                    top_confidence = detected_diseases[0].get('confidence', 0) if detected_diseases else 0
                    
                    # Handle confidence as percentage or decimal
                    if top_confidence > 1:
                        top_confidence = top_confidence / 100.0
                    
                    prediction = Prediction(
                        patient_id=patient.id,
                        doctor_id=1,  # TODO: assign to actual doctor
                        image_path=filename,
                        predicted_disease=top_disease,
                        confidence=top_confidence,
                        predicted_diseases=json.dumps(detected_diseases),
                        notes=json.dumps(medicine_suggestions) if medicine_suggestions else None,
                    )
                    db.session.add(prediction)
                    db.session.commit()
                    
                    # Auto-generate PDF report
                    if USE_ENHANCED and enhanced_report_gen:
                        try:
                            patient_info = {
                                'name': patient.full_name,
                                'id': f'P{patient.id}',
                                'age': patient.age if patient.age else 'N/A',
                                'gender': patient.gender if patient.gender else 'N/A',
                                'scan_type': 'Chest X-Ray',
                                'doctor_name': 'HealthGuard System',
                                'institution': 'HealthGuard Medical Center',
                                'report_id': f'XR{prediction.id}'
                            }
                            
                            report_path = enhanced_report_gen.generate_xray_report(
                                patient_info=patient_info,
                                prediction_result=analysis_result,
                                image_path=filepath,
                                heatmap_path=None  # TODO: Generate heatmap
                            )
                            
                            if report_path:
                                # Store report path in prediction notes
                                prediction.notes = json.dumps({
                                    'medicines': medicine_suggestions,
                                    'report_path': report_path
                                })
                                db.session.commit()
                                flash('X-ray analysis completed, saved, and report generated!', 'success')
                        except Exception as e:
                            print(f"Report generation failed: {e}")
                            flash('X-ray analysis completed and saved (report generation failed)', 'warning')
                    else:
                        flash('X-ray analysis completed and saved', 'success')
            else:
                flash(f"Analysis failed: {analysis_result.get('error', 'Unknown error')}", 'danger')
        
        except Exception as e:
            flash(f'Error processing image: {str(e)}', 'danger')
            import traceback
            traceback.print_exc()
    
    return render_template('dashboards/xray_prediction.html',
                         predictions=predictions,
                         analysis_details=analysis_details,
                         medicine_suggestions=medicine_suggestions,
                         uploaded_filename=uploaded_filename,
                         user=user)

@dashboards.route('/mri-prediction', methods=['GET', 'POST'])
@login_required
@role_required('patient', 'doctor')
def mri_prediction():
    """MRI image analysis and disease prediction"""
    user = get_current_user()
    predictions = None
    analysis_details = None
    medicine_suggestions = None
    uploaded_filename = None
    
    if request.method == 'POST':
        # Check if file was uploaded
        if 'mri_image' not in request.files:
            flash('No image file selected', 'warning')
            return redirect(request.url)
        
        file = request.files['mri_image']
        
        if file.filename == '':
            flash('No image file selected', 'warning')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Only PNG, JPG, JPEG, and PDF are allowed', 'danger')
            return redirect(request.url)
        
        try:
            # Read file and analyze
            image_bytes = file.read()
            
            # Use comprehensive predictor for MRI (same system as X-ray for consistency)
            if USE_COMPREHENSIVE and comprehensive_predictor:
                analysis_result = comprehensive_predictor.predict(image_bytes)
                logger.info(f"✅ Using comprehensive predictor ({comprehensive_predictor.comprehensive_predictor.disease_count} diseases)")
            elif USE_ENHANCED and enhanced_predictor:
                analysis_result = enhanced_predictor.predict(image_bytes)
                logger.info("Using enhanced predictor")
            else:
                analysis_result = image_predictor.analyze_xray(image_bytes)
                logger.info("Using basic image predictor")
            
            if analysis_result.get('success'):
                # Handle comprehensive predictor format (returns 'diseases_detected') and old formats
                detected_diseases = analysis_result.get('diseases_detected', analysis_result.get('predictions', analysis_result.get('detected_diseases', [])))
                predictions = detected_diseases  # For template compatibility
                analysis_details = analysis_result
                
                # Get medicine suggestions for top prediction
                if detected_diseases:
                    top_disease = detected_diseases[0].get('disease', 'Unknown')
                    severity = detected_diseases[0].get('severity', 'moderate')
                    medicine_suggestions = medicine_recommender.get_medicine_suggestions(top_disease, severity)
                
                # Save to database if patient
                if user.role == 'patient':
                    patient = user.patient
                    
                    # Save uploaded file
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = 'MRI_' + timestamp + filename
                    filepath = os.path.join(UPLOAD_DIR, filename)
                    file.seek(0)  # Reset file pointer
                    file.save(filepath)
                    uploaded_filename = filename
                    
                    # Create prediction record
                    top_disease = detected_diseases[0]['disease'] if detected_diseases else 'Unknown'
                    top_confidence = detected_diseases[0].get('confidence', 0) if detected_diseases else 0
                    
                    prediction = Prediction(
                        patient_id=patient.id,
                        doctor_id=1,  # TODO: assign to actual doctor
                        image_path=filename,
                        predicted_disease=top_disease,
                        confidence=top_confidence,
                        predicted_diseases=json.dumps(detected_diseases),
                        notes=json.dumps(medicine_suggestions) if medicine_suggestions else None,
                    )
                    db.session.add(prediction)
                    db.session.commit()
                    
                    # Auto-generate PDF report
                    if USE_ENHANCED and enhanced_report_gen:
                        try:
                            patient_info = {
                                'name': patient.full_name,
                                'id': f'P{patient.id}',
                                'age': patient.age if patient.age else 'N/A',
                                'gender': patient.gender if patient.gender else 'N/A',
                                'scan_type': 'MRI Scan',
                                'doctor_name': 'HealthGuard System',
                                'institution': 'HealthGuard Medical Center',
                                'report_id': f'MR{prediction.id}'
                            }
                            
                            report_path = enhanced_report_gen.generate_xray_report(
                                patient_info=patient_info,
                                prediction_result=analysis_result,
                                image_path=filepath,
                                heatmap_path=None  # TODO: Generate heatmap
                            )
                            
                            if report_path:
                                # Store report path in prediction notes
                                prediction.notes = json.dumps({
                                    'medicines': medicine_suggestions,
                                    'report_path': report_path
                                })
                                db.session.commit()
                                flash('MRI analysis completed, saved, and report generated!', 'success')
                        except Exception as e:
                            print(f"Report generation failed: {e}")
                            flash('MRI analysis completed and saved (report generation failed)', 'warning')
                    else:
                        flash('MRI analysis completed and saved', 'success')
            else:
                flash(f"Analysis failed: {analysis_result.get('error', 'Unknown error')}", 'danger')
        
        except Exception as e:
            flash(f'Error processing image: {str(e)}', 'danger')
            import traceback
            traceback.print_exc()
    
    return render_template('dashboards/mri_prediction.html',
                         predictions=predictions,
                         analysis_details=analysis_details,
                         medicine_suggestions=medicine_suggestions,
                         uploaded_filename=uploaded_filename,
                         user=user)

@dashboards.route('/download-report/<int:prediction_id>', methods=['GET'])
@login_required
def download_report(prediction_id):
    """Download prediction report as PDF"""
    user = get_current_user()
    prediction = Prediction.query.get(prediction_id)
    
    if not prediction:
        flash('Prediction not found', 'danger')
        return redirect(request.referrer or url_for('dashboards.patient_dashboard'))
    
    # Check access rights
    if user.role == 'patient' and prediction.patient_id != user.patient.id:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboards.patient_dashboard'))
    
    # Get patient info
    patient = prediction.patient
    
    try:
        # Generate report based on prediction type
        if prediction.prediction_type == 'symptoms':
            symptoms = json.loads(prediction.symptoms) if prediction.symptoms else []
            predictions_data = json.loads(prediction.predicted_diseases) if prediction.predicted_diseases else []
            
            # Convert predictions format
            formatted_predictions = [
                (p.get('disease', 'Unknown'), p.get('confidence', 0), p.get('severity', 'moderate'))
                for p in predictions_data
            ]
            
            medicine_suggestions = None
            if prediction.notes:
                medicine_suggestions = json.loads(prediction.notes)
            
            pdf_bytes = report_generator.generate_symptom_report(
                patient.full_name,
                patient.age or 0,
                symptoms,
                formatted_predictions,
                medicine_suggestions or {}
            )
        else:  # image-based (xray or mri)
            predictions_data = json.loads(prediction.predicted_diseases) if prediction.predicted_diseases else []
            
            medicine_suggestions = None
            if prediction.notes:
                medicine_suggestions = json.loads(prediction.notes)
            
            pdf_bytes = report_generator.generate_image_report(
                patient.full_name,
                patient.age or 0,
                'X-Ray' if prediction.prediction_type == 'xray' else 'MRI',
                predictions_data,
                {'recommendation': {}},
                medicine_suggestions or {}
            )
        
        # Send file
        pdf_bytes.seek(0)  # Reset position to start
        return send_file(
            pdf_bytes,
            mimetype='application/pdf',
            as_attachment=True,
            attachment_filename=f'Medical_Report_{prediction.id}_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('dashboards.patient_dashboard'))

@dashboards.route('/prediction-history', methods=['GET'])
@login_required
@role_required('patient')
def prediction_history():
    """View patient's prediction history"""
    patient = get_current_patient()
    
    if not patient:
        flash('Patient profile not found', 'danger')
        return redirect(url_for('dashboards.patient_dashboard'))
    
    # Get filter parameters
    prediction_type = request.args.get('type', 'all')
    sort_by = request.args.get('sort', 'date_desc')
    
    # Build query
    query = Prediction.query.filter_by(patient_id=patient.id)
    
    # Apply type filter
    if prediction_type != 'all':
        query = query.filter_by(prediction_type=prediction_type)
    
    # Apply sorting
    if sort_by == 'date_asc':
        query = query.order_by(Prediction.created_at.asc())
    else:  # date_desc (default)
        query = query.order_by(Prediction.created_at.desc())
    
    predictions = query.all()
    
    # Parse predictions data for display
    for pred in predictions:
        try:
            pred.parsed_predictions = json.loads(pred.predicted_diseases) if pred.predicted_diseases else []
        except:
            pred.parsed_predictions = []
    
    return render_template('dashboards/prediction_history.html',
                         predictions=predictions,
                         patient=patient,
                         current_filter=prediction_type,
                         current_sort=sort_by)

@dashboards.route('/api/prediction/<int:prediction_id>', methods=['GET'])
@login_required
def api_prediction_details(prediction_id):
    """API endpoint to get prediction details"""
    user = get_current_user()
    prediction = Prediction.query.get(prediction_id)
    
    if not prediction:
        return jsonify({'error': 'Prediction not found'}), 404
    
    # Check access
    if user.role == 'patient' and prediction.patient_id != user.patient.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Prepare response
    response = {
        'id': prediction.id,
        'type': prediction.prediction_type,
        'disease': prediction.predicted_disease,
        'confidence': prediction.confidence,
        'created_at': prediction.created_at.isoformat(),
    }
    
    # Add detailed predictions
    if prediction.predicted_diseases:
        try:
            response['predictions'] = json.loads(prediction.predicted_diseases)
        except:
            response['predictions'] = []
    
    # Add symptoms if available
    if prediction.symptoms:
        try:
            response['symptoms'] = json.loads(prediction.symptoms)
        except:
            response['symptoms'] = []
    
    # Add medicine suggestions if available
    if prediction.notes:
        try:
            response['medicine_suggestions'] = json.loads(prediction.notes)
        except:
            response['medicine_suggestions'] = {}
    
    return jsonify(response)

# ========================================
# ADMIN: Add Doctor and Patient Routes
# ========================================

@dashboards.route('/admin/add-doctor', methods=['POST'])
@login_required
@role_required('admin')
def add_doctor():
    """Add a new doctor to the system"""
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        specialization = request.form.get('specialization', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        license_number = request.form.get('license_number', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validation
        if not all([name, specialization, email, username, password]):
            return jsonify({
                'success': False,
                'message': 'All required fields must be filled'
            }), 400
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Username or email already exists'
            }), 400
        
        # Check if license number exists
        if license_number:
            existing_license = Doctor.query.filter_by(license_number=license_number).first()
            if existing_license:
                return jsonify({
                    'success': False,
                    'message': 'License number already exists'
                }), 400
        
        # Create User
        user = User(
            username=username,
            email=email,
            role='doctor'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Get the user.id
        
        # Create Doctor
        doctor = Doctor(
            user_id=user.id,
            full_name=name,
            specialization=specialization,
            phone=phone,
            license_number=license_number or None
        )
        db.session.add(doctor)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Doctor added successfully',
            'doctor': {
                'id': doctor.id,
                'name': doctor.full_name,
                'specialization': doctor.specialization,
                'email': email,
                'license_number': doctor.license_number
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error adding doctor: {str(e)}'
        }), 500

@dashboards.route('/admin/add-patient', methods=['POST'])
@login_required
@role_required('admin')
def add_patient():
    """Add a new patient to the system"""
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        gender = request.form.get('gender', '').strip()
        address = request.form.get('address', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validation
        if not all([name, email, username, password]):
            return jsonify({
                'success': False,
                'message': 'Name, email, username, and password are required'
            }), 400
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Username or email already exists'
            }), 400
        
        # Validate age
        patient_age = None
        if age:
            try:
                patient_age = int(age)
                if patient_age < 0 or patient_age > 150:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid age value'
                    }), 400
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Age must be a number'
                }), 400
        
        # Create User
        user = User(
            username=username,
            email=email,
            role='patient'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Get the user.id
        
        # Create Patient
        patient = Patient(
            user_id=user.id,
            full_name=name,
            age=patient_age,
            gender=gender or None,
            phone=phone or None,
            address=address or None
        )
        db.session.add(patient)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Patient added successfully',
            'patient': {
                'id': patient.id,
                'name': patient.full_name,
                'age': patient.age,
                'email': email,
                'gender': patient.gender
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error adding patient: {str(e)}'
        }), 500

@dashboards.route('/admin/doctors', methods=['GET'])
@login_required
@role_required('admin')
def get_all_doctors():
    """Get all doctors for the admin dashboard"""
    doctors = Doctor.query.join(User).all()
    return jsonify({
        'success': True,
        'doctors': [{
            'id': d.id,
            'name': d.full_name,
            'specialization': d.specialization,
            'email': d.user.email,
            'license_number': d.license_number
        } for d in doctors]
    })

@dashboards.route('/admin/patients', methods=['GET'])
@login_required
@role_required('admin')
def get_all_patients():
    """Get all patients for the admin dashboard"""
    patients = Patient.query.join(User).all()
    return jsonify({
        'success': True,
        'patients': [{
            'id': p.id,
            'name': p.full_name,
            'age': p.age,
            'email': p.user.email,
            'gender': p.gender
        } for p in patients]
    })

# ========================================
# ADMIN: Settings Page (Remove Doctors/Patients)
# ========================================

@dashboards.route('/admin/settings', methods=['GET'])
@login_required
@role_required('admin')
def admin_settings():
    """Admin settings page for managing doctors and patients"""
    admin = get_current_admin()
    
    # Get all doctors with user info
    doctors = Doctor.query.join(User).all()
    
    # Get all patients with user info
    patients = Patient.query.join(User).all()
    
    return render_template('dashboards/admin_settings.html',
                         admin=admin,
                         doctors=doctors,
                         patients=patients)

@dashboards.route('/admin/remove-doctor/<int:doctor_id>', methods=['POST'])
@login_required
@role_required('admin')
def remove_doctor(doctor_id):
    """Remove a doctor from the system"""
    try:
        doctor = Doctor.query.get(doctor_id)
        
        if not doctor:
            return jsonify({
                'success': False,
                'message': 'Doctor not found'
            }), 404
        
        # Get associated user
        user = User.query.get(doctor.user_id)
        
        # Delete doctor (cascade will handle relationships)
        db.session.delete(doctor)
        
        # Delete associated user
        if user:
            db.session.delete(user)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Doctor {doctor.full_name} removed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error removing doctor: {str(e)}'
        }), 500

@dashboards.route('/admin/remove-patient/<int:patient_id>', methods=['POST'])
@login_required
@role_required('admin')
def remove_patient(patient_id):
    """Remove a patient from the system"""
    try:
        patient = Patient.query.get(patient_id)
        
        if not patient:
            return jsonify({
                'success': False,
                'message': 'Patient not found'
            }), 404
        
        # Get associated user
        user = User.query.get(patient.user_id)
        
        # Delete patient (cascade will handle relationships)
        db.session.delete(patient)
        
        # Delete associated user
        if user:
            db.session.delete(user)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Patient {patient.full_name} removed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error removing patient: {str(e)}'
        }), 500

# ========================================
# ADMIN: Report Generator
# ========================================

@dashboards.route('/admin/report-generator', methods=['GET'])
@login_required
@role_required('admin')
def admin_report_generator():
    """Admin report generator page"""
    admin = get_current_admin()
    
    # Get statistics
    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_users = User.query.count()
    total_predictions = Prediction.query.count()
    
    # Get doctors list
    doctors = Doctor.query.join(User).all()
    
    # Get patients list
    patients = Patient.query.join(User).all()
    
    # Get recent predictions
    recent_predictions = Prediction.query.order_by(
        Prediction.created_at.desc()
    ).limit(10).all()
    
    return render_template('dashboards/admin_report_generator.html',
                         admin=admin,
                         total_doctors=total_doctors,
                         total_patients=total_patients,
                         total_users=total_users,
                         total_predictions=total_predictions,
                         doctors=doctors,
                         patients=patients,
                         recent_predictions=recent_predictions,
                         now=datetime.now())

# ==================== VOICE INPUT / SPEECH-TO-TEXT ROUTES ====================

@dashboards.route('/speech-to-text', methods=['POST'])
@login_required
@role_required('patient', 'doctor')
def speech_to_text():
    """
    Process voice input for symptom detection
    Accepts either audio file or direct transcript from Web Speech API
    """
    try:
        user = get_current_user()
        
        # Check if this is a direct transcript from Web Speech API
        if request.is_json:
            data = request.get_json()
            
            if data.get('use_web_speech') and data.get('transcript'):
                # Process transcript directly (no audio file conversion needed)
                transcript = data['transcript'].strip()
                
                logger.info(f"Processing direct transcript: {transcript}")
                
                # Extract symptoms from transcribed text
                symptoms_dict = symptom_extractor.extract_symptoms(transcript)
                
                # Validate symptoms
                is_valid, error_msg = symptom_extractor.validate_symptoms(symptoms_dict)
                
                if not is_valid:
                    return jsonify({
                        'status': 'error',
                        'message': error_msg,
                        'transcript': transcript,
                        'error_type': 'no_symptoms_detected'
                    }), 400
                
                # Get disease predictions
                predictions = advanced_predictor.predict_disease(symptoms_dict)
                
                # Get medicine suggestions for top prediction
                medicine_suggestions = None
                selected_disease = None
                
                if predictions and predictions[0][0] != 'Please select at least one symptom':
                    selected_disease = predictions[0][0]
                    severity = predictions[0][2] if len(predictions[0]) > 2 else 'moderate'
                    medicine_suggestions = medicine_recommender.get_medicine_suggestions(selected_disease, severity)
                
                # Get symptom summary
                symptom_summary = symptom_extractor.get_symptom_summary(symptoms_dict)
                
                # Save to database if patient
                if user.role == 'patient':
                    patient = user.patient
                    top_prediction = predictions[0][0] if predictions else 'Unknown'
                    top_confidence = predictions[0][1] if predictions else 0
                    
                    prediction = Prediction(
                        patient_id=patient.id,
                        doctor_id=1,  # TODO: assign to actual doctor
                        prediction_type='voice_symptoms',
                        predicted_disease=top_prediction,
                        confidence=top_confidence,
                        symptoms=json.dumps(symptom_summary),
                        predicted_diseases=json.dumps([
                            {'disease': p[0], 'confidence': p[1], 'severity': p[2] if len(p) > 2 else 'moderate'}
                            for p in predictions
                        ]),
                        notes=json.dumps({
                            'transcript': transcript,
                            'detected_symptoms': [k for k, v in symptoms_dict.items() if v],
                            'medicines': medicine_suggestions,
                            'source': 'web_speech_api'
                        }),
                    )
                    db.session.add(prediction)
                    db.session.commit()
                
                # Return success response
                return jsonify({
                    'status': 'success',
                    'transcript': transcript,
                    'confidence': 0.95,  # High confidence for Web Speech API
                    'symptom_summary': symptom_summary,
                    'detected_symptoms': [k.replace('_', ' ').title() for k, v in symptoms_dict.items() if v],
                    'predictions': [
                        {
                            'disease': p[0],
                            'confidence': p[1],
                            'severity': p[2] if len(p) > 2 else 'moderate'
                        }
                        for p in predictions
                    ],
                    'medicine_suggestions': medicine_suggestions,
                    'selected_disease': selected_disease
                }), 200
        
        # Original audio file processing (legacy - requires ffmpeg)
        # Check if audio file is present
        if 'audio' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No audio file or transcript provided',
                'error_type': 'missing_input'
            }), 400
            return jsonify({
                'status': 'error',
                'message': 'No audio file provided',
                'error_type': 'missing_audio'
            }), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No audio file selected',
                'error_type': 'empty_filename'
            }), 400
        
        # Save audio file temporarily
        import tempfile
        temp_dir = tempfile.gettempdir()
        temp_filename = secure_filename(f"voice_input_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.webm")
        temp_path = os.path.join(temp_dir, temp_filename)
        
        try:
            audio_file.save(temp_path)
            
            # Process audio: transcribe and validate language
            result = voice_processor.process_audio_file(temp_path)
            
            # Clean up temp file
            try:
                os.remove(temp_path)
            except:
                pass
            
            # Check if transcription failed
            if not result['success']:
                # If non-English language detected, generate voice feedback
                if result.get('requires_english_prompt'):
                    try:
                        voice_feedback = voice_processor.generate_voice_feedback(
                            "Please speak in English", 
                            lang='en'
                        )
                        
                        # Save voice feedback temporarily
                        feedback_path = os.path.join(temp_dir, f"feedback_{user.id}.mp3")
                        with open(feedback_path, 'wb') as f:
                            f.write(voice_feedback)
                        
                        return jsonify({
                            'status': 'error',
                            'message': result['error_message'],
                            'error_type': 'wrong_language',
                            'detected_language': result.get('language'),
                            'transcript': result.get('transcript'),
                            'voice_feedback_url': f'/dashboard/voice-feedback/{user.id}'
                        }), 400
                    except Exception as e:
                        print(f"Error generating voice feedback: {e}")
                
                return jsonify({
                    'status': 'error',
                    'message': result['error_message'],
                    'error_type': 'transcription_failed'
                }), 400
            
            # Extract symptoms from transcribed text
            transcript = result['transcript']
            symptoms_dict = symptom_extractor.extract_symptoms(transcript)
            
            # Validate symptoms
            is_valid, error_msg = symptom_extractor.validate_symptoms(symptoms_dict)
            
            if not is_valid:
                return jsonify({
                    'status': 'error',
                    'message': error_msg,
                    'transcript': transcript,
                    'error_type': 'no_symptoms_detected'
                }), 400
            
            # Get disease predictions
            predictions = advanced_predictor.predict_disease(symptoms_dict)
            
            # Get medicine suggestions for top prediction
            medicine_suggestions = None
            selected_disease = None
            
            if predictions and predictions[0][0] != 'Please select at least one symptom':
                selected_disease = predictions[0][0]
                severity = predictions[0][2] if len(predictions[0]) > 2 else 'moderate'
                medicine_suggestions = medicine_recommender.get_medicine_suggestions(selected_disease, severity)
            
            # Get symptom summary
            symptom_summary = symptom_extractor.get_symptom_summary(symptoms_dict)
            
            # Save to database if patient
            if user.role == 'patient':
                patient = user.patient
                top_prediction = predictions[0][0] if predictions else 'Unknown'
                top_confidence = predictions[0][1] if predictions else 0
                
                prediction = Prediction(
                    patient_id=patient.id,
                    doctor_id=1,  # TODO: assign to actual doctor
                    prediction_type='voice_symptoms',
                    predicted_disease=top_prediction,
                    confidence=top_confidence,
                    symptoms=json.dumps(symptom_summary),
                    predicted_diseases=json.dumps([
                        {'disease': p[0], 'confidence': p[1], 'severity': p[2] if len(p) > 2 else 'moderate'}
                        for p in predictions
                    ]),
                    notes=json.dumps({
                        'transcript': transcript,
                        'detected_symptoms': [k for k, v in symptoms_dict.items() if v],
                        'medicines': medicine_suggestions
                    }),
                )
                db.session.add(prediction)
                db.session.commit()
            
            # Return success response
            return jsonify({
                'status': 'success',
                'transcript': transcript,
                'confidence': result['confidence'],
                'symptom_summary': symptom_summary,
                'detected_symptoms': [k.replace('_', ' ').title() for k, v in symptoms_dict.items() if v],
                'predictions': [
                    {
                        'disease': p[0],
                        'confidence': p[1],
                        'severity': p[2] if len(p) > 2 else 'moderate'
                    }
                    for p in predictions
                ],
                'medicine_suggestions': medicine_suggestions,
                'selected_disease': selected_disease
            }), 200
            
        except Exception as e:
            # Clean up temp file on error
            try:
                os.remove(temp_path)
            except:
                pass
            raise
            
    except Exception as e:
        print(f"Error in speech-to-text: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}',
            'error_type': 'server_error'
        }), 500

@dashboards.route('/voice-feedback/<int:user_id>', methods=['GET'])
def voice_feedback(user_id):
    """Serve voice feedback audio file"""
    try:
        import tempfile
        temp_dir = tempfile.gettempdir()
        feedback_path = os.path.join(temp_dir, f"feedback_{user_id}.mp3")
        
        if os.path.exists(feedback_path):
            return send_file(feedback_path, mimetype='audio/mpeg')
        else:
            return "Voice feedback not found", 404
            
    except Exception as e:
        print(f"Error serving voice feedback: {e}")
        return "Error serving voice feedback", 500

# ==================== ASHA WORKER ROUTES ====================

@dashboards.route('/asha-dashboard')
@login_required
@role_required('asha_worker')
def asha_dashboard():
    """Asha Worker dashboard - manage patients in their region"""
    asha_worker = get_current_asha_worker()
    if not asha_worker:
        flash('Asha Worker profile not found', 'danger')
        return redirect(url_for('routes.index'))
    
    # Get all patients in this Asha Worker's region
    patients = Patient.query.filter_by(region=asha_worker.region).order_by(Patient.created_at.desc()).all()
    
    # Get statistics
    stats = {
        'total_patients': len(patients),
        'patients_with_disease': len([p for p in patients if p.diagnosed_disease]),
        'recent_patients': len([p for p in patients if (datetime.now() - p.created_at).days <= 7]),
        'region': asha_worker.region
    }
    
    return render_template('dashboards/asha_worker_dashboard.html', 
                         asha_worker=asha_worker, 
                         patients=patients,
                         stats=stats)

@dashboards.route('/asha-worker')
@login_required
@role_required('asha_worker')
def asha_worker_dashboard():
    """Legacy route - redirects to /asha-dashboard"""
    return redirect(url_for('dashboards.asha_dashboard'))

@dashboards.route('/asha-dashboard/add-patient', methods=['POST'])
@login_required
@role_required('asha_worker')
def asha_dashboard_add_patient():
    """Add a new patient by Asha Worker"""
    asha_worker = get_current_asha_worker()
    if not asha_worker:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Asha Worker profile not found'}), 403
        flash('Asha Worker profile not found', 'danger')
        return redirect(url_for('dashboards.asha_dashboard'))
    
    full_name = request.form.get('full_name', '').strip()
    age = request.form.get('age', '').strip()
    gender = request.form.get('gender', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    diagnosed_disease = request.form.get('diagnosed_disease', '').strip()
    medical_history = request.form.get('medical_history', '').strip()
    
    if not full_name:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Patient name is required'}), 400
        flash('Patient name is required', 'danger')
        return redirect(url_for('dashboards.asha_dashboard'))
    
    try:
        # Create new patient (auto-assign region from Asha Worker)
        patient = Patient(
            full_name=full_name,
            age=int(age) if age else None,
            gender=gender if gender else None,
            phone=phone if phone else None,
            address=address if address else None,
            region=asha_worker.region,  # Auto-assign Asha Worker's region
            diagnosed_disease=diagnosed_disease if diagnosed_disease else None,
            medical_history=medical_history if medical_history else None,
            asha_worker_id=asha_worker.id
        )
        db.session.add(patient)
        db.session.commit()
        
        # Return JSON for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': f'Patient {full_name} added successfully',
                'patient': {
                    'id': patient.id,
                    'full_name': patient.full_name,
                    'age': patient.age,
                    'gender': patient.gender,
                    'phone': patient.phone,
                    'address': patient.address,
                    'diagnosed_disease': patient.diagnosed_disease,
                    'medical_history': patient.medical_history,
                    'created_at': patient.created_at.strftime('%b %d, %Y')
                }
            }), 200
        
        flash(f'Patient {full_name} added successfully to {asha_worker.region}', 'success')
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': f'Error adding patient: {str(e)}'}), 500
        flash(f'Error adding patient: {str(e)}', 'danger')
    
    return redirect(url_for('dashboards.asha_dashboard'))

@dashboards.route('/asha-dashboard/remove-patient/<int:patient_id>', methods=['POST'])
@login_required
@role_required('asha_worker')
def asha_dashboard_remove_patient(patient_id):
    """Remove a patient by Asha Worker"""
    asha_worker = get_current_asha_worker()
    if not asha_worker:
        flash('Asha Worker profile not found', 'danger')
        return redirect(url_for('dashboards.asha_dashboard'))
    
    patient = Patient.query.get(patient_id)
    if not patient:
        flash('Patient not found', 'danger')
        return redirect(url_for('dashboards.asha_dashboard'))
    
    # Verify patient is in Asha Worker's region
    if patient.region != asha_worker.region:
        flash('You can only remove patients from your region', 'danger')
        return redirect(url_for('dashboards.asha_dashboard'))
    
    try:
        patient_name = patient.full_name
        db.session.delete(patient)
        db.session.commit()
        flash(f'Patient {patient_name} removed successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing patient: {str(e)}', 'danger')
    
    return redirect(url_for('dashboards.asha_dashboard'))

@dashboards.route('/asha-dashboard/edit-patient/<int:patient_id>', methods=['POST'])
@login_required
@role_required('asha_worker')
def asha_dashboard_edit_patient(patient_id):
    """Edit a patient by Asha Worker"""
    asha_worker = get_current_asha_worker()
    if not asha_worker:
        flash('Asha Worker profile not found', 'danger')
        return redirect(url_for('dashboards.asha_dashboard'))
    
    patient = Patient.query.get(patient_id)
    if not patient:
        flash('Patient not found', 'danger')
        return redirect(url_for('dashboards.asha_dashboard'))
    
    # Verify patient is in Asha Worker's region
    if patient.region != asha_worker.region:
        flash('You can only edit patients from your region', 'danger')
        return redirect(url_for('dashboards.asha_dashboard'))
    
    try:
        patient.full_name = request.form.get('full_name', patient.full_name).strip()
        age = request.form.get('age', '').strip()
        patient.age = int(age) if age else patient.age
        patient.gender = request.form.get('gender', patient.gender)
        patient.phone = request.form.get('phone', patient.phone)
        patient.address = request.form.get('address', patient.address)
        patient.diagnosed_disease = request.form.get('diagnosed_disease', patient.diagnosed_disease)
        patient.medical_history = request.form.get('medical_history', patient.medical_history)
        # Region cannot be changed - locked to Asha Worker's region
        
        db.session.commit()
        flash(f'Patient {patient.full_name} updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating patient: {str(e)}', 'danger')
    
    return redirect(url_for('dashboards.asha_dashboard'))

@dashboards.route('/asha-worker/add-patient', methods=['POST'])
@login_required
@role_required('asha_worker')
def asha_worker_add_patient():
    """Legacy route - redirects to new route"""
    return asha_dashboard_add_patient()

@dashboards.route('/asha-worker/remove-patient/<int:patient_id>', methods=['POST'])
@login_required
@role_required('asha_worker')
def asha_worker_remove_patient(patient_id):
    """Legacy route - redirects to new route"""
    return asha_dashboard_remove_patient(patient_id)

@dashboards.route('/asha-worker/edit-patient/<int:patient_id>', methods=['POST'])
@login_required
@role_required('asha_worker')
def asha_worker_edit_patient(patient_id):
    """Legacy route - redirects to new route"""
    return asha_dashboard_edit_patient(patient_id)


# ============================================================================
# COMPREHENSIVE DISEASE PREDICTION API ENDPOINTS
# ============================================================================

@dashboards.route('/api/diseases', methods=['GET'])
def get_all_diseases():
    """Get all supported diseases with comprehensive information"""
    if not USE_COMPREHENSIVE or not comprehensive_predictor:
        return jsonify({'error': 'Comprehensive predictor not available'}), 503
    
    try:
        diseases_info = comprehensive_predictor.get_supported_diseases()
        return jsonify({
            'success': True,
            'total_diseases': diseases_info['total_diseases'],
            'by_category': diseases_info['by_category'],
            'all_diseases': diseases_info['all_diseases']
        })
    except Exception as e:
        logger.error(f"Error fetching diseases: {e}")
        return jsonify({'error': str(e)}), 500


@dashboards.route('/api/disease/<disease_name>', methods=['GET'])
def get_disease_details(disease_name):
    """Get detailed information about a specific disease"""
    if not USE_COMPREHENSIVE or not comprehensive_predictor:
        return jsonify({'error': 'Comprehensive predictor not available'}), 503
    
    try:
        disease_info = comprehensive_predictor.get_disease_info(disease_name)
        if disease_info:
            return jsonify({
                'success': True,
                'disease': disease_info
            })
        else:
            return jsonify({'error': 'Disease not found'}), 404
    except Exception as e:
        logger.error(f"Error fetching disease details: {e}")
        return jsonify({'error': str(e)}), 500


@dashboards.route('/api/prediction-stats', methods=['GET'])
def get_prediction_stats():
    """Get prediction system statistics"""
    if not USE_COMPREHENSIVE or not comprehensive_predictor:
        return jsonify({'error': 'Comprehensive predictor not available'}), 503
    
    try:
        stats = {
            'total_diseases_supported': comprehensive_predictor.comprehensive_predictor.disease_count,
            'diseases_by_category': {},
            'system_status': 'Active',
            'features': [
                'Ensemble deep learning models (ResNet50, VGG16, InceptionV3)',
                'Advanced image preprocessing with histogram equalization',
                'Multi-disease detection and classification',
                'Severity assessment and risk stratification',
                'Clinical recommendations and specialist referrals',
                '40+ disease categories supported'
            ]
        }
        
        # Count diseases by category
        diseases = comprehensive_predictor.comprehensive_predictor.list_supported_diseases()
        for disease in diseases:
            info = comprehensive_predictor.comprehensive_predictor.get_disease_info(disease)
            if info:
                category = info.category
                stats['diseases_by_category'][category] = stats['diseases_by_category'].get(category, 0) + 1
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Error getting prediction stats: {e}")
        return jsonify({'error': str(e)}), 500
