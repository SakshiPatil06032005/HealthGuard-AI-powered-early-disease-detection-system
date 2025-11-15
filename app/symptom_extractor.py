"""
Symptom Extraction Module
Extracts symptoms from natural language text using NLP techniques
"""
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SymptomExtractor:
    """Extracts symptoms from natural language descriptions"""
    
    def __init__(self):
        """Initialize symptom extractor with symptom keywords"""
        
        # Comprehensive symptom keywords mapping
        self.symptom_keywords = {
            'fever': ['fever', 'high temperature', 'hot', 'burning', 'pyrexia', 'temperature'],
            'cough': ['cough', 'coughing', 'tussis'],
            'fatigue': ['tired', 'fatigue', 'exhausted', 'weakness', 'weak', 'energy loss', 'lethargy'],
            'shortness_of_breath': ['breathless', 'shortness of breath', 'difficulty breathing', 'dyspnea', 
                                   'hard to breathe', 'breathing problem', 'cant breathe'],
            'chest_pain': ['chest pain', 'chest hurts', 'pain in chest', 'chest discomfort'],
            'sore_throat': ['sore throat', 'throat pain', 'throat hurts', 'scratchy throat'],
            'headache': ['headache', 'head pain', 'head hurts', 'migraine', 'head ache'],
            'muscle_pain': ['muscle pain', 'body pain', 'body ache', 'myalgia', 'muscles hurt', 'aching'],
            'chills': ['chills', 'shivering', 'shaking', 'cold', 'shivers'],
            'nausea': ['nausea', 'feel sick', 'queasy', 'upset stomach', 'feel nauseous'],
            'vomiting': ['vomiting', 'throwing up', 'vomit', 'puke', 'emesis'],
            'diarrhea': ['diarrhea', 'loose stool', 'watery stool', 'frequent bowel', 'diarrhoea'],
            'loss_of_smell': ['lost smell', 'no smell', 'cant smell', 'smell loss', 'anosmia'],
            'loss_of_taste': ['lost taste', 'no taste', 'cant taste', 'taste loss', 'ageusia'],
            'runny_nose': ['runny nose', 'running nose', 'nasal discharge', 'nose dripping'],
            'stuffy_nose': ['stuffy nose', 'blocked nose', 'nasal congestion', 'nose blocked', 'stuffed nose'],
            'sneezing': ['sneezing', 'sneeze', 'achoo'],
            'itchy_eyes': ['itchy eyes', 'eyes itch', 'eye itching'],
            'watery_eyes': ['watery eyes', 'teary eyes', 'eyes watering', 'tearing'],
            'skin_rash': ['rash', 'skin rash', 'skin eruption', 'skin irritation', 'red spots'],
            'dizziness': ['dizzy', 'dizziness', 'lightheaded', 'vertigo', 'spinning'],
            'sweating': ['sweating', 'perspiration', 'sweats', 'night sweats'],
            'abdominal_pain': ['stomach pain', 'abdominal pain', 'belly pain', 'tummy ache', 'stomach ache'],
            'back_pain': ['back pain', 'backache', 'spine pain', 'back hurts'],
            'joint_pain': ['joint pain', 'joints hurt', 'arthralgia', 'knee pain', 'elbow pain'],
            'swelling': ['swelling', 'swollen', 'inflammation', 'edema', 'puffiness'],
            'difficulty_swallowing': ['hard to swallow', 'difficulty swallowing', 'swallowing problem', 'dysphagia'],
            'loss_of_appetite': ['no appetite', 'loss of appetite', 'dont feel like eating', 'not hungry'],
            'weight_loss': ['weight loss', 'losing weight', 'lost weight'],
            'night_sweats': ['night sweats', 'sweating at night', 'waking up sweating'],
            'confusion': ['confused', 'confusion', 'disoriented', 'mental fog'],
            'wheezing': ['wheezing', 'whistling breath', 'breathing sounds'],
        }
        
        # Negation words
        self.negation_words = ['no', 'not', 'never', 'without', 'dont', "don't", 'doesnt', "doesn't", 
                               'neither', 'nor', 'none', 'nothing']
        
        logger.info(f"✅ Symptom extractor initialized with {len(self.symptom_keywords)} symptom patterns")
    
    def extract_symptoms(self, text):
        """
        Extract symptoms from natural language text
        
        Args:
            text: Natural language description of symptoms
            
        Returns:
            dict: Dictionary with symptom names as keys and boolean values
                 Example: {'fever': True, 'cough': True, 'fatigue': False}
        """
        if not text:
            return {}
        
        # Normalize text
        text = text.lower().strip()
        
        # Initialize result dictionary
        detected_symptoms = {}
        
        # Process each symptom
        for symptom_name, keywords in self.symptom_keywords.items():
            # Check if any keyword is present
            found = False
            negated = False
            
            for keyword in keywords:
                # Create regex pattern for whole word matching
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = list(re.finditer(pattern, text))
                
                if matches:
                    found = True
                    
                    # Check for negation in surrounding context
                    for match in matches:
                        start_pos = max(0, match.start() - 20)  # Look 20 chars before
                        context = text[start_pos:match.start()]
                        
                        # Check if any negation word is in the context
                        if any(neg_word in context.split() for neg_word in self.negation_words):
                            negated = True
                            break
                    
                    if found:
                        break
            
            # Set symptom value (True if found and not negated)
            detected_symptoms[symptom_name] = found and not negated
        
        # Log detected symptoms
        active_symptoms = [k for k, v in detected_symptoms.items() if v]
        logger.info(f"Detected symptoms: {', '.join(active_symptoms) if active_symptoms else 'None'}")
        
        return detected_symptoms
    
    def get_symptom_summary(self, symptoms_dict):
        """
        Get a human-readable summary of detected symptoms
        
        Args:
            symptoms_dict: Dictionary of symptoms
            
        Returns:
            str: Summary text
        """
        active = [k.replace('_', ' ').title() for k, v in symptoms_dict.items() if v]
        
        if not active:
            return "No symptoms detected"
        elif len(active) == 1:
            return f"Detected symptom: {active[0]}"
        else:
            return f"Detected symptoms: {', '.join(active[:-1])} and {active[-1]}"
    
    def validate_symptoms(self, symptoms_dict):
        """
        Validate that at least one symptom is present
        
        Args:
            symptoms_dict: Dictionary of symptoms
            
        Returns:
            tuple: (is_valid, error_message)
        """
        active_count = sum(1 for v in symptoms_dict.values() if v)
        
        if active_count == 0:
            return False, "No symptoms detected in your description. Please describe your symptoms clearly."
        
        return True, None

# Global instance
symptom_extractor = SymptomExtractor()
