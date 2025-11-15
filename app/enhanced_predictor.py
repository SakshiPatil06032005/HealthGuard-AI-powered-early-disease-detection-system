"""
Enhanced Predictor for X-ray and MRI Disease Detection
- Loads improved trained model
- Better predictions with confidence scores
- Multi-label disease detection
- Seamless integration with existing dashboard
- Improved preprocessing and error handling

Author: AI-Enhanced Medical Imaging System
Date: 2025-11-13
"""

import os
import numpy as np
import tensorflow as tf
from PIL import Image
from io import BytesIO
from pathlib import Path
import json
import logging
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check TensorFlow availability
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    logger.warning("TensorFlow not available - using fallback mode")


class EnhancedXRayPredictor:
    """Enhanced predictor for X-ray and MRI disease detection"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize enhanced predictor
        
        Args:
            model_path: Path to trained model (optional)
        """
        self.model = None
        self.label_map = None
        self.reverse_label_map = None
        self.image_size = (256, 256)  # Match training size
        self.confidence_threshold = 0.5
        
        # Default paths
        if model_path is None:
            # Try enhanced model first, fallback to original
            enhanced_model_path = Path("app/models/enhanced_chest_xray_model.keras")
            original_model_path = Path("app/models/chest_xray_model.keras")
            
            if enhanced_model_path.exists():
                model_path = str(enhanced_model_path)
                logger.info("Using enhanced model")
            elif original_model_path.exists():
                model_path = str(original_model_path)
                logger.info("Using original model")
            else:
                logger.warning("No model found - using fallback mode")
                model_path = None
        
        self.model_path = model_path
        self.label_map_path = Path("app/models/label_map.json")
        
        # Initialize
        if TF_AVAILABLE and self.model_path:
            self._load_model()
            self._load_label_map()
        else:
            self._init_fallback_labels()
    
    def _load_model(self):
        """Load trained model"""
        try:
            self.model = tf.keras.models.load_model(self.model_path)
            logger.info(f"✅ Model loaded successfully from {self.model_path}")
            
            # Get image size from model input shape
            input_shape = self.model.input_shape
            if input_shape and len(input_shape) >= 3:
                self.image_size = (input_shape[1], input_shape[2])
                logger.info(f"Model input size: {self.image_size}")
                
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            self.model = None
    
    def _load_label_map(self):
        """Load label mapping"""
        try:
            if self.label_map_path.exists():
                with open(self.label_map_path, 'r') as f:
                    self.label_map = json.load(f)
                
                # Create reverse mapping (index -> label)
                self.reverse_label_map = {v: k for k, v in self.label_map.items()}
                logger.info(f"✅ Loaded {len(self.label_map)} disease labels")
            else:
                self._init_default_labels()
                
        except Exception as e:
            logger.error(f"Error loading label map: {e}")
            self._init_default_labels()
    
    def _init_default_labels(self):
        """Initialize default NIH labels"""
        default_labels = [
            "Atelectasis", "Cardiomegaly", "Consolidation", "Edema", "Effusion",
            "Emphysema", "Fibrosis", "Hernia", "Infiltration", "Mass",
            "Nodule", "Pleural_Thickening", "Pneumonia", "Pneumothorax"
        ]
        self.label_map = {label: i for i, label in enumerate(default_labels)}
        self.reverse_label_map = {i: label for i, label in enumerate(default_labels)}
        logger.info("Using default NIH labels")
    
    def _init_fallback_labels(self):
        """Initialize fallback labels for pattern analysis"""
        self.label_map = {
            "Pneumonia": 0,
            "Consolidation": 1,
            "Pneumothorax": 2,
            "Normal": 3
        }
        self.reverse_label_map = {v: k for k, v in self.label_map.items()}
    
    def preprocess_image(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """
        Preprocess image for prediction
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Preprocessed image array or None
        """
        try:
            # Load image
            img = Image.open(BytesIO(image_bytes))
            
            # Convert to RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize to model input size
            img = img.resize(self.image_size)
            
            # Convert to array
            img_array = np.array(img, dtype=np.float32)
            
            # Preprocess for EfficientNet
            if TF_AVAILABLE:
                img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)
            else:
                # Manual normalization
                img_array = (img_array / 127.5) - 1.0
            
            # Add batch dimension
            img_array = np.expand_dims(img_array, axis=0)
            
            return img_array
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return None
    
    def predict(self, image_bytes: bytes) -> Dict:
        """
        Predict diseases from X-ray/MRI image
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Dictionary with predictions and metadata
        """
        if self.model is not None and TF_AVAILABLE:
            return self._predict_with_model(image_bytes)
        else:
            return self._predict_with_pattern_analysis(image_bytes)
    
    def _predict_with_model(self, image_bytes: bytes) -> Dict:
        """
        Prediction using trained model
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Prediction results dictionary
        """
        try:
            # Preprocess image
            img_array = self.preprocess_image(image_bytes)
            if img_array is None:
                return {"error": "Failed to preprocess image", "success": False}
            
            # Make prediction
            predictions = self.model.predict(img_array, verbose=0)[0]
            
            # Get top predictions above threshold
            detected_diseases = []
            all_predictions = []
            
            for idx, confidence in enumerate(predictions):
                disease_name = self.reverse_label_map.get(idx, f"Unknown_{idx}")
                all_predictions.append({
                    "disease": disease_name,
                    "confidence": float(confidence),
                    "percentage": float(confidence * 100)
                })
                
                if confidence > self.confidence_threshold:
                    detected_diseases.append({
                        "disease": disease_name,
                        "confidence": float(confidence),
                        "percentage": float(confidence * 100),
                        "severity": self._get_severity(disease_name, confidence)
                    })
            
            # Sort by confidence
            detected_diseases.sort(key=lambda x: x['confidence'], reverse=True)
            all_predictions.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Get primary prediction
            if detected_diseases:
                primary_disease = detected_diseases[0]['disease']
                primary_confidence = detected_diseases[0]['confidence']
            else:
                primary_disease = "No Disease Detected"
                primary_confidence = 1.0 - np.max(predictions)
            
            # Get recommendations
            recommendations = self._get_recommendations(detected_diseases)
            
            return {
                "success": True,
                "prediction": [d['disease'] for d in detected_diseases] if detected_diseases else ["No Disease Detected"],
                "primary_disease": primary_disease,
                "confidence": primary_confidence,
                "confidence_percentage": float(primary_confidence * 100),
                "detected_diseases": detected_diseases,
                "all_predictions": all_predictions[:10],  # Top 10
                "recommendations": recommendations,
                "method": "deep_learning",
                "model_type": "Enhanced EfficientNet"
            }
            
        except Exception as e:
            logger.error(f"Error in model prediction: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    def _predict_with_pattern_analysis(self, image_bytes: bytes) -> Dict:
        """
        Fallback prediction using pattern analysis
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Prediction results dictionary
        """
        try:
            import cv2
            
            # Load image
            img = Image.open(BytesIO(image_bytes)).convert("L")
            img_array = np.array(img, dtype=np.uint8)
            
            # Analyze patterns
            brightness = np.mean(img_array)
            contrast = np.std(img_array)
            
            # Edge detection
            edges = cv2.Canny(img_array, 100, 200)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Histogram analysis
            hist = cv2.calcHist([img_array], [0], None, [256], [0, 256])
            bright_pixels = np.sum(hist[200:])
            total_pixels = np.sum(hist)
            bright_ratio = bright_pixels / total_pixels if total_pixels > 0 else 0
            
            # Connected components
            _, binary = cv2.threshold(img_array, 150, 255, cv2.THRESH_BINARY)
            num_labels, _ = cv2.connectedComponents(binary)
            
            # Score different conditions
            pneumonia_score = self._score_pneumonia(brightness, contrast, edge_density, bright_ratio, num_labels)
            pneumothorax_score = self._score_pneumothorax(brightness, contrast, edge_density)
            
            # Determine prediction
            detected_diseases = []
            
            if pneumonia_score > 0.6:
                detected_diseases.append({
                    "disease": "Pneumonia",
                    "confidence": min(0.95, pneumonia_score),
                    "percentage": min(95, pneumonia_score * 100),
                    "severity": "high" if pneumonia_score > 0.8 else "moderate"
                })
            elif pneumonia_score > 0.4:
                detected_diseases.append({
                    "disease": "Consolidation",
                    "confidence": pneumonia_score,
                    "percentage": pneumonia_score * 100,
                    "severity": "moderate"
                })
            
            if pneumothorax_score > 0.5:
                detected_diseases.append({
                    "disease": "Pneumothorax",
                    "confidence": pneumothorax_score,
                    "percentage": pneumothorax_score * 100,
                    "severity": "high"
                })
            
            # Primary disease
            if detected_diseases:
                primary = max(detected_diseases, key=lambda x: x['confidence'])
                primary_disease = primary['disease']
                primary_confidence = primary['confidence']
            else:
                primary_disease = "No Disease Detected"
                primary_confidence = 0.85
                detected_diseases.append({
                    "disease": "Normal",
                    "confidence": 0.85,
                    "percentage": 85,
                    "severity": "low"
                })
            
            recommendations = self._get_recommendations(detected_diseases)
            
            return {
                "success": True,
                "prediction": [d['disease'] for d in detected_diseases],
                "primary_disease": primary_disease,
                "confidence": primary_confidence,
                "confidence_percentage": float(primary_confidence * 100),
                "detected_diseases": detected_diseases,
                "recommendations": recommendations,
                "method": "pattern_analysis",
                "model_type": "Fallback Pattern Detection"
            }
            
        except Exception as e:
            logger.error(f"Error in pattern analysis: {e}")
            return {
                "error": str(e),
                "success": False,
                "prediction": ["Unable to analyze"],
                "confidence": 0.0
            }
    
    def _score_pneumonia(self, brightness, contrast, edge_density, bright_ratio, num_labels):
        """Score likelihood of pneumonia"""
        score = 0
        
        if brightness > 120:
            score += 0.3
        if contrast > 30:
            score += 0.3
        if edge_density > 0.1:
            score += 0.2
        if bright_ratio > 0.1:
            score += 0.2
        if num_labels > 50:
            score += 0.3
        
        return min(1.0, score)
    
    def _score_pneumothorax(self, brightness, contrast, edge_density):
        """Score likelihood of pneumothorax"""
        score = 0
        
        # Pneumothorax shows as very dark areas (collapsed lung)
        if brightness < 80:
            score += 0.4
        if contrast > 40:
            score += 0.3
        if edge_density > 0.15:
            score += 0.3
        
        return min(1.0, score)
    
    def _get_severity(self, disease_name: str, confidence: float) -> str:
        """
        Determine severity level
        
        Args:
            disease_name: Disease name
            confidence: Confidence score
            
        Returns:
            Severity level string
        """
        high_severity_diseases = [
            "Pneumonia", "COVID-19", "Pneumothorax", "Tuberculosis",
            "Pulmonary Edema", "Cardiomegaly", "Mass"
        ]
        
        moderate_severity_diseases = [
            "Consolidation", "Effusion", "Infiltration", "Nodule",
            "Atelectasis", "Pleural_Thickening"
        ]
        
        if disease_name in high_severity_diseases:
            if confidence > 0.8:
                return "high"
            else:
                return "moderate"
        elif disease_name in moderate_severity_diseases:
            return "moderate"
        else:
            return "low"
    
    def _get_recommendations(self, detected_diseases: List[Dict]) -> List[str]:
        """
        Get medical recommendations based on predictions
        
        Args:
            detected_diseases: List of detected disease dictionaries
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if not detected_diseases or detected_diseases[0]['disease'] == "Normal":
            recommendations.append("✅ No significant abnormalities detected")
            recommendations.append("Continue routine health checkups")
            return recommendations
        
        # General recommendations
        recommendations.append("⚠️ Abnormalities detected - consult a physician immediately")
        
        # Disease-specific recommendations
        for disease_info in detected_diseases:
            disease = disease_info['disease']
            severity = disease_info.get('severity', 'moderate')
            
            if disease == "Pneumonia":
                recommendations.append("🏥 Urgent: Start antibiotic treatment")
                recommendations.append("💊 Supportive care with rest and hydration")
                recommendations.append("🌡️ Monitor temperature and oxygen levels")
                
            elif disease == "COVID-19":
                recommendations.append("🏥 Urgent: Isolate and seek medical attention")
                recommendations.append("💊 Antiviral medication may be required")
                recommendations.append("🫁 Monitor breathing and oxygen saturation")
                
            elif disease == "Pneumothorax":
                recommendations.append("🚨 Emergency: Immediate medical intervention needed")
                recommendations.append("🏥 May require chest tube placement")
                
            elif disease == "Tuberculosis":
                recommendations.append("🏥 Start multi-drug TB treatment (6 months)")
                recommendations.append("😷 Isolate to prevent transmission")
                recommendations.append("💊 Complete full course of medication")
                
            elif disease == "Cardiomegaly":
                recommendations.append("❤️ Cardiac evaluation required")
                recommendations.append("💊 May need cardiac medications")
                recommendations.append("🏃 Lifestyle modifications recommended")
                
            elif disease in ["Consolidation", "Infiltration"]:
                recommendations.append("🏥 Further diagnostic imaging recommended")
                recommendations.append("💊 May require antibiotic treatment")
                
            elif disease == "Nodule":
                recommendations.append("🔍 Follow-up imaging in 3-6 months")
                recommendations.append("🏥 Consider biopsy if suspicious features")
        
        # Add severity-based recommendations
        if any(d.get('severity') == 'high' for d in detected_diseases):
            recommendations.insert(1, "🚨 HIGH PRIORITY: Seek immediate medical attention")
        
        return list(dict.fromkeys(recommendations))  # Remove duplicates


# Global instance for backward compatibility
enhanced_predictor = EnhancedXRayPredictor()


def predict_xray(image_bytes: bytes) -> Dict:
    """
    Convenience function for X-ray prediction
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        Prediction results dictionary
    """
    return enhanced_predictor.predict(image_bytes)


if __name__ == "__main__":
    # Test the predictor
    print("Testing Enhanced X-Ray Predictor...")
    print(f"Model loaded: {enhanced_predictor.model is not None}")
    print(f"Labels available: {len(enhanced_predictor.label_map)}")
    print(f"Image size: {enhanced_predictor.image_size}")
