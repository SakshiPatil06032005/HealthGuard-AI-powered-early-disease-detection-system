"""
Test script to verify the X-ray prediction pipeline without using the web UI.
This helps isolate model loading and prediction issues.
"""
import sys
import os

# Add parent directory to path so we can import from app/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api import XRayPredictor
from app.generate_heatmap import XRayHeatmapGenerator
from app.chat import GPT

def test_prediction(image_path):
    """Test the full prediction pipeline on a single image."""
    print(f"\nTesting prediction pipeline with image: {image_path}")
    
    try:
        # 1. Load the model and make prediction
        print("\n1. Loading model and making prediction...")
        predictor = XRayPredictor()
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        result = predictor.predict(image_bytes)
        print(f"Prediction result: {result}")

        # 2. Generate heatmap
        print("\n2. Generating heatmap visualization...")
        heatmap_gen = XRayHeatmapGenerator()
        heatmap = heatmap_gen.generate_heatmap(image_bytes)
        if heatmap is not None:
            output_path = heatmap_gen.overlay_heatmap(heatmap, image_bytes)
            print(f"Heatmap saved to: {output_path}")
        else:
            print("Warning: Heatmap generation failed")

        # 3. Get LLM explanation (if API_TOKEN set)
        print("\n3. Getting LLM explanation...")
        try:
            gpt = GPT()
            disease = result.get('prediction', ['No disease detected'])[0]
            explanation = gpt.create_prompt(disease)
            print(f"LLM Explanation: {explanation}")
        except Exception as e:
            print(f"Warning: LLM explanation failed (API_TOKEN set?): {e}")

        print("\nPipeline test completed successfully!")
        return True

    except Exception as e:
        print(f"\nError in prediction pipeline: {e}")
        return False

if __name__ == "__main__":
    # Check if an image path was provided
    if len(sys.argv) < 2:
        print("Usage: python test_prediction.py path/to/xray/image.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    success = test_prediction(image_path)
    sys.exit(0 if success else 1)