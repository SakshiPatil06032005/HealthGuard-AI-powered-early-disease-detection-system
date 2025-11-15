"""
Medicine Recommendation System
Provides medicine suggestions based on predicted disease using Gemini API
"""
import os
import json
from typing import Dict, List, Tuple

class MedicineRecommendationSystem:
    """
    Provides medicine recommendations based on disease predictions
    Uses both hardcoded knowledge base and Gemini API for personalization
    """
    
    def __init__(self, gemini_api_key: str = None):
        """Initialize medicine recommendation system"""
        self.gemini_api_key = gemini_api_key or os.environ.get('GEMINI_API_KEY', '')
        self.gemini_available = False
        
        # Try to import Gemini
        try:
            import google.generativeai as genai
            if self.gemini_api_key:
                genai.configure(api_key=self.gemini_api_key)
                self.genai = genai
                self.gemini_available = True
                print("✅ Gemini API initialized for medicine recommendations")
        except Exception as e:
            print(f"⚠️ Gemini API not available: {e}")
            self.genai = None
        
        # Medicine knowledge base (disease -> list of medicine info)
        self.medicine_database = self._initialize_medicine_database()
    
    def _initialize_medicine_database(self) -> Dict:
        """Initialize comprehensive medicine database"""
        return {
            'COVID-19': {
                'primary_medicines': [
                    {'name': 'Remdesivir', 'dosage': 'IV 200mg day 1, then 100mg daily', 'days': '5-10 days', 'type': 'Antiviral'},
                    {'name': 'Dexamethasone', 'dosage': '6-8mg daily', 'days': '10 days', 'type': 'Corticosteroid'},
                    {'name': 'Favipiravir', 'dosage': '1600mg x 2 on day 1, then 600mg x 2', 'days': '5-7 days', 'type': 'Antiviral'},
                ],
                'supportive_care': [
                    {'name': 'Paracetamol', 'dosage': '500mg', 'frequency': 'Every 4-6 hours (max 3g/day)', 'type': 'Pain reliever'},
                    {'name': 'Vitamin D3', 'dosage': '1000-4000 IU', 'frequency': 'Daily', 'type': 'Supplement'},
                    {'name': 'Zinc Supplements', 'dosage': '15-30mg', 'frequency': 'Daily', 'type': 'Supplement'},
                    {'name': 'Vitamin C', 'dosage': '500-1000mg', 'frequency': 'Daily', 'type': 'Supplement'},
                ],
                'when_severe': [
                    {'name': 'Tocilizumab', 'dosage': '4-8mg/kg IV', 'indication': 'Severe inflammation'},
                    {'name': 'Monoclonal Antibodies', 'indication': 'Early stage high-risk patients'},
                ],
                'precautions': [
                    'Avoid NSAIDs (may worsen condition)',
                    'Monitor oxygen saturation',
                    'Stay hydrated',
                    'Rest and isolation'
                ]
            },
            
            'Pneumonia': {
                'primary_medicines': [
                    {'name': 'Amoxicillin', 'dosage': '500mg', 'frequency': '3 times daily', 'days': '7-10 days', 'type': 'Antibiotic (bacterial)'},
                    {'name': 'Azithromycin', 'dosage': '500mg day 1, then 250mg daily', 'days': '5-7 days', 'type': 'Antibiotic (atypical)'},
                    {'name': 'Ceftriaxone', 'dosage': '500mg-1g IV', 'frequency': 'Every 12 hours', 'days': '5-10 days', 'type': 'Antibiotic (severe)'},
                ],
                'supportive_care': [
                    {'name': 'Paracetamol', 'dosage': '500mg', 'frequency': 'Every 4-6 hours (max 3g/day)', 'type': 'Pain reliever'},
                    {'name': 'Guaifenesin', 'dosage': '200-400mg', 'frequency': 'Every 4 hours', 'type': 'Expectorant'},
                    {'name': 'Dextromethorphan', 'dosage': '10-20mg', 'frequency': 'Every 6-8 hours', 'type': 'Cough suppressant'},
                ],
                'precautions': [
                    'Complete full antibiotic course',
                    'Chest physiotherapy',
                    'Adequate oxygen if needed',
                    'Monitor for breathing difficulties'
                ]
            },
            
            'Flu': {
                'primary_medicines': [
                    {'name': 'Oseltamivir (Tamiflu)', 'dosage': '75mg', 'frequency': '2 times daily', 'days': '5 days', 'type': 'Antiviral (start within 48 hours)'},
                    {'name': 'Zanamivir', 'dosage': '2 inhalations', 'frequency': 'Twice daily', 'days': '5 days', 'type': 'Antiviral'},
                ],
                'supportive_care': [
                    {'name': 'Paracetamol', 'dosage': '500mg', 'frequency': 'Every 4-6 hours (max 3g/day)', 'type': 'Pain reliever'},
                    {'name': 'Ibuprofen', 'dosage': '200-400mg', 'frequency': 'Every 6 hours', 'type': 'Pain reliever'},
                    {'name': 'Rest and fluids', 'indication': 'Critical for recovery'},
                ],
                'precautions': [
                    'Start antivirals early (within 48 hours of symptoms)',
                    'Avoid spreading to others',
                    'Stay hydrated',
                    'Get flu vaccine next year'
                ]
            },
            
            'Common Cold': {
                'primary_medicines': [
                    {'name': 'No specific antiviral', 'indication': 'Self-limiting viral infection'},
                ],
                'supportive_care': [
                    {'name': 'Paracetamol', 'dosage': '500mg', 'frequency': 'Every 4-6 hours (max 3g/day)', 'type': 'Pain reliever'},
                    {'name': 'Pseudoephedrine', 'dosage': '30-60mg', 'frequency': 'Every 4-6 hours', 'type': 'Decongestant'},
                    {'name': 'Zinc lozenges', 'dosage': '10-15mg', 'frequency': 'Every 2 hours', 'type': 'Immune support'},
                    {'name': 'Vitamin C', 'dosage': '1000mg', 'frequency': 'Daily', 'type': 'Supplement'},
                ],
                'precautions': [
                    'Hydration is essential',
                    'Avoid smoking',
                    'Gargle with salt water',
                    'Use humidifier'
                ]
            },
            
            'Bronchitis': {
                'primary_medicines': [
                    {'name': 'Amoxicillin', 'dosage': '500mg', 'frequency': '3 times daily', 'days': '7 days', 'type': 'Antibiotic'},
                    {'name': 'No antibiotic needed if viral', 'indication': 'Most bronchitis is viral'},
                ],
                'supportive_care': [
                    {'name': 'Dextromethorphan', 'dosage': '10-20mg', 'frequency': 'Every 6-8 hours', 'type': 'Cough suppressant'},
                    {'name': 'Guaifenesin', 'dosage': '200-400mg', 'frequency': 'Every 4 hours', 'type': 'Expectorant'},
                    {'name': 'Paracetamol', 'dosage': '500mg', 'frequency': 'Every 4-6 hours (max 3g/day)', 'type': 'Pain reliever'},
                ],
                'precautions': [
                    'Stay hydrated',
                    'Use humidifier',
                    'Avoid irritants',
                    'Monitor for pneumonia development'
                ]
            },
            
            'Strep Throat': {
                'primary_medicines': [
                    {'name': 'Amoxicillin', 'dosage': '500mg', 'frequency': '3 times daily', 'days': '10 days', 'type': 'Antibiotic'},
                    {'name': 'Penicillin V', 'dosage': '500mg', 'frequency': '2-3 times daily', 'days': '10 days', 'type': 'Antibiotic'},
                ],
                'supportive_care': [
                    {'name': 'Paracetamol', 'dosage': '500mg', 'frequency': 'Every 4-6 hours', 'type': 'Pain reliever'},
                    {'name': 'Throat lozenges', 'indication': 'As needed for comfort'},
                    {'name': 'Salt water gargle', 'frequency': 'Every 2-3 hours', 'type': 'Local relief'},
                ],
                'precautions': [
                    'Complete full antibiotic course (10 days)',
                    'Avoid dairy with antibiotics',
                    'Monitor for complications',
                    'Rest voice'
                ]
            },
            
            'Allergic Rhinitis': {
                'primary_medicines': [
                    {'name': 'Cetirizine', 'dosage': '10mg', 'frequency': 'Once daily', 'type': 'Antihistamine'},
                    {'name': 'Loratadine', 'dosage': '10mg', 'frequency': 'Once daily', 'type': 'Antihistamine'},
                    {'name': 'Fexofenadine', 'dosage': '180mg', 'frequency': 'Once daily', 'type': 'Antihistamine'},
                ],
                'supportive_care': [
                    {'name': 'Nasal saline spray', 'frequency': 'Multiple times daily', 'type': 'Nasal irrigation'},
                    {'name': 'Nasal corticosteroid spray', 'frequency': 'Once daily', 'type': 'Anti-inflammatory'},
                ],
                'precautions': [
                    'Identify and avoid allergens',
                    'Keep environment clean',
                    'Use air purifiers',
                    'HEPA filter pillowcase'
                ]
            },
            
            'Sinusitis': {
                'primary_medicines': [
                    {'name': 'Amoxicillin-clavulanate', 'dosage': '500mg', 'frequency': '3 times daily', 'days': '10-14 days', 'type': 'Antibiotic'},
                    {'name': 'Mometasone', 'frequency': 'Once daily', 'type': 'Nasal corticosteroid'},
                ],
                'supportive_care': [
                    {'name': 'Saline nasal rinse', 'frequency': 'Multiple times daily', 'type': 'Nasal irrigation'},
                    {'name': 'Paracetamol', 'dosage': '500mg', 'frequency': 'Every 4-6 hours', 'type': 'Pain reliever'},
                    {'name': 'Decongestant spray', 'frequency': 'Max 3 days use', 'type': 'Temporary relief'},
                ],
                'precautions': [
                    'Use humidifier',
                    'Apply warm compress',
                    'Avoid decongestants >3 days',
                    'Consider CT scan if chronic'
                ]
            },
            
            'Gastroenteritis': {
                'primary_medicines': [
                    {'name': 'Loperamide', 'dosage': '2mg', 'frequency': 'After each loose stool', 'type': 'Antidiarrheal (use with caution)'},
                    {'name': 'Bismuth subsalicylate', 'dosage': '262mg', 'frequency': 'Every 30 minutes', 'type': 'Antidiarrheal'},
                ],
                'supportive_care': [
                    {'name': 'Oral rehydration solution', 'frequency': 'Frequent small sips', 'type': 'Hydration'},
                    {'name': 'Probiotics', 'frequency': 'Once daily', 'type': 'Gut health'},
                    {'name': 'Light bland diet', 'indication': 'BRAT diet (Bananas, Rice, Applesauce, Toast)'},
                ],
                'precautions': [
                    'Avoid dairy and fatty foods',
                    'Prevent dehydration',
                    'Hand hygiene to prevent spread',
                    'Monitor for severe dehydration'
                ]
            },
            
            'Migraine': {
                'primary_medicines': [
                    {'name': 'Sumatriptan', 'dosage': '50mg', 'frequency': 'As needed', 'type': 'Triptan'},
                    {'name': 'Ibuprofen', 'dosage': '400-600mg', 'frequency': 'At first sign', 'type': 'NSAID'},
                    {'name': 'Aspirin-caffeine combination', 'dosage': 'As per package', 'type': 'Combination'},
                ],
                'preventive': [
                    {'name': 'Propranolol', 'dosage': '40mg', 'frequency': 'Daily', 'type': 'Beta blocker'},
                    {'name': 'Topiramate', 'dosage': '25-100mg', 'frequency': 'Daily', 'type': 'Anticonvulsant'},
                ],
                'supportive_care': [
                    {'name': 'Rest in dark, quiet room', 'indication': 'Essential during migraine'},
                    {'name': 'Cold compress', 'frequency': 'Apply to head'},
                ],
                'precautions': [
                    'Avoid triggers (stress, caffeine, alcohol, hormones)',
                    'Regular sleep schedule',
                    'Regular exercise',
                    'Consider preventive treatment if frequent'
                ]
            }
        }
    
    def get_medicine_suggestions(self, disease: str, severity: str = 'moderate', symptoms: List[str] = None) -> Dict:
        """
        Get comprehensive medicine suggestions for a disease using Gemini API
        
        Args:
            disease: Disease name
            severity: 'low', 'moderate', or 'high'
            symptoms: List of patient symptoms (optional)
            
        Returns:
            Dict with medicine recommendations
        """
        # Try Gemini API first for personalized recommendations
        if self.gemini_available:
            gemini_suggestions = self._get_gemini_suggestions_enhanced(disease, severity, symptoms)
            if gemini_suggestions and 'error' not in gemini_suggestions:
                # Merge with database knowledge if available
                if disease in self.medicine_database:
                    db_info = self.medicine_database[disease]
                    gemini_suggestions['database_medicines'] = db_info.get('primary_medicines', [])[:2]
                return gemini_suggestions
        
        # Fallback to database
        if disease not in self.medicine_database:
            return self._get_fallback_suggestions(disease, severity)
        
        medicine_info = self.medicine_database[disease]
        
        suggestions = {
            'disease': disease,
            'severity': severity,
            'primary_medicines': medicine_info.get('primary_medicines', []),
            'supportive_care': medicine_info.get('supportive_care', []),
            'preventive': medicine_info.get('preventive', []),
            'precautions': medicine_info.get('precautions', []),
            'when_to_seek_help': self._get_warning_signs(disease),
            'source': 'database'
        }
        
        return suggestions
    
    def _get_gemini_suggestions_enhanced(self, disease: str, severity: str, symptoms: List[str] = None) -> Dict:
        """
        Get comprehensive suggestions from Gemini API with structured format
        """
        if not self.gemini_available:
            return None
        
        try:
            # Build detailed prompt
            symptom_text = ""
            if symptoms:
                symptom_text = f"\nPatient symptoms: {', '.join(symptoms)}"
            
            prompt = f"""You are a medical expert AI assistant. Provide treatment recommendations for the following case:

Disease: {disease}
Severity Level: {severity}{symptom_text}

Provide a comprehensive treatment plan with SPECIFIC MEDICINES in the following structured format:

**PRIMARY MEDICATIONS:**
List 3-4 specific medicines (MUST include actual medicine names, not generic advice):
- Medicine name: [Specific brand or generic drug name]
- Dosage: [Exact dosage with unit]
- Frequency: [How often to take]
- Duration: [How many days]
- Purpose: [What it treats]

Example format:
- Medicine name: Paracetamol 500mg
- Dosage: 500mg
- Frequency: Every 6 hours
- Duration: 5 days
- Purpose: Fever and pain relief

**SUPPORTIVE CARE:**
List 3-4 supportive treatments or supplements:
- Treatment name: [Specific supplement/treatment]
- Dosage: [Amount]
- Frequency: [How often]
- Purpose: [Benefits]

**PRECAUTIONS:**
List 5-7 important precautions:
- [Specific precaution or warning]
- [What to avoid]
- [Monitoring requirements]
- [Lifestyle modifications]
- [Drug interactions to watch]

**WHEN TO SEEK EMERGENCY HELP:**
List 4-6 warning signs:
- [Specific symptom requiring immediate attention]
- [Danger signs]
- [When to call emergency services]

**ADDITIONAL RECOMMENDATIONS:**
- Dietary advice: [Specific dietary recommendations]
- Rest and activity: [Rest duration and activity restrictions]
- Expected recovery timeline: [How long until recovery]
- Follow-up care: [When to see doctor again]

IMPORTANT: 
1. ALWAYS provide SPECIFIC medicine names (like Paracetamol, Ibuprofen, Amoxicillin, etc.)
2. DO NOT use generic phrases like "consult a doctor" in the PRIMARY MEDICATIONS section
3. Include actual dosages and frequencies
4. Base recommendations on evidence-based medicine for the given disease
5. Add disclaimer that professional medical consultation is essential

Format your response clearly with the exact headers and bullet points as shown above."""

            model = self.genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            # Parse the response text
            response_text = response.text
            
            # Extract structured information
            suggestions = {
                'disease': disease,
                'severity': severity,
                'full_recommendations': response_text,
                'primary_medicines': self._parse_medicines_from_text(response_text, 'PRIMARY MEDICATIONS'),
                'supportive_care': self._parse_medicines_from_text(response_text, 'SUPPORTIVE CARE'),
                'precautions': self._parse_list_from_text(response_text, 'PRECAUTIONS'),
                'when_to_seek_help': self._parse_list_from_text(response_text, 'WHEN TO SEEK EMERGENCY HELP'),
                'additional_recommendations': self._parse_section(response_text, 'ADDITIONAL RECOMMENDATIONS'),
                'source': 'gemini_ai',
                'note': '⚕️ AI-generated recommendations - Please consult a healthcare professional for personalized treatment'
            }
            
            return suggestions
            
        except Exception as e:
            print(f"⚠️ Gemini API error: {e}")
            return None
    
    def _parse_medicines_from_text(self, text: str, section: str) -> List[Dict]:
        """Parse medicine information from Gemini response"""
        medicines = []
        try:
            # Find section
            if section in text:
                section_start = text.find(section)
                # Find next section or end
                next_section_markers = ['**PRIMARY', '**SUPPORTIVE', '**PRECAUTIONS', '**WHEN TO', '**ADDITIONAL']
                section_end = len(text)
                for marker in next_section_markers:
                    if marker != f"**{section.split(':')[0]}" and marker in text[section_start + len(section):]:
                        potential_end = text.find(marker, section_start + len(section))
                        if potential_end < section_end and potential_end > section_start:
                            section_end = potential_end
                
                section_text = text[section_start:section_end]
                
                # Parse lines - improved parsing logic
                lines = section_text.split('\n')
                current_med = {}
                
                for line in lines[1:]:  # Skip header
                    line = line.strip()
                    
                    # Skip empty lines
                    if not line:
                        if current_med and current_med.get('name'):
                            medicines.append(current_med)
                            current_med = {}
                        continue
                    
                    # Check if line starts with bullet point
                    if line.startswith('-') or line.startswith('*') or line.startswith('•') or line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.'):
                        # Remove bullet point
                        line_text = line.lstrip('-*•0123456789. ').strip()
                        
                        if ':' in line_text:
                            key, value = line_text.split(':', 1)
                            key = key.strip().lower().replace(' ', '_').replace('medicine_name', 'name').replace('medication_name', 'name').replace('treatment_name', 'name')
                            value = value.strip()
                            
                            # Store the key-value pair
                            current_med[key] = value
                        else:
                            # If no colon and we don't have a name yet, this might be the medicine name
                            if not current_med.get('name'):
                                current_med['name'] = line_text
                
                # Add last medicine if exists
                if current_med and current_med.get('name'):
                    medicines.append(current_med)
                
                # If no medicines found, try alternative parsing
                if not medicines and section_text:
                    # Try to extract any medicine names mentioned
                    import re
                    # Look for common medicine name patterns
                    med_pattern = r'(?:^|\n)[-*•]?\s*([A-Z][a-zA-Z]+(?:\s+\d+\s*mg)?)'
                    matches = re.findall(med_pattern, section_text)
                    for match in matches[:4]:
                        if len(match) > 3:  # Filter out very short matches
                            medicines.append({'name': match.strip(), 'type': 'Medication'})
                            
        except Exception as e:
            print(f"⚠️ Error parsing medicines from section '{section}': {e}")
        
        return medicines[:4]  # Return top 4
    
    def _parse_list_from_text(self, text: str, section: str) -> List[str]:
        """Parse list items from Gemini response"""
        items = []
        try:
            if section in text:
                section_start = text.find(section)
                # Find next section
                next_section_markers = ['**PRIMARY', '**SUPPORTIVE', '**PRECAUTIONS', '**WHEN TO', '**ADDITIONAL']
                section_end = len(text)
                for marker in next_section_markers:
                    if marker != f"**{section.split(':')[0]}" and marker in text[section_start + len(section):]:
                        potential_end = text.find(marker, section_start + len(section))
                        if potential_end < section_end and potential_end > section_start:
                            section_end = potential_end
                
                section_text = text[section_start:section_end]
                lines = section_text.split('\n')
                
                for line in lines[1:]:
                    line = line.strip()
                    if line and (line.startswith('-') or line.startswith('*') or line.startswith('•')):
                        item = line[1:].strip()
                        if item:
                            items.append(item)
        except Exception as e:
            print(f"Error parsing list: {e}")
        
        return items[:7]  # Return top 7
    
    def _parse_section(self, text: str, section: str) -> str:
        """Parse a section as text"""
        try:
            if section in text:
                section_start = text.find(section)
                next_section_markers = ['**PRIMARY', '**SUPPORTIVE', '**PRECAUTIONS', '**WHEN TO', '**ADDITIONAL', '---', '***']
                section_end = len(text)
                for marker in next_section_markers:
                    if marker != f"**{section}" and marker in text[section_start + len(section):]:
                        potential_end = text.find(marker, section_start + len(section))
                        if potential_end < section_end and potential_end > section_start:
                            section_end = potential_end
                
                return text[section_start:section_end].strip()
        except:
            pass
        return ""
    
    def _get_fallback_suggestions(self, disease: str, severity: str) -> Dict:
        """Fallback suggestions when both API and database unavailable"""
        
        # Common symptomatic treatments based on disease category
        common_medicines = {
            'fever': [
                {'name': 'Paracetamol', 'dosage': '500mg', 'frequency': 'Every 6 hours', 'purpose': 'Fever and pain relief'},
                {'name': 'Ibuprofen', 'dosage': '400mg', 'frequency': 'Every 8 hours', 'purpose': 'Anti-inflammatory and fever reduction'},
            ],
            'pain': [
                {'name': 'Paracetamol', 'dosage': '500-1000mg', 'frequency': 'Every 6 hours', 'purpose': 'Pain relief'},
                {'name': 'Aspirin', 'dosage': '300-600mg', 'frequency': 'Every 6 hours', 'purpose': 'Pain and inflammation'},
            ],
            'infection': [
                {'name': 'Amoxicillin', 'dosage': '500mg', 'frequency': '3 times daily for 5-7 days', 'purpose': 'Bacterial infection', 'note': 'Requires prescription'},
                {'name': 'Azithromycin', 'dosage': '500mg', 'frequency': 'Once daily for 3 days', 'purpose': 'Bacterial infection', 'note': 'Requires prescription'},
            ],
            'allergy': [
                {'name': 'Cetirizine', 'dosage': '10mg', 'frequency': 'Once daily', 'purpose': 'Antihistamine for allergies'},
                {'name': 'Loratadine', 'dosage': '10mg', 'frequency': 'Once daily', 'purpose': 'Allergy relief'},
            ],
            'cough': [
                {'name': 'Dextromethorphan', 'dosage': '10-20mg', 'frequency': 'Every 6-8 hours', 'purpose': 'Cough suppressant'},
                {'name': 'Guaifenesin', 'dosage': '200-400mg', 'frequency': 'Every 4 hours', 'purpose': 'Expectorant'},
            ],
            'digestive': [
                {'name': 'Omeprazole', 'dosage': '20mg', 'frequency': 'Once daily', 'purpose': 'Acid reflux and stomach issues'},
                {'name': 'Loperamide', 'dosage': '2mg', 'frequency': 'After each loose stool', 'purpose': 'Diarrhea relief'},
            ]
        }
        
        # Try to match disease with common categories
        disease_lower = disease.lower()
        primary_meds = []
        
        if any(word in disease_lower for word in ['fever', 'flu', 'cold', 'viral', 'covid', 'malaria', 'typhoid', 'dengue']):
            primary_meds.extend(common_medicines['fever'])
        
        if any(word in disease_lower for word in ['infection', 'bacterial', 'pneumonia', 'tuberculosis', 'bronchitis']):
            primary_meds.extend(common_medicines['infection'][:1])
        
        if any(word in disease_lower for word in ['allergy', 'rhinitis', 'hay', 'hives', 'urticaria']):
            primary_meds.extend(common_medicines['allergy'])
        
        if any(word in disease_lower for word in ['cough', 'bronchitis', 'asthma']):
            primary_meds.extend(common_medicines['cough'])
        
        if any(word in disease_lower for word in ['gastro', 'stomach', 'diarrhea', 'acid', 'ulcer', 'gerd']):
            primary_meds.extend(common_medicines['digestive'])
        
        if any(word in disease_lower for word in ['pain', 'ache', 'headache', 'migraine', 'arthritis']):
            primary_meds.extend(common_medicines['pain'])
        
        # If no specific match, provide general symptomatic treatment
        if not primary_meds:
            primary_meds = [
                {'name': 'Paracetamol', 'dosage': '500mg', 'frequency': 'Every 6 hours', 'purpose': 'General pain and fever relief'},
                {'name': 'Multivitamin supplements', 'dosage': 'As per package', 'frequency': 'Once daily', 'purpose': 'Nutritional support'},
            ]
        
        return {
            'disease': disease,
            'severity': severity,
            'primary_medicines': primary_meds[:4],  # Limit to 4 medicines
            'supportive_care': [
                {'name': 'Adequate rest', 'frequency': '7-8 hours sleep daily', 'purpose': 'Recovery support'},
                {'name': 'Hydration', 'frequency': 'Drink 8-10 glasses of water daily', 'purpose': 'Maintain body functions'},
                {'name': 'Healthy balanced diet', 'frequency': 'Regular nutritious meals', 'purpose': 'Boost immunity'},
                {'name': 'Vitamin C supplement', 'dosage': '500-1000mg', 'frequency': 'Once daily', 'purpose': 'Immune support'},
            ],
            'precautions': [
                'Consult a healthcare professional for accurate diagnosis and prescription',
                'Do not self-medicate with antibiotics',
                'Follow prescribed dosages and duration',
                'Monitor your symptoms daily',
                'Avoid triggers and allergens if applicable',
                'Maintain good hygiene practices',
                'Seek immediate help if symptoms worsen'
            ],
            'when_to_seek_help': [
                'Severe or rapidly worsening symptoms',
                'High fever (>39°C/102°F) lasting more than 3 days',
                'Difficulty breathing or chest pain',
                'Persistent symptoms beyond expected duration',
                'Signs of dehydration or severe weakness',
                'Any unusual or alarming symptoms'
            ],
            'source': 'fallback',
            'note': '⚠️ These are general symptomatic treatments. Professional medical consultation is essential for proper diagnosis and treatment plan.'
        }
        """Get warning signs for a disease"""
        warning_signs = {
            'COVID-19': [
                'Difficulty breathing or shortness of breath',
                'Persistent chest pain or pressure',
                'Confusion or difficulty concentrating',
                'Inability to wake or stay awake',
                'Lips or face turning blue'
            ],
            'Pneumonia': [
                'Severe shortness of breath',
                'Coughing up blood',
                'Severe chest pain',
                'High fever (>39°C)',
                'Altered consciousness'
            ],
            'Gastroenteritis': [
                'Signs of severe dehydration',
                'Bloody or black stools',
                'Severe abdominal pain',
                'High fever (>38.5°C)',
                'Symptoms lasting >3 days'
            ],
            'Strep Throat': [
                'Difficulty swallowing or breathing',
                'Severe swelling of face or tongue',
                'High fever (>39°C)',
                'Rash spreading',
                'Signs of rheumatic fever'
            ],
        }
        
        return warning_signs.get(disease, ['Persistent symptoms', 'Worsening condition', 'Fever >38.5°C', 'Difficulty breathing'])
    
    
    def _get_warning_signs(self, disease: str) -> List[str]:
        """Get warning signs for a disease"""
        warning_signs = {
            'COVID-19': [
                'Difficulty breathing or shortness of breath',
                'Persistent chest pain or pressure',
                'Confusion or difficulty concentrating',
                'Inability to wake or stay awake',
                'Lips or face turning blue'
            ],
            'Pneumonia': [
                'Severe shortness of breath',
                'Coughing up blood',
                'Severe chest pain',
                'High fever (>39°C)',
                'Altered consciousness'
            ],
            'Gastroenteritis': [
                'Signs of severe dehydration',
                'Bloody or black stools',
                'Severe abdominal pain',
                'High fever (>38.5°C)',
                'Symptoms lasting >3 days'
            ],
            'Strep Throat': [
                'Difficulty swallowing or breathing',
                'Severe swelling of face or tongue',
                'High fever (>39°C)',
                'Rash spreading',
                'Signs of rheumatic fever'
            ],
        }
        
        return warning_signs.get(disease, ['Persistent symptoms', 'Worsening condition', 'Fever >38.5°C', 'Difficulty breathing'])
    
    def get_all_available_diseases(self) -> List[str]:
        """Get list of all diseases with medicine recommendations"""
        return sorted(list(self.medicine_database.keys()))

# Global instance
medicine_recommender = MedicineRecommendationSystem()