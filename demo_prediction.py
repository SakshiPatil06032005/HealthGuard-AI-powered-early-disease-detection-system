"""
Enhanced X-ray prediction demo script with better error handling and image preview.
"""
import sys
import os
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import requests
from pathlib import Path

# Add parent directory to path so we can import from app/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def download_sample_images():
    """Download some sample chest X-rays for testing."""
    demo_dir = Path("demo_images")
    demo_dir.mkdir(exist_ok=True)
    
    # Sample X-ray URLs (these are example NIH chest X-rays)
    sample_images = {
        "normal.png": "https://raw.githubusercontent.com/mlmed/torchxrayvision/master/tests/sample_images/2_norm.png",
        "pneumonia.png": "https://raw.githubusercontent.com/mlmed/torchxrayvision/master/tests/sample_images/2_pne.png"
    }
    
    downloaded = []
    for filename, url in sample_images.items():
        filepath = demo_dir / filename
        if not filepath.exists():
            try:
                print(f"Downloading {filename}...")
                response = requests.get(url)
                response.raise_for_status()
                filepath.write_bytes(response.content)
                downloaded.append(filepath)
            except Exception as e:
                print(f"Error downloading {filename}: {e}")
        else:
            downloaded.append(filepath)
    
    return downloaded

def verify_model():
    """Check if the model file exists and is valid."""
    model_path = "app/models/chest_xray_model.keras"
    if not os.path.exists(model_path):
        print(f"\n⚠️ Model file not found at {model_path}")
        print("Please ensure:")
        print("1. You have downloaded the trained model")
        print("2. The model file is placed in app/models/")
        print("3. The file is named 'chest_xray_model.keras'")
        return False
    
    print("\nℹ️ Model file found, checking format...")
    
    # Try to load the model to verify it's valid
    try:
        model = tf.keras.models.load_model(model_path)
        print("✓ Model verified successfully")
        return True
    except Exception as e:
        print(f"\n⚠️ Error loading model: {str(e)}")
        print("\nPlease ensure:")
        print("1. The model file is not corrupted")
        print("2. You have TensorFlow installed (pip install tensorflow)")
        print("3. The model is compatible with your TensorFlow version")
        return False

def preview_image(image_path):
    """Show basic image info and verify it can be loaded."""
    try:
        with Image.open(image_path) as img:
            print(f"\nImage Preview:")
            print(f"Format: {img.format}")
            print(f"Size: {img.size}")
            print(f"Mode: {img.mode}")
            return True
    except Exception as e:
        print(f"Error loading image: {e}")
        return False

def run_prediction(image_path):
    """Run the full prediction pipeline with error checking."""
    from app.api import XRayPredictor
    from app.generate_heatmap import XRayHeatmapGenerator
    from app.chat import GPT
    
    try:
        # 1. Verify image
        if not preview_image(image_path):
            return False
            
        # 2. Load model and predict
        print("\nRunning prediction...")
        predictor = XRayPredictor()
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        result = predictor.predict(image_bytes)
        if "error" in result:
            print(f"Prediction error: {result['error']}")
            return False
            
        predictions = result["prediction"]
        print(f"\nPredicted conditions: {', '.join(predictions)}")
        
        # 3. Generate heatmap
        print("\nGenerating visualization...")
        heatmap_gen = XRayHeatmapGenerator()
        heatmap = heatmap_gen.generate_heatmap(image_bytes)
        if heatmap is not None:
            output_path = heatmap_gen.overlay_heatmap(heatmap, image_bytes)
            print(f"✓ Heatmap saved to: {output_path}")
        
        # 4. Get LLM explanation if API key set
        if os.getenv("API_TOKEN"):
            print("\nGenerating medical explanation...")
            gpt = GPT()
            explanation = gpt.create_prompt(predictions[0])
            print(f"\nMedical interpretation:\n{explanation}")
        else:
            print("\nNote: Set API_TOKEN environment variable to enable medical explanations")
        
        return True
        
    except Exception as e:
        print(f"\nError in prediction pipeline: {str(e)}")
        return False

def main():
    """Main demo function."""
    print("AI-Powered Disease Prediction Demo")
    print("=================================")
    
    # 1. First verify the model exists and is valid
    if not verify_model():
        return False
    
    # 2. Download sample images if none provided
    if len(sys.argv) < 2:
        print("\nNo image provided, downloading samples...")
        image_paths = download_sample_images()
        if not image_paths:
            print("Error: Could not download sample images")
            return False
    else:
        image_paths = [sys.argv[1]]
    
    # 3. Run prediction for each image
    success = True
    for image_path in image_paths:
        print(f"\nProcessing: {image_path}")
        if not run_prediction(image_path):
            success = False
            
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)