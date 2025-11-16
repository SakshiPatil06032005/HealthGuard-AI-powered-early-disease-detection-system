"""
Dashboard Report Display Component
Displays medical imaging analysis results directly on the dashboard board
Shows comprehensive prediction details, confidence scores, severity, and recommendations
No PDF generation - everything rendered as rich HTML on the dashboard
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DashboardReportDisplay:
    """Generate rich HTML report display for dashboard"""
    
    def __init__(self):
        self.logger = logger
    
    def generate_prediction_report(self, 
                                   predictions: List[Dict],
                                   analysis_details: Dict,
                                   medicine_suggestions: Optional[Dict] = None,
                                   patient_info: Optional[Dict] = None) -> Dict:
        """
        Generate comprehensive report data for dashboard display
        
        Args:
            predictions: List of prediction dictionaries with disease, confidence, severity
            analysis_details: Full analysis result details
            medicine_suggestions: Medicine recommendations dictionary
            patient_info: Patient information
            
        Returns:
            Dictionary containing report data ready for dashboard display
        """
        try:
            report_data = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'overall_confidence': analysis_details.get('overall_confidence', 0),
                'analysis_method': analysis_details.get('analysis_method', 'Ensemble Deep Learning'),
                'model_info': analysis_details.get('model_info', {}),
                'predictions': self._format_predictions(predictions),
                'disease_summary': self._generate_disease_summary(predictions),
                'severity_analysis': self._analyze_severity(predictions),
                'confidence_analysis': self._analyze_confidence(predictions),
                'recommendations': self._generate_recommendations(predictions, medicine_suggestions),
                'clinical_insights': self._generate_clinical_insights(predictions, analysis_details),
                'warnings': self._generate_warnings(predictions),
                'medicine_suggestions': medicine_suggestions or {},
                'patient_info': patient_info or {}
            }
            
            logger.info(f"✅ Dashboard report generated with {len(predictions)} predictions")
            return report_data
            
        except Exception as e:
            logger.error(f"❌ Error generating dashboard report: {e}")
            return {
                'success': False,
                'error': str(e),
                'predictions': [],
                'recommendations': []
            }
    
    def _format_predictions(self, predictions: List[Dict]) -> List[Dict]:
        """Format predictions with enhanced details"""
        formatted = []
        for pred in predictions:
            formatted.append({
                'disease': pred.get('disease', 'Unknown'),
                'confidence': pred.get('confidence', 0),
                'confidence_percent': f"{pred.get('confidence', 0):.1f}%",
                'severity': pred.get('severity', 'moderate').lower(),
                'severity_badge': self._get_severity_badge(pred.get('severity', 'moderate')),
                'description': pred.get('description', 'No description available'),
                'treatment': pred.get('treatment', 'Consult healthcare professional'),
                'referral': pred.get('referral', 'General Practitioner'),
                'is_critical': pred.get('severity', 'moderate').lower() == 'high'
            })
        return formatted
    
    def _get_severity_badge(self, severity: str) -> Dict:
        """Get severity badge styling"""
        severity = severity.lower()
        badges = {
            'low': {'color': 'bg-green-100 border-green-400 text-green-800', 'icon': '✓', 'label': 'LOW RISK'},
            'moderate': {'color': 'bg-yellow-100 border-yellow-400 text-yellow-800', 'icon': '⚠', 'label': 'MODERATE RISK'},
            'high': {'color': 'bg-red-100 border-red-400 text-red-800', 'icon': '⛔', 'label': 'HIGH RISK'}
        }
        return badges.get(severity, badges['moderate'])
    
    def _generate_disease_summary(self, predictions: List[Dict]) -> Dict:
        """Generate disease summary statistics"""
        if not predictions:
            return {'total': 0, 'critical': 0, 'high_confidence': 0}
        
        return {
            'total': len(predictions),
            'critical': sum(1 for p in predictions if p.get('severity', '').lower() == 'high'),
            'high_confidence': sum(1 for p in predictions if p.get('confidence', 0) > 80),
            'moderate_risk': sum(1 for p in predictions if p.get('severity', '').lower() == 'moderate'),
            'low_risk': sum(1 for p in predictions if p.get('severity', '').lower() == 'low'),
            'top_disease': predictions[0].get('disease', 'None') if predictions else 'None',
            'top_confidence': predictions[0].get('confidence', 0) if predictions else 0
        }
    
    def _analyze_severity(self, predictions: List[Dict]) -> Dict:
        """Analyze overall severity distribution"""
        severity_dist = {'low': 0, 'moderate': 0, 'high': 0}
        for pred in predictions:
            severity = pred.get('severity', 'moderate').lower()
            if severity in severity_dist:
                severity_dist[severity] += 1
        
        return {
            'distribution': severity_dist,
            'overall_risk': self._calculate_overall_risk(severity_dist),
            'requires_urgent_attention': severity_dist['high'] > 0
        }
    
    def _analyze_confidence(self, predictions: List[Dict]) -> Dict:
        """Analyze confidence distribution"""
        if not predictions:
            return {'average': 0, 'min': 0, 'max': 0, 'reliability': 'Low'}
        
        confidences = [p.get('confidence', 0) for p in predictions]
        avg_conf = sum(confidences) / len(confidences)
        
        return {
            'average': avg_conf,
            'min': min(confidences),
            'max': max(confidences),
            'reliability': self._rate_reliability(avg_conf),
            'high_confidence_count': sum(1 for c in confidences if c > 80)
        }
    
    def _rate_reliability(self, confidence: float) -> str:
        """Rate prediction reliability"""
        if confidence >= 85:
            return 'Very High'
        elif confidence >= 70:
            return 'High'
        elif confidence >= 55:
            return 'Moderate'
        else:
            return 'Low'
    
    def _calculate_overall_risk(self, severity_dist: Dict) -> str:
        """Calculate overall risk level"""
        if severity_dist['high'] > 0:
            return 'HIGH'
        elif severity_dist['moderate'] > 0:
            return 'MODERATE'
        else:
            return 'LOW'
    
    def _generate_recommendations(self, predictions: List[Dict], medicine_suggestions: Optional[Dict]) -> List[Dict]:
        """Generate clinical recommendations"""
        recommendations = []
        
        # Add specific disease recommendations
        for pred in predictions[:3]:  # Top 3 diseases
            disease = pred.get('disease', 'Unknown')
            severity = pred.get('severity', 'moderate').lower()
            treatment = pred.get('treatment', 'Consult healthcare professional')
            
            recommendations.append({
                'disease': disease,
                'action': treatment,
                'priority': 'High' if severity == 'high' else 'Medium' if severity == 'moderate' else 'Low',
                'referral': pred.get('referral', 'General Practitioner'),
                'follow_up': self._get_follow_up_time(severity)
            })
        
        # Add medicine recommendations
        if medicine_suggestions:
            recommendations.append({
                'type': 'medication',
                'disease': predictions[0].get('disease', 'Unknown') if predictions else 'General',
                'primary_medicines': medicine_suggestions.get('primary_medicines', []),
                'precautions': medicine_suggestions.get('precautions', [])
            })
        
        return recommendations
    
    def _get_follow_up_time(self, severity: str) -> str:
        """Get recommended follow-up time"""
        severity = severity.lower()
        follow_ups = {
            'high': 'Immediate - Same day',
            'moderate': '1-3 days',
            'low': '1-2 weeks'
        }
        return follow_ups.get(severity, '1-2 weeks')
    
    def _generate_clinical_insights(self, predictions: List[Dict], analysis_details: Dict) -> List[str]:
        """Generate clinical insights from predictions"""
        insights = []
        
        if not predictions:
            return ['No significant findings detected']
        
        # Top disease insight
        top_pred = predictions[0]
        disease = top_pred.get('disease', 'Unknown')
        confidence = top_pred.get('confidence', 0)
        severity = top_pred.get('severity', 'moderate').lower()
        
        if severity == 'high':
            insights.append(f"⚠️ PRIMARY FINDING: High confidence detection of {disease} ({confidence:.1f}%). Urgent medical attention recommended.")
        elif severity == 'moderate':
            insights.append(f"⚠️ FINDING: {disease} detected with {confidence:.1f}% confidence. Follow-up medical consultation advised.")
        else:
            insights.append(f"✓ {disease} detected with {confidence:.1f}% confidence. Monitor and follow routine care.")
        
        # Multiple findings insight
        if len(predictions) > 1:
            insights.append(f"Multiple findings detected ({len(predictions)} conditions). See detailed analysis below.")
        
        # Confidence insight
        avg_confidence = sum(p.get('confidence', 0) for p in predictions) / len(predictions)
        if avg_confidence >= 85:
            insights.append("✓ High confidence predictions based on ensemble deep learning analysis.")
        elif avg_confidence >= 70:
            insights.append("⚠️ Moderate confidence predictions. Recommended for expert review.")
        else:
            insights.append("⚠️ Lower confidence findings. Professional medical review strongly recommended.")
        
        # Analysis method
        method = analysis_details.get('analysis_method', 'Unknown')
        insights.append(f"Analysis Method: {method}")
        
        return insights
    
    def _generate_warnings(self, predictions: List[Dict]) -> List[Dict]:
        """Generate important warnings"""
        warnings = []
        
        # Critical severity warning
        critical_count = sum(1 for p in predictions if p.get('severity', '').lower() == 'high')
        if critical_count > 0:
            warnings.append({
                'level': 'critical',
                'message': f'{critical_count} critical finding(s) detected. Immediate medical attention required.',
                'icon': '⛔'
            })
        
        # Low confidence warning
        low_conf_count = sum(1 for p in predictions if p.get('confidence', 0) < 60)
        if low_conf_count > 0:
            warnings.append({
                'level': 'warning',
                'message': f'{low_conf_count} finding(s) with low confidence. Professional review recommended.',
                'icon': '⚠️'
            })
        
        # General disclaimer
        warnings.append({
            'level': 'info',
            'message': 'This AI analysis is for informational purposes only. Always consult healthcare professionals for diagnosis and treatment.',
            'icon': 'ℹ️'
        })
        
        return warnings
    
    def generate_html_display(self, report_data: Dict) -> str:
        """Generate HTML for dashboard display (can be used in templates)"""
        if not report_data.get('success'):
            return f"<div class='alert alert-danger'>Error: {report_data.get('error', 'Unknown error')}</div>"
        
        # This method returns structured data - actual HTML rendering 
        # is done in the Jinja2 templates for better integration
        return report_data


# Global instance
dashboard_report_display = DashboardReportDisplay()


def generate_dashboard_report(predictions: List[Dict],
                             analysis_details: Dict,
                             medicine_suggestions: Optional[Dict] = None,
                             patient_info: Optional[Dict] = None) -> Dict:
    """
    Convenience function to generate dashboard report
    
    Args:
        predictions: List of prediction dictionaries
        analysis_details: Full analysis details
        medicine_suggestions: Medicine recommendations
        patient_info: Patient information
        
    Returns:
        Report data dictionary
    """
    return dashboard_report_display.generate_prediction_report(
        predictions,
        analysis_details,
        medicine_suggestions,
        patient_info
    )
