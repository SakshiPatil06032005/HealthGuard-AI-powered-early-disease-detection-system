"""
Test script to verify that patients can be created without user_id
"""
import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models import db, Patient, AshaWorker

app = create_app()

with app.app_context():
    print("Testing patient creation without user_id...")
    
    # Try to create a test patient without user_id
    try:
        test_patient = Patient(
            full_name="Test Patient",
            age=30,
            gender="Male",
            phone="1234567890",
            address="Test Address",
            region="Test Region",
            diagnosed_disease="Test Disease",
            medical_history="Test History",
            asha_worker_id=None  # Can be None if no Asha Worker assigned
        )
        
        db.session.add(test_patient)
        db.session.commit()
        
        print(f"✅ SUCCESS! Patient created with ID: {test_patient.id}")
        print(f"   Name: {test_patient.full_name}")
        print(f"   user_id: {test_patient.user_id} (should be None)")
        print(f"   Region: {test_patient.region}")
        
        # Clean up - delete the test patient
        db.session.delete(test_patient)
        db.session.commit()
        print("✅ Test patient cleaned up")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
