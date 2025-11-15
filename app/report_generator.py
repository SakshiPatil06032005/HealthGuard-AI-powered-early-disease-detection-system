"""
Report Generation Module
Generates PDF reports for disease predictions with heatmaps and recommendations
"""
import os
from datetime import datetime
from io import BytesIO
from typing import Dict, List

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

class MedicalReportGenerator:
    """Generate professional medical reports for predictions"""
    
    def __init__(self):
        self.fpdf_available = FPDF_AVAILABLE
    
    def generate_symptom_report(self, patient_name: str, age: int, symptoms: List[str], 
                               predictions: List, medicine_suggestions: Dict) -> BytesIO:
        """
        Generate PDF report for symptom-based prediction
        
        Args:
            patient_name: Patient name
            age: Patient age
            symptoms: List of selected symptoms
            predictions: List of (disease, confidence, severity) tuples
            medicine_suggestions: Medicine recommendations dict
            
        Returns:
            BytesIO object with PDF data
        """
        if not self.fpdf_available:
            return self._generate_text_report(patient_name, age, symptoms, predictions)
        
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Header
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'MEDICAL PREDICTION REPORT', ln=True, align='C')
            pdf.set_line_width(0.5)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            
            # Patient Information
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 5, '', ln=True)
            pdf.cell(0, 8, 'PATIENT INFORMATION', ln=True)
            pdf.set_font('Arial', '', 11)
            pdf.cell(60, 6, f'Name: {patient_name}')
            pdf.cell(0, 6, f'Age: {age} years', ln=True)
            pdf.cell(0, 6, f'Report Date: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', ln=True)
            
            # Symptoms
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'REPORTED SYMPTOMS', ln=True)
            pdf.set_font('Arial', '', 11)
            for i, symptom in enumerate(symptoms, 1):
                pdf.cell(0, 6, f'{i}. {symptom}', ln=True)
            
            # Predictions
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'DISEASE PREDICTIONS', ln=True)
            pdf.set_font('Arial', '', 10)
            
            for i, (disease, confidence, severity) in enumerate(predictions, 1):
                color_map = {'low': (200, 255, 200), 'moderate': (255, 255, 150), 'high': (255, 150, 150)}
                color = color_map.get(severity, (200, 200, 200))
                pdf.set_fill_color(*color)
                
                pdf.cell(80, 8, f'{i}. {disease}', border=1, fill=True)
                pdf.cell(40, 8, f'Confidence: {confidence}%', border=1, fill=True)
                pdf.cell(0, 8, f'Severity: {severity.upper()}', border=1, fill=True, ln=True)
            
            # Medicine Recommendations
            if medicine_suggestions:
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, 'RECOMMENDED TREATMENT', ln=True)
                pdf.set_font('Arial', '', 10)
                
                # Primary medicines
                if medicine_suggestions.get('primary_medicines'):
                    pdf.set_font('Arial', 'B', 11)
                    pdf.cell(0, 6, 'Primary Medicines:', ln=True)
                    pdf.set_font('Arial', '', 10)
                    for med in medicine_suggestions['primary_medicines'][:3]:
                        pdf.cell(0, 6, f"• {med.get('name', 'N/A')} - {med.get('dosage', 'N/A')}", ln=True)
                
                # Supportive care
                if medicine_suggestions.get('supportive_care'):
                    pdf.set_font('Arial', 'B', 11)
                    pdf.cell(0, 6, 'Supportive Care:', ln=True)
                    pdf.set_font('Arial', '', 10)
                    for care in medicine_suggestions['supportive_care'][:3]:
                        pdf.cell(0, 6, f"• {care.get('name', 'N/A')} - {care.get('frequency', 'N/A')}", ln=True)
                
                # Precautions
                if medicine_suggestions.get('precautions'):
                    pdf.set_font('Arial', 'B', 11)
                    pdf.cell(0, 6, 'Important Precautions:', ln=True)
                    pdf.set_font('Arial', '', 10)
                    for precaution in medicine_suggestions['precautions'][:4]:
                        pdf.cell(0, 6, f"• {precaution}", ln=True)
            
            # Footer
            pdf.set_y(-15)
            pdf.set_font('Arial', 'I', 9)
            pdf.cell(0, 10, 'This report is for informational purposes only and should not replace professional medical advice.', 
                    align='C')
            pdf.cell(0, 10, f'Page {pdf.page_no()}', align='C', ln=True)
            
            # Return PDF as bytes
            pdf_output = BytesIO()
            pdf_output.write(pdf.output())
            pdf_output.seek(0)
            return pdf_output
        
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return self._generate_text_report(patient_name, age, symptoms, predictions)
    
    def generate_image_report(self, patient_name: str, age: int, image_type: str,
                             predictions: List, analysis_details: Dict, 
                             medicine_suggestions: Dict, heatmap_path: str = None) -> BytesIO:
        """
        Generate PDF report for image-based prediction
        
        Args:
            patient_name: Patient name
            age: Patient age
            image_type: 'X-ray' or 'MRI'
            predictions: List of predictions
            analysis_details: Analysis details dict
            medicine_suggestions: Medicine recommendations
            heatmap_path: Optional path to heatmap image
            
        Returns:
            BytesIO object with PDF data
        """
        if not self.fpdf_available:
            return self._generate_text_report(patient_name, age, [image_type], predictions)
        
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Header
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, f'{image_type.upper()} ANALYSIS REPORT', ln=True, align='C')
            pdf.set_line_width(0.5)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            
            # Patient Information
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 5, '', ln=True)
            pdf.cell(0, 8, 'PATIENT INFORMATION', ln=True)
            pdf.set_font('Arial', '', 11)
            pdf.cell(60, 6, f'Name: {patient_name}')
            pdf.cell(0, 6, f'Age: {age} years', ln=True)
            pdf.cell(0, 6, f'Examination Type: {image_type}', ln=True)
            pdf.cell(0, 6, f'Report Date: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', ln=True)
            
            # Analysis Details
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'ANALYSIS FINDINGS', ln=True)
            pdf.set_font('Arial', '', 11)
            
            for prediction in predictions:
                pdf.set_font('Arial', 'B', 11)
                disease = prediction.get('disease', 'Unknown')
                confidence = prediction.get('confidence', 0)
                severity = prediction.get('severity', 'unknown')
                
                color_map = {'low': (200, 255, 200), 'moderate': (255, 255, 150), 'high': (255, 150, 150)}
                color = color_map.get(severity, (200, 200, 200))
                pdf.set_fill_color(*color)
                
                pdf.cell(80, 8, f'{disease}', border=1, fill=True)
                pdf.cell(40, 8, f'Confidence: {confidence}%', border=1, fill=True)
                pdf.cell(0, 8, f'Severity: {severity.upper()}', border=1, fill=True, ln=True)
            
            # Recommendation
            if analysis_details.get('recommendation'):
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, 'CLINICAL RECOMMENDATION', ln=True)
                pdf.set_font('Arial', '', 11)
                rec = analysis_details['recommendation']
                pdf.multi_cell(0, 6, f"{rec.get('recommendation', 'N/A')}")
                pdf.cell(0, 6, f"Action: {rec.get('action', 'N/A')}", ln=True)
                pdf.cell(0, 6, f"Follow-up: {rec.get('followup', 'N/A')}", ln=True)
            
            # Medicine Recommendations
            if medicine_suggestions:
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, 'TREATMENT RECOMMENDATIONS', ln=True)
                pdf.set_font('Arial', '', 10)
                
                if medicine_suggestions.get('primary_medicines'):
                    pdf.set_font('Arial', 'B', 11)
                    pdf.cell(0, 6, 'Primary Medicines:', ln=True)
                    pdf.set_font('Arial', '', 10)
                    for med in medicine_suggestions['primary_medicines'][:3]:
                        pdf.cell(0, 6, f"• {med.get('name', 'N/A')} - {med.get('dosage', 'N/A')}", ln=True)
            
            # Footer
            pdf.set_y(-15)
            pdf.set_font('Arial', 'I', 9)
            pdf.cell(0, 10, 'This report is for informational purposes only and should not replace professional medical advice.', 
                    align='C')
            pdf.cell(0, 10, f'Page {pdf.page_no()}', align='C', ln=True)
            
            pdf_output = BytesIO()
            pdf_output.write(pdf.output())
            pdf_output.seek(0)
            return pdf_output
        
        except Exception as e:
            print(f"Error generating image report PDF: {e}")
            return self._generate_text_report(patient_name, age, [image_type], predictions)
    
    def _generate_text_report(self, patient_name: str, age: int, symptoms: List, predictions: List) -> BytesIO:
        """Generate text-based report as fallback"""
        report = f"""
MEDICAL PREDICTION REPORT
=============================

PATIENT INFORMATION
-------------------
Name: {patient_name}
Age: {age} years
Report Date: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

FINDINGS
--------
Symptoms/Examination: {', '.join(symptoms)}

PREDICTIONS
-----------
"""
        for i, pred in enumerate(predictions, 1):
            if isinstance(pred, tuple):
                disease, confidence, severity = pred
                report += f"{i}. {disease} - Confidence: {confidence}% - Severity: {severity}\n"
            else:
                report += f"{i}. {pred}\n"
        
        report += "\n" + "="*50 + "\n"
        report += "Disclaimer: This report is for informational purposes only.\n"
        report += "Please consult a healthcare professional for proper diagnosis and treatment.\n"
        
        text_bytes = BytesIO(report.encode('utf-8'))
        return text_bytes

# Global instance
report_generator = MedicalReportGenerator()
