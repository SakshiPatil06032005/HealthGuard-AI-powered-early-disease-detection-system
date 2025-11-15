import google.generativeai as genai
import base64
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class GPT:
    def __init__(self):
        # Get API key from Flask config
        try:
            api_key = current_app.config.get('GEMINI_API_KEY', '')
            if not api_key:
                logger.warning("GEMINI_API_KEY not found in config")
                self.api_key = None
                self.model = None
                return
                
            genai.configure(api_key=api_key)
            # Use gemini-2.0-flash - latest and most capable model
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.api_key = api_key
            logger.info("Gemini API initialized successfully with gemini-2.0-flash")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.api_key = None
            self.model = None
        
    def create_prompt(self, label):
        """Create a medical report based on the prediction label using Gemini."""
        if not self.model or not self.api_key:
            logger.warning(f"Gemini model not available. Prediction: {label}")
            return f"X-ray Analysis Result: {label}\n\nNote: AI report generation is currently disabled. Please configure your Gemini API key to enable this feature."
        
        try:
            prompt = f"""You are a medical AI Diagnostic expert and a radiologist.
            
My X-ray model predicted: {label}.

Please explain what this means in a single paragraph. If it predicted nothing or "No Disease Detected", 
then just state that there is no disease detected and the patient appears healthy based on the X-ray analysis.

Keep the explanation clear, concise, and suitable for a medical report."""
            
            response = self.model.generate_content(prompt)
            logger.info(f"Generated report for prediction: {label}")
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating medical report: {e}")
            return f"X-ray Analysis Result: {label}\n\nNote: Could not generate detailed AI report. Error: {str(e)}"
    
    def _encode_image(self, image):
        """Encode image to base64 for API calls."""
        with open(image, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
