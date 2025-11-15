"""
Generate a simple test image for the X-ray prediction demo.
"""
import numpy as np
from PIL import Image
import os

def create_test_image():
    # Create a 224x224 grayscale image (size expected by the model)
    size = (224, 224)
    # Create a gradient pattern that looks vaguely like a chest X-ray
    x = np.linspace(0, 1, size[0])
    y = np.linspace(0, 1, size[1])
    xx, yy = np.meshgrid(x, y)
    # Create circular patterns
    center1 = (0.3, 0.5)
    center2 = (0.7, 0.5)
    radius = 0.2
    circle1 = (xx - center1[0])**2 + (yy - center1[1])**2 < radius**2
    circle2 = (xx - center2[0])**2 + (yy - center2[1])**2 < radius**2
    
    # Combine patterns
    image = np.zeros(size)
    image += 0.7 * (1 - xx)  # Gradient
    image += 0.3 * (circle1 | circle2)  # Add circles
    
    # Normalize to 0-255 range
    image = (image * 255).astype(np.uint8)
    
    # Create PIL Image
    img = Image.fromarray(image, mode='L')
    
    # Ensure demo_images directory exists
    os.makedirs('demo_images', exist_ok=True)
    
    # Save as PNG
    output_path = os.path.join('demo_images', 'test_xray.png')
    img.save(output_path)
    print(f"Created test image: {output_path}")
    return output_path

if __name__ == '__main__':
    create_test_image()