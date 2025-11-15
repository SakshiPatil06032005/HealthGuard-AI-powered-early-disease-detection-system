"""
Database models for the AI Disease Prediction System
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

db = SQLAlchemy()

class UserRole(Enum):
    """User role enumeration"""
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"
    ASHA_WORKER = "asha_worker"

class User(db.Model):
    """Base User model with role-based access"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='patient')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    admin = db.relationship('Admin', uselist=False, backref='user', cascade='all, delete-orphan')
    doctor = db.relationship('Doctor', uselist=False, backref='user', cascade='all, delete-orphan')
    patient = db.relationship('Patient', uselist=False, backref='user', cascade='all, delete-orphan')
    asha_worker = db.relationship('AshaWorker', uselist=False, backref='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Admin(db.Model):
    """Admin model"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Admin {self.full_name}>'

class Doctor(db.Model):
    """Doctor model"""
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(120), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    license_number = db.Column(db.String(50), unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    patients = db.relationship('DoctorPatient', backref='doctor', cascade='all, delete-orphan')
    predictions = db.relationship('Prediction', backref='doctor', lazy=True)
    
    def __repr__(self):
        return f'<Doctor {self.full_name}>'

class Patient(db.Model):
    """Patient model"""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, unique=True)  # Made nullable for Asha-managed patients
    full_name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    region = db.Column(db.String(100))  # Region for Asha Worker filtering
    medical_history = db.Column(db.Text)
    diagnosed_disease = db.Column(db.String(255))  # For Asha-managed patients
    asha_worker_id = db.Column(db.Integer, db.ForeignKey('asha_workers.id'), nullable=True)  # Link to Asha Worker
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    doctors = db.relationship('DoctorPatient', backref='patient', cascade='all, delete-orphan')
    predictions = db.relationship('Prediction', backref='patient', lazy=True)
    
    def __repr__(self):
        return f'<Patient {self.full_name}>'

class AshaWorker(db.Model):
    """Asha Worker model"""
    __tablename__ = 'asha_workers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(120), nullable=False)
    asha_worker_id = db.Column(db.String(50), unique=True, nullable=False)
    region = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships - Asha workers can manage patients
    patients = db.relationship('Patient', backref='asha_worker', lazy=True)
    
    def __repr__(self):
        return f'<AshaWorker {self.full_name}>'

class DoctorPatient(db.Model):
    """Association table for Doctor-Patient relationship"""
    __tablename__ = 'doctor_patient'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    assigned_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('doctor_id', 'patient_id', name='unique_doctor_patient'),)

class Prediction(db.Model):
    """Medical prediction model for X-ray/MRI and symptom-based predictions"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    prediction_type = db.Column(db.String(50), nullable=True)  # 'xray', 'mri', 'symptoms' - made nullable
    
    # For X-ray/MRI predictions
    image_path = db.Column(db.String(255))
    predicted_disease = db.Column(db.String(100))
    confidence = db.Column(db.Float)
    heatmap_path = db.Column(db.String(255))
    
    # For symptom-based predictions
    symptoms = db.Column(db.Text)  # JSON format
    predicted_diseases = db.Column(db.Text)  # JSON format with diseases and probabilities
    
    # General
    report_path = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Prediction {self.predicted_disease}>'
