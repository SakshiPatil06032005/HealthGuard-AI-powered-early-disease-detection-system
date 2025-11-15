"""
Disease Prediction Model - Predicts diseases from symptoms
Integrated with trained accuracy model from Accuracy_model folder
"""
import os
import pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import json

class DiseasePredictor:
    """Class to handle disease prediction from symptoms using trained accuracy model"""
    
    def __init__(self):
        self.model = None
        self.feature_names = None
        self.label_encoder = None
        self.X_columns = None  # Store training data columns for feature matching
        
        # Try to load the accuracy model first
        self.accuracy_model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Accuracy_model')
        self.accuracy_model_path = os.path.join(self.accuracy_model_dir, 'symptom_model.pkl')
        self.accuracy_encoder_path = os.path.join(self.accuracy_model_dir, 'label_encoder.pkl')
        
        self.load_model()
    
    def load_model(self):
        """Load pre-trained accuracy model from Accuracy_model folder"""
        try:
            # Try loading the accuracy model
            if os.path.exists(self.accuracy_model_path) and os.path.exists(self.accuracy_encoder_path):
                self.model = pickle.load(open(self.accuracy_model_path, "rb"))
                self.label_encoder = pickle.load(open(self.accuracy_encoder_path, "rb"))
                
                # Load dataset columns for feature matching
                self._load_dataset_columns()
                
                print("✅ Accuracy disease prediction model loaded successfully")
                print(f"✅ Model supports {len(self.X_columns)} symptoms")
                print(f"✅ Can predict {len(self.label_encoder.classes_)} diseases")
            else:
                print("⚠️ Accuracy model not found - using extended symptom list for demo")
                self._create_demo_model()
        except Exception as e:
            print(f"❌ Error loading accuracy model: {e}")
            self._create_demo_model()
    
    def _load_dataset_columns(self):
        """Load dataset columns from the training data source"""
        try:
            # Try loading from the same source as training
            url1 = "https://raw.githubusercontent.com/anujdutt9/Disease-Prediction-from-Symptoms/master/dataset/training_data.csv"
            url2 = "https://raw.githubusercontent.com/kaushik-rohit/Disease-Prediction-from-Symptoms/master/Training.csv"
            
            try:
                df = pd.read_csv(url1)
            except:
                df = pd.read_csv(url2)
            
            # Identify target column
            if 'label' in df.columns:
                target_col = 'label'
            elif 'prognosis' in df.columns:
                target_col = 'prognosis'
            else:
                raise Exception("Could not identify target column")
            
            # Store feature columns
            self.X_columns = df.drop(target_col, axis=1).columns.tolist()
            self.feature_names = self.X_columns  # Use these as feature names
            
        except Exception as e:
            print(f"⚠️ Could not load dataset columns: {e}")
            print("Using default extended symptom list")
            self._create_demo_model()
    
    def _create_demo_model(self):
        """Create extended symptom list (132 symptoms) for demo mode"""
        # All 132 symptoms from the new classification
        self.feature_names = [
            # 1. ALLERGY & IMMUNE REACTION SYMPTOMS
            'itching', 'skin_rash', 'nodal_skin_eruptions', 'continuous_sneezing', 'runny_nose',
            'redness_of_eyes', 'watering_from_eyes', 'sinus_pressure', 'throat_irritation',
            'patches_in_throat', 'congestion',
            
            # 2. RESPIRATORY / LUNG SYMPTOMS
            'cough', 'phlegm', 'breathlessness', 'chest_pain', 'high_fever',
            'rusty_sputum', 'mucoid_sputum', 'blood_in_sputum', 'sweating',
            
            # 3. DIGESTIVE / STOMACH & GASTRO SYMPTOMS
            'stomach_pain', 'acidity', 'ulcers_on_tongue', 'vomiting', 'indigestion',
            'abdominal_pain', 'nausea', 'loss_of_appetite', 'diarrhoea', 'constipation',
            'belly_pain', 'stomach_bleeding', 'distention_of_abdomen', 'passage_of_gases',
            'internal_itching', 'dehydration',
            
            # 4. URINARY & KIDNEY SYMPTOMS
            'burning_micturition', 'spotting_urination', 'yellow_urine', 'dark_urine',
            'foul_smell_of_urine', 'bladder_discomfort', 'continuous_feel_of_urine', 'polyuria',
            
            # 5. SKIN & DERMATOLOGY SYMPTOMS
            'blister', 'pus_filled_pimples', 'small_dents_in_nails', 'silver_like_dusting',
            'blackheads', 'skin_peeling', 'scurring', 'dischromic_patches',
            'red_sore_around_nose', 'yellow_crust_ooze', 'inflammatory_nails',
            
            # 6. NEUROLOGICAL / BRAIN & NERVE SYMPTOMS
            'headache', 'dizziness', 'loss_of_balance', 'unsteadiness', 'weakness_of_one_body_side',
            'slurred_speech', 'altered_sensorium', 'coma', 'spinning_movements',
            'visual_disturbances', 'lack_of_concentration',
            
            # 7. JOINT, MUSCLE & BONE SYMPTOMS
            'joint_pain', 'muscle_weakness', 'muscle_pain', 'cramps', 'stiff_neck',
            'swelling_joints', 'movement_stiffness', 'hip_joint_pain', 'knee_pain',
            'painful_walking', 'back_pain', 'weakness_in_limbs',
            
            # 8. HEART & CARDIAC SYMPTOMS
            'fast_heart_rate', 'palpitations', 'prominent_veins_on_calf',
            
            # 9. LIVER, BLOOD & INTERNAL ORGAN SYMPTOMS
            'yellowish_skin', 'yellowing_of_eyes', 'acute_liver_failure', 'fluid_overload',
            'history_of_alcohol_consumption', 'toxic_look_(typhos)',
            
            # 10. ENDOCRINE / HORMONAL SYMPTOMS
            'weight_gain', 'weight_loss', 'restlessness', 'cold_hands_and_feets',
            'lethargy', 'irregular_sugar_level', 'increased_appetite', 'excessive_hunger',
            'family_history', 'mood_swings', 'anxiety',
            
            # 11. FEMALE-SPECIFIC SYMPTOMS
            'abnormal_menstruation',
            
            # 12. INFECTION-RELATED / FEVER / SYSTEMIC
            'shivering', 'chills', 'mild_fever', 'malaise', 'red_spots_over_body',
            'sunken_eyes', 'swelled_lymph_nodes',
            
            # 13. MENTAL HEALTH / BEHAVIORAL
            'irritability', 'depression',
            
            # 14. ANAL & COLON SYMPTOMS
            'pain_in_anal_region', 'pain_during_bowel_movements', 'bloody_stool', 'irritation_in_anus',
            
            # 15. GENERAL HEALTH SYMPTOMS
            'fatigue', 'fever'
        ]
        
        self.X_columns = self.feature_names
        self.label_encoder = None
        self.model = None  # Demo mode - no real model
    
    def predict_disease(self, symptoms_dict):
        """
        Predict disease from symptoms using the accuracy model
        
        Args:
            symptoms_dict: Dictionary with symptom names as keys and boolean values
                          Example: {'fever': True, 'cough': True, 'fatigue': False}
        
        Returns:
            List of tuples: [(disease_name, confidence_score), ...]
        """
        try:
            if self.model is None or self.X_columns is None:
                # Demo mode: use rule-based logic
                return self._demo_predict(symptoms_dict)
            
            # Normalize symptom names
            def normalize(name):
                return str(name).strip().lower().replace(' ', '_').replace('-', '_')
            
            # Create feature mapping
            normalized_col_map = {normalize(col): col for col in self.X_columns}
            
            # Create input row with same columns as training data
            input_row = pd.DataFrame([0] * len(self.X_columns), index=self.X_columns).T
            
            # Mark selected symptoms
            matched = 0
            for symptom_key, is_selected in symptoms_dict.items():
                if is_selected:
                    key = normalize(symptom_key)
                    if key in normalized_col_map:
                        input_row.loc[0, normalized_col_map[key]] = 1
                        matched += 1
            
            if matched == 0:
                return [('Please select at least one symptom', 0.0, 'low')]
            
            # Predict using the trained model
            pred_idx = self.model.predict(input_row)[0]
            pred_proba = self.model.predict_proba(input_row)[0]
            pred_label = self.label_encoder.inverse_transform([pred_idx])[0]
            confidence = pred_proba[pred_idx] * 100
            
            # Get top 3 predictions
            top_indices = np.argsort(pred_proba)[-3:][::-1]
            predictions = []
            for idx in top_indices:
                disease = self.label_encoder.inverse_transform([idx])[0]
                conf = pred_proba[idx] * 100
                # Determine severity based on confidence
                if conf > 70:
                    severity = 'high'
                elif conf > 40:
                    severity = 'moderate'
                else:
                    severity = 'low'
                predictions.append((disease, conf, severity))
            
            return predictions
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            import traceback
            traceback.print_exc()
            return self._demo_predict(symptoms_dict)
    
    def _demo_predict(self, symptoms_dict):
        """Demo prediction using rule-based logic"""
        score = {
            'Pneumonia': 0.0,
            'COVID-19': 0.0,
            'Flu': 0.0,
            'Common Cold': 0.0,
            'Bronchitis': 0.0
        }
        
        # Rule-based scoring
        if symptoms_dict.get('fever'):
            score['COVID-19'] += 15
            score['Flu'] += 10
            score['Pneumonia'] += 5
        if symptoms_dict.get('cough'):
            score['Flu'] += 15
            score['COVID-19'] += 10
            score['Pneumonia'] += 10
            score['Bronchitis'] += 10
        if symptoms_dict.get('shortness_of_breath'):
            score['Pneumonia'] += 20
            score['COVID-19'] += 15
            score['Bronchitis'] += 10
        if symptoms_dict.get('chest_pain'):
            score['Pneumonia'] += 15
            score['Bronchitis'] += 10
        if symptoms_dict.get('sore_throat'):
            score['COVID-19'] += 10
            score['Flu'] += 10
            score['Common Cold'] += 15
        if symptoms_dict.get('fatigue'):
            score['COVID-19'] += 10
            score['Flu'] += 10
        if symptoms_dict.get('loss_of_smell') or symptoms_dict.get('loss_of_taste'):
            score['COVID-19'] += 20
        if symptoms_dict.get('runny_nose') or symptoms_dict.get('stuffy_nose'):
            score['Common Cold'] += 15
            score['Flu'] += 5
        if symptoms_dict.get('nausea') or symptoms_dict.get('vomiting') or symptoms_dict.get('diarrhea'):
            score['COVID-19'] += 10
            score['Flu'] += 10
        
        # Normalize scores
        total = sum(score.values())
        if total == 0:
            return [('Consultation Recommended', 50.0, 'moderate')]
        
        predictions = []
        for disease in score:
            conf = (score[disease] / total) * 100
            if conf > 70:
                severity = 'high'
            elif conf > 40:
                severity = 'moderate'
            else:
                severity = 'low'
            predictions.append((disease, conf, severity))
        
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        return [(d, round(c, 1), s) for d, c, s in predictions if c > 5.0]
    
    def get_symptom_list(self):
        """Return list of all available symptoms (formatted for display)"""
        if self.feature_names:
            return [s.replace('_', ' ').title() for s in self.feature_names]
        return []
    
    def get_grouped_symptoms(self):
        """Return symptoms grouped by category for better UI organization"""
        return {
            '🟩 Allergy & Immune': [
                'itching', 'skin_rash', 'nodal_skin_eruptions', 'continuous_sneezing', 'runny_nose',
                'redness_of_eyes', 'watering_from_eyes', 'sinus_pressure', 'throat_irritation',
                'patches_in_throat', 'congestion'
            ],
            '🟥 Respiratory / Lung': [
                'cough', 'phlegm', 'breathlessness', 'chest_pain', 'high_fever',
                'rusty_sputum', 'mucoid_sputum', 'blood_in_sputum', 'sweating'
            ],
            '🟨 Digestive / Stomach': [
                'stomach_pain', 'acidity', 'ulcers_on_tongue', 'vomiting', 'indigestion',
                'abdominal_pain', 'nausea', 'loss_of_appetite', 'diarrhoea', 'constipation',
                'belly_pain', 'stomach_bleeding', 'distention_of_abdomen', 'passage_of_gases',
                'internal_itching', 'dehydration'
            ],
            '🟫 Urinary & Kidney': [
                'burning_micturition', 'spotting_urination', 'yellow_urine', 'dark_urine',
                'foul_smell_of_urine', 'bladder_discomfort', 'continuous_feel_of_urine', 'polyuria'
            ],
            '🟧 Skin & Dermatology': [
                'blister', 'pus_filled_pimples', 'small_dents_in_nails', 'silver_like_dusting',
                'blackheads', 'skin_peeling', 'scurring', 'dischromic_patches',
                'red_sore_around_nose', 'yellow_crust_ooze', 'inflammatory_nails'
            ],
            '🟪 Neurological / Brain': [
                'headache', 'dizziness', 'loss_of_balance', 'unsteadiness', 'weakness_of_one_body_side',
                'slurred_speech', 'altered_sensorium', 'coma', 'spinning_movements',
                'visual_disturbances', 'lack_of_concentration'
            ],
            '🟦 Joint, Muscle & Bone': [
                'joint_pain', 'muscle_weakness', 'muscle_pain', 'cramps', 'stiff_neck',
                'swelling_joints', 'movement_stiffness', 'hip_joint_pain', 'knee_pain',
                'painful_walking', 'back_pain', 'weakness_in_limbs'
            ],
            '🔵 Heart & Cardiac': [
                'fast_heart_rate', 'chest_pain', 'palpitations', 'prominent_veins_on_calf'
            ],
            '🟣 Liver & Blood': [
                'yellowish_skin', 'yellowing_of_eyes', 'acute_liver_failure', 'fluid_overload',
                'history_of_alcohol_consumption', 'toxic_look_(typhos)'
            ],
            '🟢 Endocrine / Hormonal': [
                'weight_gain', 'weight_loss', 'restlessness', 'cold_hands_and_feets',
                'lethargy', 'irregular_sugar_level', 'increased_appetite', 'excessive_hunger',
                'family_history', 'mood_swings', 'anxiety'
            ],
            '🟤 Female-Specific': [
                'abnormal_menstruation'
            ],
            '⚪ Infection / Fever': [
                'shivering', 'chills', 'mild_fever', 'high_fever', 'malaise', 
                'red_spots_over_body', 'sunken_eyes', 'swelled_lymph_nodes'
            ],
            '🟡 Mental Health': [
                'irritability', 'depression', 'restlessness', 'lack_of_concentration', 'anxiety'
            ],
            '🔶 Anal & Colon': [
                'pain_in_anal_region', 'pain_during_bowel_movements', 'bloody_stool', 'irritation_in_anus'
            ],
            '🔻 General Health': [
                'fatigue', 'weakness_in_limbs', 'sweating', 'breathlessness', 'dizziness', 'fever'
            ]
        }

# Global disease predictor instance
disease_predictor = DiseasePredictor()
