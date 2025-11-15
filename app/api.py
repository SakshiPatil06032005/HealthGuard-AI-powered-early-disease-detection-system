try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

from PIL import Image
from io import BytesIO
import numpy as np
import cv2

IMG_SIZE = (224, 224)

MODEL_PATH = "app/models/chest_xray_model.keras"

class XRayPredictor:
    def __init__(self):
        self.model = None
        if not TF_AVAILABLE:
            print("TensorFlow not available - using fallback pneumonia detection")
            return
        try:
            self.model = tf.keras.models.load_model(MODEL_PATH)
            print("✅ TensorFlow model loaded successfully")
        except Exception as e:
            print(f"Warning: Could not load TensorFlow model: {e}")
            print("Using fallback pneumonia detection via image analysis")
            self.model = None

    def predict(self, image_bytes):
        if self.model is not None:
            # Use TensorFlow model
            return self._predict_with_model(image_bytes)
        else:
            # Use fallback pattern detection
            return self._predict_with_pattern_analysis(image_bytes)
    
    def _predict_with_model(self, image_bytes):
        """Prediction using TensorFlow model"""
        transformed_image = self._transform_image(image_bytes)
        if transformed_image is None:
            return {"error": "Error processing image"}

        predictions = self.model.predict(transformed_image)[0]
        all_labels = [
            "Atelectasis", "Cardiomegaly", "Consolidation", "Edema", "Effusion",
            "Emphysema", "Fibrosis", "Hernia", "Infiltration", "Mass",
            "Nodule", "Pleural_Thickening", "Pneumonia", "Pneumothorax"
        ]
        predicted_labels = [all_labels[i] for i in np.where(predictions > 0.5)[0]]

        return {
            "prediction": predicted_labels if predicted_labels else ["No Disease Detected"],
            "confidence": float(np.max(predictions))
        }
    
    def _predict_with_pattern_analysis(self, image_bytes):
        """Fallback: Use image pattern analysis to detect pneumonia-like patterns"""
        try:
            # Load and convert image to grayscale
            img = Image.open(BytesIO(image_bytes)).convert("L")
            img_array = np.array(img, dtype=np.uint8)
            
            # Analyze the image for pneumonia-like patterns
            # Pneumonia typically shows as white/bright areas (consolidation)
            brightness = np.mean(img_array)
            contrast = np.std(img_array)
            
            # Calculate histogram to detect bright regions (consolidation areas)
            hist = cv2.calcHist([img_array], [0], None, [256], [0, 256])
            bright_pixels = np.sum(hist[200:])  # Count very bright pixels
            total_pixels = np.sum(hist)
            bright_ratio = bright_pixels / total_pixels if total_pixels > 0 else 0
            
            # Detect edges and texture (pneumonia has distinct patterns)
            edges = cv2.Canny(img_array, 100, 200)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Simple heuristic for pneumonia detection
            # Pneumonia shows: increased brightness, high edge density, and white consolidations
            pneumonia_score = 0
            
            if brightness > 120:  # Brighter than normal lung tissue
                pneumonia_score += 0.3
            if contrast > 30:  # Good contrast indicating patterns
                pneumonia_score += 0.3
            if edge_density > 0.1:  # Significant edges indicating consolidation
                pneumonia_score += 0.2
            if bright_ratio > 0.1:  # Significant bright areas
                pneumonia_score += 0.2
            
            # Detect connected components (consolidation areas)
            _, binary = cv2.threshold(img_array, 150, 255, cv2.THRESH_BINARY)
            num_labels, _ = cv2.connectedComponents(binary)
            
            if num_labels > 50:  # Many connected white regions suggest consolidation
                pneumonia_score += 0.3
            
            # Make prediction
            predictions = []
            confidence = 0
            
            if pneumonia_score > 0.6:
                predictions = ["Pneumonia"]
                confidence = min(0.95, pneumonia_score)
            elif pneumonia_score > 0.4:
                predictions = ["Consolidation"]
                confidence = min(0.85, pneumonia_score)
            else:
                predictions = ["No Disease Detected"]
                confidence = 1.0 - pneumonia_score
            
            return {
                "prediction": predictions,
                "confidence": confidence,
                "method": "pattern_analysis"
            }
            
        except Exception as e:
            print(f"Error in pattern analysis: {e}")
            return {"prediction": ["Unable to analyze"], "error": str(e)}

    def _transform_image(self, image_bytes):
        try:
            img = Image.open(BytesIO(image_bytes)).convert("RGB")  # Convert to RGB
            img = img.resize(IMG_SIZE)  # Resize to match model input
            img_array = np.array(img, dtype=np.float32)
            if TF_AVAILABLE:
                img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)  # Normalize
            img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
            return img_array
        except Exception as e:
            print(f"Error processing image: {e}")
            return None

if __name__ == "__main__":
    predictor = XRayPredictor()
    image_bytes = open("model_train/NIH_CHEST_XRAY/00000001_002.png", "rb").read()
    result = predictor.predict(image_bytes)
    print("Prediction:", result)
