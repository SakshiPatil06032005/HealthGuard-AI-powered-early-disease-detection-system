"""
Download and prepare sample chest X-rays from public datasets.
Creates a structured test set with labeled examples.
"""
import os
import requests
import hashlib
from PIL import Image
import io

# Sample X-rays from public datasets (NIH Chest X-ray sample images)
SAMPLE_XRAYS = {
    "normal.png": {
        "url": "https://production-media.paperswithcode.com/datasets/NIH-Chest-X-ray-0000000002-6552ea87_7A8c4Sz.jpg",
        "description": "Normal chest X-ray",
        "expected": "No Disease Detected"
    },
    "pneumonia.png": {
        "url": "https://production-media.paperswithcode.com/datasets/NIH-Chest-X-ray-0000000030-25b32db6_ymQeGjZ.jpg",
        "description": "Chest X-ray showing pneumonia",
        "expected": "Pneumonia"
    }
}

def download_image(url, filepath):
    """Download an image and verify it can be opened."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Try to open the image to verify it's valid
        img = Image.open(io.BytesIO(response.content))
        
        # Convert to RGB if needed
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Resize to model input size
        img = img.resize((224, 224))
        
        # Save as PNG
        img.save(filepath, "PNG")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def setup_test_suite():
    """Download and prepare test images."""
    # Create directories
    base_dir = "test_suite"
    os.makedirs(base_dir, exist_ok=True)
    
    # Create README with image descriptions
    readme_content = "# Test X-ray Images\n\n"
    readme_content += "This folder contains sample chest X-rays for testing the prediction system.\n\n"
    
    success = False
    for filename, info in SAMPLE_XRAYS.items():
        filepath = os.path.join(base_dir, filename)
        readme_content += f"\n## {filename}\n"
        readme_content += f"- Description: {info['description']}\n"
        readme_content += f"- Expected: {info['expected']}\n"
        
        print(f"\nDownloading {filename}...")
        if download_image(info['url'], filepath):
            print(f"✓ Saved to {filepath}")
            success = True
        else:
            readme_content += "- Status: ⚠️ Download failed\n"
    
    # Save README
    readme_path = os.path.join(base_dir, "README.md")
    with open(readme_path, "w") as f:
        f.write(readme_content)
    
    if success:
        print(f"\n✓ Test suite created in {base_dir}/")
        print("✓ Sample images downloaded")
        print(f"✓ Documentation written to {readme_path}")
    else:
        print("\n⚠️ Failed to download any test images")

if __name__ == "__main__":
    setup_test_suite()