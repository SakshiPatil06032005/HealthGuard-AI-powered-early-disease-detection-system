"""
Setup script to initialize the application with demo data and environment
"""
import os
import sys
import subprocess
from app import create_app, db
from app.models import User, Admin, Doctor, Patient, DoctorPatient

def setup_demo_data():
    """Create demo users for testing"""
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        db.session.query(DoctorPatient).delete()
        db.session.query(Admin).delete()
        db.session.query(Doctor).delete()
        db.session.query(Patient).delete()
        db.session.query(User).delete()
        
        print("Creating admin user...")
        # Create admin user
        admin_user = User(username='admin', email='admin@hospital.com', role='admin')
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.flush()
        
        admin = Admin(user_id=admin_user.id, full_name='Hospital Admin', phone='+1-555-0001')
        db.session.add(admin)
        
        print("Creating doctor users...")
        # Create doctor users
        doc_users = [
            ('mahima', 'mahima@hospital.com', 'mahima', 'Dr. Mahima Singh', 'Pulmonology'),
            ('drsmith', 'smith@hospital.com', 'doctor123', 'Dr. John Smith', 'Cardiology'),
            ('drbrown', 'brown@hospital.com', 'doctor123', 'Dr. Sarah Brown', 'Neurology'),
        ]
        
        doctors = []
        for username, email, password, name, spec in doc_users:
            doc_user = User(username=username, email=email, role='doctor')
            doc_user.set_password(password)
            db.session.add(doc_user)
            db.session.flush()
            
            doctor = Doctor(user_id=doc_user.id, full_name=name, specialization=spec,
                          phone=f'+1-555-000{len(doctors)+2}', license_number=f'LIC{1000+len(doctors)}')
            db.session.add(doctor)
            doctors.append(doctor)
        
        print("Creating patient users...")
        # Create patient users
        pat_users = [
            ('john_doe', 'john@email.com', 'patient123', 'John Doe', 35, 'M'),
            ('jane_smith', 'jane@email.com', 'patient123', 'Jane Smith', 28, 'F'),
            ('mike_johnson', 'mike@email.com', 'patient123', 'Mike Johnson', 45, 'M'),
        ]
        
        patients = []
        for username, email, password, name, age, gender in pat_users:
            pat_user = User(username=username, email=email, role='patient')
            pat_user.set_password(password)
            db.session.add(pat_user)
            db.session.flush()
            
            patient = Patient(user_id=pat_user.id, full_name=name, age=age, gender=gender,
                            phone=f'+1-555-100{len(patients)}', address='123 Main St, City')
            db.session.add(patient)
            patients.append(patient)
        
        print("Assigning patients to doctors...")
        # Assign patients to doctors
        db.session.flush()  # Ensure all patient IDs are generated
        
        for i, patient in enumerate(patients):
            doctor = doctors[i % len(doctors)]
            # Refresh to get latest ID
            db.session.refresh(patient)
            db.session.refresh(doctor)
            doc_pat = DoctorPatient(doctor_id=doctor.id, patient_id=patient.id)
            db.session.add(doc_pat)
        
        db.session.commit()
        
        print("\n✅ Demo data created successfully!")
        print("\n📋 Demo Credentials:")
        print("Admin: username='admin', password='admin123'")
        print("Doctor: username='mahima', password='mahima'")
        print("         username='drsmith', password='doctor123'")
        print("         username='drbrown', password='doctor123'")
        print("Patient: username='john_doe', password='patient123'")
        print("         username='jane_smith', password='patient123'")
        print("         username='mike_johnson', password='patient123'")

def setup_environment():
    """Create virtual environment and install requirements"""
    print("\nSetting up AI Disease Prediction System...")
    
    # Create venv if it doesn't exist
    if not os.path.exists('venv'):
        print("\n1. Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'])
    
    # Activate venv and install requirements
    print("\n2. Installing requirements...")
    if os.name == 'nt':  # Windows
        pip_path = os.path.join('venv', 'Scripts', 'pip')
    else:  # Linux/Mac
        pip_path = os.path.join('venv', 'bin', 'pip')
    
    subprocess.run([pip_path, 'install', '-r', 'requirements.txt'])

def init_database():
    """Initialize the SQLite database"""
    print("\n3. Initializing database...")
    if os.path.exists('app.db'):
        os.remove('app.db')
    
    # Import here to ensure venv is activated
    from app import create_app
    from app.models import db, User
    
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Create demo users
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        
        doctor = User(username='doctor', role='doctor')
        doctor.set_password('doctor123')
        db.session.add(doctor)
        
        db.session.commit()
        print("✓ Database initialized with demo users")

def create_directories():
    """Create necessary directories"""
    print("\n4. Creating required directories...")
    dirs = ['uploads', 'app/static/heatmaps']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"✓ Created {d}/")

def print_instructions():
    """Show next steps"""
    print("\n✨ Setup Complete! ✨")
    print("\nDemo Credentials:")
    print("1. Admin User")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n2. Doctor User")
    print("   Username: doctor")
    print("   Password: doctor123")
    
    print("\nTo run the application:")
    if os.name == 'nt':  # Windows
        print("1. .\\venv\\Scripts\\activate")
    else:
        print("1. source venv/bin/activate")
    print("2. python run.py")
    print("3. Open http://localhost:3000 in your browser")
    
    print("\nOptional: Set OpenAI API key for medical reports:")
    print("export API_TOKEN=your_openai_key")

if __name__ == '__main__':
    try:
        setup_environment()
        create_directories()
        init_database()
        print_instructions()
    except Exception as e:
        print(f"\n❌ Error during setup: {str(e)}")
        sys.exit(1)