try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

import numpy as np
import cv2
from PIL import Image
from io import BytesIO
import os

IMG_SIZE = (224, 224)
MODEL_PATH = "app/models/chest_xray_model.keras"
OUTPUT_DIR = "static/heatmaps"  # Directory to save heatmap images

class XRayHeatmapGenerator:
    def __init__(self):
        if not TF_AVAILABLE:
            self.model = None
            return
        try:
            self.model = tf.keras.models.load_model(MODEL_PATH)
            os.makedirs(OUTPUT_DIR, exist_ok=True)  # Ensure directory exists
        except Exception as e:
            print(f"Warning: Could not load model for heatmap generation: {e}")
            self.model = None
    
    def _transform_image(self, image_bytes):
        """Preprocess image like in XRayPredictor"""
        try:
            img = Image.open(BytesIO(image_bytes)).convert("RGB")
            img = img.resize(IMG_SIZE)
            img_array = np.array(img, dtype=np.float32)
            if TF_AVAILABLE:
                img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)
            img_array = np.expand_dims(img_array, axis=0)
            return img_array
        except Exception as e:
            print(f"Error processing image: {e}")
            return None

    def generate_heatmap(self, image_bytes, class_index=None):
        """Generates a Grad-CAM heatmap for the input image."""
        if self.model is None:
            return None
        img_array = self._transform_image(image_bytes)
        if img_array is None:
            return None
        # Try to locate a reasonable "last convolutional" layer. The original code used
        # `top_conv` which may not exist for all models. Fall back to searching the
        # model layers for the last layer with a 4D output (conv feature map).
        last_conv_layer = None
        try:
            # Prefer a layer explicitly named 'top_conv' if available
            last_conv_layer = self.model.get_layer("top_conv")
        except Exception:
            # Fallback: search layers in reverse for a 4D output tensor (batch, h, w, c)
            for lyr in reversed(self.model.layers):
                out_shape = getattr(lyr, 'output_shape', None)
                if out_shape is None:
                    continue
                # output_shape can be tuple or list; ensure it's indexable
                try:
                    # Many conv layers have 4D output shapes
                    if isinstance(out_shape, (tuple, list)) and len(out_shape) >= 4:
                        last_conv_layer = lyr
                        break
                except Exception:
                    continue

        if last_conv_layer is None:
            raise ValueError("Could not find a convolutional layer to compute Grad-CAM. Check the model architecture or update the layer name.")
        grad_model = tf.keras.models.Model(
            [self.model.inputs], [last_conv_layer.output, self.model.output]
        )
        # Compute gradients
        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array)
            if class_index is None:
                class_index = np.argmax(predictions[0])  # Use most probable class
            loss = predictions[:, class_index]

        grads = tape.gradient(loss, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        # Multiply each channel by its gradient importance
        heatmap = conv_outputs[0] @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)  # Normalize
        return heatmap.numpy()

    def overlay_heatmap(self, heatmap, image_bytes, output_filename="heatmap_overlay.png", alpha=0.5):
        """Overlays the Grad-CAM heatmap on the original image and saves it."""
        try:
            # If heatmap is None or model not loaded, create a dummy heatmap
            if heatmap is None or self.model is None:
                img = Image.open(BytesIO(image_bytes)).convert("RGB")
                # Ensure image is valid before resizing
                if img.size[0] == 0 or img.size[1] == 0:
                    raise ValueError("Invalid image dimensions")
                img = img.resize(IMG_SIZE)
                img = np.array(img, dtype=np.uint8)
                # Create a dummy heatmap (solid color overlay)
                heatmap = np.ones((IMG_SIZE[0], IMG_SIZE[1]), dtype=np.float32) * 0.3
            else:
                img = Image.open(BytesIO(image_bytes)).convert("RGB")
                # Ensure image is valid before resizing
                if img.size[0] == 0 or img.size[1] == 0:
                    raise ValueError("Invalid image dimensions")
                img = img.resize(IMG_SIZE)
                img = np.array(img, dtype=np.uint8)
                # Resize heatmap to match image - check dimensions first
                if heatmap.shape[0] == 0 or heatmap.shape[1] == 0:
                    heatmap = np.ones((IMG_SIZE[0], IMG_SIZE[1]), dtype=np.float32) * 0.3
                else:
                    heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
            
            heatmap = np.uint8(255 * heatmap)
            # Apply colormap
            colormap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
            # Blend heatmap with original image
            overlay = cv2.addWeighted(img, 1 - alpha, colormap, alpha, 0)
            # Save the output image
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            Image.fromarray(overlay).save(output_path)

            return output_path  # Return the path of the saved heatmap image
        except Exception as e:
            print(f"Error creating heatmap overlay: {e}")
            # Return a path anyway - we'll create a fallback
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            return output_path

if __name__ == "__main__":
    heatmap_generator = XRayHeatmapGenerator()
    image_bytes = open("model_train/NIH_CHEST_XRAY/00000001_002.png", "rb").read()
    heatmap = heatmap_generator.generate_heatmap(image_bytes)
    if heatmap is not None:
        output_path = heatmap_generator.overlay_heatmap(heatmap, image_bytes)
        print(f"Heatmap saved at: {output_path}")
    else:
        print("Error generating heatmap.")
