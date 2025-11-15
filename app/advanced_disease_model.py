"""
Advanced Disease Prediction Model - Using trained accuracy model with comprehensive symptom support
Wrapper around the improved disease_model.py with extended 132 symptoms
"""
import os
import json
import numpy as np
from typing import Dict, List, Tuple
from app.disease_model import disease_predictor

class AdvancedDiseasePredictor:
    """Advanced disease predictor using the trained accuracy model with extended symptoms"""
    
    def __init__(self):
        """Initialize with the disease predictor from disease_model.py"""
        self.predictor = disease_predictor
        self.disease_info = self._initialize_disease_info()
    
    def predict_disease(self, symptoms_dict: Dict[str, bool]) -> List[Tuple[str, float, str]]:
        """
        Predict disease from symptoms using the trained accuracy model
        
        Args:
            symptoms_dict: Dictionary with symptom names as keys and boolean values
        
        Returns:
            List of tuples: [(disease_name, confidence_score, severity), ...]
        """
        return self.predictor.predict_disease(symptoms_dict)
    
    def get_symptom_list(self) -> List[str]:
        """Get formatted list of all symptoms"""
        return self.predictor.get_symptom_list()
    
    def get_grouped_symptoms(self) -> Dict[str, List[str]]:
        """Get symptoms organized by category"""
        return self.predictor.get_grouped_symptoms()
    
    def _initialize_disease_info(self) -> Dict:
        """Initialize disease information with severity and recommendations"""
        return {
            'COVID-19': {
                'severity': 'high',
                'description': 'Coronavirus Disease 2019',
                'warning_signs': ['Difficulty breathing', 'Persistent chest pain', 'Confusion'],
                'incubation_period': '5-14 days',
                'recovery_time': '2-4 weeks'
            },
            'Pneumonia': {
                'severity': 'high',
                'description': 'Bacterial or viral lung infection',
                'warning_signs': ['Severe shortness of breath', 'Coughing up blood', 'Chest pain'],
                'incubation_period': '1-3 days',
                'recovery_time': '3-6 weeks'
            },
            'Flu': {
                'severity': 'moderate',
                'description': 'Influenza virus infection',
                'warning_signs': ['High fever', 'Severe fatigue', 'Difficulty breathing'],
                'incubation_period': '1-4 days',
                'recovery_time': '7-10 days'
            },
            'Common Cold': {
                'severity': 'low',
                'description': 'Viral upper respiratory infection',
                'warning_signs': ['Secondary bacterial infection', 'Fever over 38.5°C'],
                'incubation_period': '1-3 days',
                'recovery_time': '7-14 days'
            },
            'Bronchitis': {
                'severity': 'moderate',
                'description': 'Inflammation of airways in lungs',
                'warning_signs': ['Persistent cough', 'Coughing up blood', 'Shortness of breath'],
                'incubation_period': '3-5 days',
                'recovery_time': '2-4 weeks'
            },
            'Asthma': {
                'severity': 'moderate',
                'description': 'Chronic airway inflammation',
                'warning_signs': ['Severe wheezing', 'Difficulty speaking', 'Peak flow <50%'],
                'incubation_period': 'N/A (chronic)',
                'recovery_time': 'Ongoing management'
            },
            'Strep Throat': {
                'severity': 'moderate',
                'description': 'Bacterial throat infection',
                'warning_signs': ['Severe throat pain', 'Difficulty swallowing', 'Fever >39°C'],
                'incubation_period': '2-5 days',
                'recovery_time': '7-10 days with antibiotics'
            },
            'Allergic Rhinitis': {
                'severity': 'low',
                'description': 'Allergic inflammation of nasal passages',
                'warning_signs': ['Persistent symptoms', 'Sinus infection'],
                'incubation_period': 'Minutes to hours after exposure',
                'recovery_time': 'Varies with allergen exposure'
            },
            'Sinusitis': {
                'severity': 'moderate',
                'description': 'Inflammation of sinus cavities',
                'warning_signs': ['Severe pain', 'Vision changes', 'Fever with facial swelling'],
                'incubation_period': 'Variable',
                'recovery_time': '7-14 days'
            },
            'Gastroenteritis': {
                'severity': 'moderate',
                'description': 'Stomach and intestinal inflammation',
                'warning_signs': ['Severe dehydration', 'Bloody stools', 'Severe abdominal pain'],
                'incubation_period': '1-3 days',
                'recovery_time': '3-7 days'
            },
            'Migraine': {
                'severity': 'moderate',
                'description': 'Severe, debilitating headache',
                'warning_signs': ['Sudden severe onset', 'Visual changes', 'Neurological symptoms'],
                'incubation_period': 'N/A (chronic)',
                'recovery_time': '4-72 hours'
            },
        }
    
    def get_disease_details(self, disease_name: str) -> Dict:
        """Get detailed information about a disease"""
        return self.disease_info.get(disease_name, {})

# Global instance
advanced_predictor = AdvancedDiseasePredictor()
