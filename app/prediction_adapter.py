"""
Integration adapter for comprehensive image prediction
Maintains backward compatibility while using enhanced predictor
"""

from app.comprehensive_image_predictor import ComprehensiveImagePredictor
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class PredictionIntegrationAdapter:
    """
    Adapter to integrate comprehensive predictor with existing API
    Maintains backward compatibility while providing enhanced features
    """
    
    def __init__(self):
        """Initialize the adapter with comprehensive predictor"""
        self.comprehensive_predictor = ComprehensiveImagePredictor()
        logger.info(f"✅ Comprehensive predictor initialized with {self.comprehensive_predictor.disease_count} diseases")
    
    def predict(self, image_bytes: bytes, model_type: str = 'comprehensive') -> Dict:
        """
        Make disease prediction
        
        Args:
            image_bytes: Raw image data
            model_type: Type of model to use ('comprehensive', 'ensemble', etc.)
            
        Returns:
            Prediction results
        """
        try:
            result = self.comprehensive_predictor.predict_diseases(image_bytes, top_k=5)
            
            # Format for API compatibility
            if result.get('success'):
                diseases = result.get('diseases_detected', [])
                
                return {
                    'success': True,
                    'predictions': diseases,
                    'total_predictions': len(diseases),
                    'overall_confidence': result.get('overall_confidence', 0),
                    'recommendations': result.get('recommendations', {}),
                    'method': result.get('analysis_method', 'Ensemble'),
                    'supported_diseases': self.comprehensive_predictor.disease_count,
                    'disease_categories': self._get_category_summary(diseases)
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Prediction failed'),
                    'predictions': []
                }
                
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                'success': False,
                'error': str(e),
                'predictions': []
            }
    
    def _get_category_summary(self, predictions: List[Dict]) -> Dict[str, int]:
        """Get summary of predictions by category"""
        summary = {}
        for pred in predictions:
            category = pred.get('category', 'Other')
            summary[category] = summary.get(category, 0) + 1
        return summary
    
    def get_supported_diseases(self) -> Dict:
        """Get list of all supported diseases"""
        diseases = self.comprehensive_predictor.list_supported_diseases()
        
        # Group by category
        categorized = {}
        for disease in diseases:
            info = self.comprehensive_predictor.get_disease_info(disease)
            if info:
                category = info.category
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append({
                    'name': disease,
                    'severity': info.severity,
                    'treatment': info.treatment
                })
        
        return {
            'total_diseases': len(diseases),
            'by_category': categorized,
            'all_diseases': sorted(diseases)
        }
    
    def get_disease_details(self, disease_name: str) -> Optional[Dict]:
        """Get detailed information about a disease"""
        info = self.comprehensive_predictor.get_disease_info(disease_name)
        
        if info:
            return {
                'name': info.name,
                'category': info.category,
                'severity': info.severity,
                'treatment': info.treatment,
                'description': info.description,
                'confidence_range': info.confidence_range
            }
        return None
    
    def analyze_batch(self, image_bytes_list: List[bytes]) -> List[Dict]:
        """Analyze multiple images"""
        results = []
        for image_bytes in image_bytes_list:
            result = self.predict(image_bytes)
            results.append(result)
        return results


# Global instance for API use
prediction_adapter = PredictionIntegrationAdapter()


def predict_disease(image_bytes: bytes) -> Dict:
    """Predict disease from X-ray/MRI image"""
    return prediction_adapter.predict(image_bytes)


def get_disease_list() -> Dict:
    """Get all supported diseases"""
    return prediction_adapter.get_supported_diseases()


def get_disease_info(disease_name: str) -> Optional[Dict]:
    """Get information about specific disease"""
    return prediction_adapter.get_disease_details(disease_name)


if __name__ == "__main__":
    # Test
    adapter = PredictionIntegrationAdapter()
    
    print("=" * 50)
    print("COMPREHENSIVE DISEASE PREDICTION SYSTEM")
    print("=" * 50)
    print(f"\n✅ System initialized successfully")
    print(f"📊 Total diseases supported: {adapter.comprehensive_predictor.disease_count}")
    
    # Show diseases by category
    diseases = adapter.get_supported_diseases()
    print(f"\n📋 Diseases by Category:")
    for category, disease_list in diseases['by_category'].items():
        print(f"\n  {category} ({len(disease_list)} diseases):")
        for disease in disease_list:
            print(f"    - {disease['name']} [{disease['severity']}]")
    
    print("\n✨ System ready for predictions!")
