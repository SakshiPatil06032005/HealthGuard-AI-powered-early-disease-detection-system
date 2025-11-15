"""
Enhanced Model Training Script for X-ray and MRI Disease Detection
- Supports multiple datasets (NIH, Kaggle Chest X-ray, COVID-19)
- Advanced data augmentation and preprocessing
- Improved architecture using EfficientNetB3/B4
- Better accuracy through transfer learning and fine-tuning
- Proper validation and error handling

Author: AI-Enhanced Medical Imaging System
Date: 2025-11-13
"""

import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks
from tensorflow.keras.applications import EfficientNetB3, EfficientNetB4
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
import logging
from pathlib import Path
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    """Training configuration"""
    # Model settings
    IMAGE_SIZE = (256, 256)  # Increased from 224x224 for better accuracy
    BATCH_SIZE = 32  # Reduced for stability
    EPOCHS_WARMUP = 10
    EPOCHS_FINETUNE = 30
    LEARNING_RATE_WARMUP = 1e-3
    LEARNING_RATE_FINETUNE = 1e-5
    
    # Model architecture
    USE_EFFICIENTNET_B4 = True  # Set to False to use B3
    DROPOUT_RATE = 0.4
    DENSE_UNITS = 512
    
    # Paths
    BASE_DIR = Path("app/model_train")
    MODEL_SAVE_PATH = Path("app/models/enhanced_chest_xray_model.keras")
    LABEL_MAP_PATH = Path("app/models/label_map.json")
    TRAINING_HISTORY_PATH = Path("app/models/training_history.json")
    
    # Dataset paths (adjust based on your setup)
    NIH_CSV = BASE_DIR / "Data_Entry_2017.csv"
    NIH_IMG_DIR = BASE_DIR / "NIH_CHEST_XRAY"
    KAGGLE_PNEUMONIA_DIR = BASE_DIR / "chest_xray"  # Kaggle pneumonia dataset
    COVID_DIR = BASE_DIR / "COVID-19_Radiography_Dataset"  # COVID-19 dataset
    
    # Disease labels
    NIH_LABELS = [
        "Atelectasis", "Cardiomegaly", "Consolidation", "Edema", "Effusion",
        "Emphysema", "Fibrosis", "Hernia", "Infiltration", "Mass",
        "Nodule", "Pleural_Thickening", "Pneumonia", "Pneumothorax"
    ]
    
    # Data augmentation
    USE_AUGMENTATION = True
    AUGMENTATION_STRENGTH = 'medium'  # 'low', 'medium', 'high'


class DatasetLoader:
    """Load and preprocess datasets from multiple sources"""
    
    def __init__(self, config: Config):
        self.config = config
        self.all_image_paths = []
        self.all_labels = []
        self.label_map = {}
        
    def load_nih_dataset(self, max_samples=50000):
        """Load NIH Chest X-ray dataset"""
        logger.info("Loading NIH Chest X-ray dataset...")
        
        if not self.config.NIH_CSV.exists():
            logger.warning(f"NIH CSV not found at {self.config.NIH_CSV}")
            return 0
        
        try:
            df = pd.read_csv(self.config.NIH_CSV)
            if max_samples:
                df = df.iloc[:max_samples]
            
            # Process labels
            df["Image Path"] = df["Image Index"].apply(
                lambda x: str(self.config.NIH_IMG_DIR / x)
            )
            
            # Filter existing images
            df = df[df["Image Path"].apply(os.path.exists)]
            
            # Create label vectors
            for label in self.config.NIH_LABELS:
                if label not in self.label_map:
                    self.label_map[label] = len(self.label_map)
            
            # Convert labels to multi-hot encoding
            for idx, row in df.iterrows():
                img_path = row["Image Path"]
                finding_labels = row["Finding Labels"].split("|")
                
                # Create label vector
                label_vector = np.zeros(len(self.label_map), dtype=np.float32)
                for label in finding_labels:
                    if label in self.label_map:
                        label_vector[self.label_map[label]] = 1.0
                
                self.all_image_paths.append(img_path)
                self.all_labels.append(label_vector)
            
            count = len(df)
            logger.info(f"✅ Loaded {count} images from NIH dataset")
            return count
            
        except Exception as e:
            logger.error(f"Error loading NIH dataset: {e}")
            return 0
    
    def load_kaggle_pneumonia_dataset(self):
        """Load Kaggle Chest X-ray Pneumonia dataset"""
        logger.info("Loading Kaggle Pneumonia dataset...")
        
        if not self.config.KAGGLE_PNEUMONIA_DIR.exists():
            logger.warning(f"Kaggle dataset not found at {self.config.KAGGLE_PNEUMONIA_DIR}")
            return 0
        
        try:
            count = 0
            pneumonia_idx = self.label_map.get("Pneumonia", len(self.label_map))
            if "Pneumonia" not in self.label_map:
                self.label_map["Pneumonia"] = pneumonia_idx
            
            # Load train and val folders
            for split in ["train", "val", "test"]:
                split_dir = self.config.KAGGLE_PNEUMONIA_DIR / split
                if not split_dir.exists():
                    continue
                
                # Normal and Pneumonia folders
                for class_name in ["NORMAL", "PNEUMONIA"]:
                    class_dir = split_dir / class_name
                    if not class_dir.exists():
                        continue
                    
                    for img_file in class_dir.glob("*.jpeg"):
                        label_vector = np.zeros(len(self.label_map), dtype=np.float32)
                        
                        if class_name == "PNEUMONIA":
                            label_vector[pneumonia_idx] = 1.0
                        
                        self.all_image_paths.append(str(img_file))
                        self.all_labels.append(label_vector)
                        count += 1
            
            logger.info(f"✅ Loaded {count} images from Kaggle Pneumonia dataset")
            return count
            
        except Exception as e:
            logger.error(f"Error loading Kaggle dataset: {e}")
            return 0
    
    def load_covid_dataset(self):
        """Load COVID-19 Radiography dataset"""
        logger.info("Loading COVID-19 dataset...")
        
        if not self.config.COVID_DIR.exists():
            logger.warning(f"COVID dataset not found at {self.config.COVID_DIR}")
            return 0
        
        try:
            count = 0
            covid_idx = self.label_map.get("COVID-19", len(self.label_map))
            pneumonia_idx = self.label_map.get("Pneumonia", len(self.label_map))
            
            if "COVID-19" not in self.label_map:
                self.label_map["COVID-19"] = covid_idx
            if "Pneumonia" not in self.label_map:
                self.label_map["Pneumonia"] = pneumonia_idx
            
            # Load COVID, Viral Pneumonia, and Normal images
            for class_name in ["COVID", "Viral Pneumonia", "Normal"]:
                class_dir = self.config.COVID_DIR / class_name / "images"
                if not class_dir.exists():
                    class_dir = self.config.COVID_DIR / class_name
                    if not class_dir.exists():
                        continue
                
                for img_file in class_dir.glob("*.png"):
                    label_vector = np.zeros(len(self.label_map), dtype=np.float32)
                    
                    if class_name == "COVID":
                        label_vector[covid_idx] = 1.0
                    elif class_name == "Viral Pneumonia":
                        label_vector[pneumonia_idx] = 1.0
                    
                    self.all_image_paths.append(str(img_file))
                    self.all_labels.append(label_vector)
                    count += 1
            
            logger.info(f"✅ Loaded {count} images from COVID-19 dataset")
            return count
            
        except Exception as e:
            logger.error(f"Error loading COVID dataset: {e}")
            return 0
    
    def load_all_datasets(self):
        """Load all available datasets"""
        logger.info("=" * 60)
        logger.info("LOADING DATASETS")
        logger.info("=" * 60)
        
        nih_count = self.load_nih_dataset()
        kaggle_count = self.load_kaggle_pneumonia_dataset()
        covid_count = self.load_covid_dataset()
        
        total = nih_count + kaggle_count + covid_count
        
        logger.info("=" * 60)
        logger.info(f"TOTAL IMAGES LOADED: {total}")
        logger.info(f"TOTAL CLASSES: {len(self.label_map)}")
        logger.info(f"Label Map: {self.label_map}")
        logger.info("=" * 60)
        
        return self.all_image_paths, self.all_labels, self.label_map


class DataGenerator(tf.keras.utils.Sequence):
    """Custom data generator with augmentation"""
    
    def __init__(self, image_paths, labels, config, augment=True, shuffle=True):
        self.image_paths = image_paths
        self.labels = labels
        self.config = config
        self.augment = augment and config.USE_AUGMENTATION
        self.shuffle = shuffle
        self.indexes = np.arange(len(self.image_paths))
        self.on_epoch_end()
        
        # Setup augmentation based on strength
        if config.AUGMENTATION_STRENGTH == 'low':
            self.aug_params = {
                'rotation_range': 5,
                'width_shift_range': 0.05,
                'height_shift_range': 0.05,
                'zoom_range': 0.05,
                'horizontal_flip': True
            }
        elif config.AUGMENTATION_STRENGTH == 'medium':
            self.aug_params = {
                'rotation_range': 10,
                'width_shift_range': 0.1,
                'height_shift_range': 0.1,
                'zoom_range': 0.1,
                'horizontal_flip': True,
                'brightness_range': [0.9, 1.1]
            }
        else:  # high
            self.aug_params = {
                'rotation_range': 15,
                'width_shift_range': 0.15,
                'height_shift_range': 0.15,
                'zoom_range': 0.15,
                'horizontal_flip': True,
                'brightness_range': [0.8, 1.2],
                'shear_range': 5
            }
        
        self.augmentor = ImageDataGenerator(**self.aug_params)
    
    def __len__(self):
        return int(np.ceil(len(self.image_paths) / self.config.BATCH_SIZE))
    
    def __getitem__(self, index):
        indexes = self.indexes[index * self.config.BATCH_SIZE:(index + 1) * self.config.BATCH_SIZE]
        
        batch_paths = [self.image_paths[i] for i in indexes]
        batch_labels = [self.labels[i] for i in indexes]
        
        X, y = self.__data_generation(batch_paths, batch_labels)
        return X, y
    
    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.indexes)
    
    def __data_generation(self, batch_paths, batch_labels):
        """Generate batch of data"""
        X = np.zeros((len(batch_paths), *self.config.IMAGE_SIZE, 3), dtype=np.float32)
        y = np.array(batch_labels, dtype=np.float32)
        
        for i, img_path in enumerate(batch_paths):
            try:
                # Load image
                img = tf.keras.preprocessing.image.load_img(
                    img_path, 
                    target_size=self.config.IMAGE_SIZE,
                    color_mode='rgb'
                )
                img_array = tf.keras.preprocessing.image.img_to_array(img)
                
                # Apply augmentation
                if self.augment:
                    img_array = self.augmentor.random_transform(img_array)
                
                # Preprocess for EfficientNet
                img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)
                
                X[i] = img_array
                
            except Exception as e:
                logger.warning(f"Error loading image {img_path}: {e}")
                # Use zero array as fallback
                X[i] = np.zeros((*self.config.IMAGE_SIZE, 3), dtype=np.float32)
        
        return X, y


class EnhancedModelTrainer:
    """Train enhanced disease detection model"""
    
    def __init__(self, config: Config):
        self.config = config
        self.model = None
        self.history = None
        
    def build_model(self, num_classes):
        """Build enhanced model architecture"""
        logger.info("Building enhanced model architecture...")
        
        # Choose base model
        if self.config.USE_EFFICIENTNET_B4:
            base_model = EfficientNetB4(
                include_top=False,
                weights='imagenet',
                input_shape=(*self.config.IMAGE_SIZE, 3)
            )
            logger.info("Using EfficientNetB4 architecture")
        else:
            base_model = EfficientNetB3(
                include_top=False,
                weights='imagenet',
                input_shape=(*self.config.IMAGE_SIZE, 3)
            )
            logger.info("Using EfficientNetB3 architecture")
        
        # Freeze base model initially
        base_model.trainable = False
        
        # Build model
        inputs = layers.Input(shape=(*self.config.IMAGE_SIZE, 3))
        x = base_model(inputs, training=False)
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dense(self.config.DENSE_UNITS, activation='relu')(x)
        x = layers.Dropout(self.config.DROPOUT_RATE)(x)
        x = layers.Dense(self.config.DENSE_UNITS // 2, activation='relu')(x)
        x = layers.Dropout(self.config.DROPOUT_RATE / 2)(x)
        outputs = layers.Dense(num_classes, activation='sigmoid')(x)
        
        self.model = models.Model(inputs=inputs, outputs=outputs)
        
        logger.info(f"✅ Model built with {num_classes} output classes")
        logger.info(f"Total parameters: {self.model.count_params():,}")
        
        return self.model
    
    def compile_model(self, learning_rate):
        """Compile model with optimizer and loss"""
        self.model.compile(
            optimizer=tf.keras.optimizers.AdamW(learning_rate=learning_rate),
            loss='binary_crossentropy',
            metrics=[
                'accuracy',
                tf.keras.metrics.AUC(name='auc'),
                tf.keras.metrics.Precision(name='precision'),
                tf.keras.metrics.Recall(name='recall')
            ]
        )
        logger.info(f"✅ Model compiled with learning rate: {learning_rate}")
    
    def get_callbacks(self, stage='warmup'):
        """Get training callbacks"""
        callback_list = [
            callbacks.EarlyStopping(
                monitor='val_auc',
                patience=5,
                restore_best_weights=True,
                mode='max',
                verbose=1
            ),
            callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=3,
                min_lr=1e-7,
                verbose=1
            ),
            callbacks.ModelCheckpoint(
                filepath=str(self.config.MODEL_SAVE_PATH).replace('.keras', f'_{stage}_best.keras'),
                monitor='val_auc',
                save_best_only=True,
                mode='max',
                verbose=1
            )
        ]
        
        return callback_list
    
    def train(self, train_generator, val_generator, stage='warmup'):
        """Train model"""
        if stage == 'warmup':
            epochs = self.config.EPOCHS_WARMUP
            logger.info(f"Starting WARMUP training for {epochs} epochs...")
        else:
            epochs = self.config.EPOCHS_FINETUNE
            logger.info(f"Starting FINE-TUNING for {epochs} epochs...")
        
        history = self.model.fit(
            train_generator,
            validation_data=val_generator,
            epochs=epochs,
            callbacks=self.get_callbacks(stage),
            verbose=1
        )
        
        self.history = history.history
        logger.info(f"✅ {stage.upper()} training completed")
        
        return history
    
    def unfreeze_model(self, layers_to_unfreeze=-30):
        """Unfreeze layers for fine-tuning"""
        logger.info(f"Unfreezing last {abs(layers_to_unfreeze)} layers for fine-tuning...")
        
        # Unfreeze the base model layers
        for layer in self.model.layers[0].layers[layers_to_unfreeze:]:
            layer.trainable = True
        
        trainable_count = sum([1 for layer in self.model.layers if layer.trainable])
        logger.info(f"✅ Trainable layers: {trainable_count}")
    
    def save_model(self, label_map):
        """Save final model and metadata"""
        # Create models directory
        self.config.MODEL_SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Save model
        self.model.save(self.config.MODEL_SAVE_PATH)
        logger.info(f"✅ Model saved to {self.config.MODEL_SAVE_PATH}")
        
        # Save label map
        with open(self.config.LABEL_MAP_PATH, 'w') as f:
            json.dump(label_map, f, indent=2)
        logger.info(f"✅ Label map saved to {self.config.LABEL_MAP_PATH}")
        
        # Save training history
        if self.history:
            with open(self.config.TRAINING_HISTORY_PATH, 'w') as f:
                json.dump(self.history, f, indent=2)
            logger.info(f"✅ Training history saved to {self.config.TRAINING_HISTORY_PATH}")


def main():
    """Main training pipeline"""
    logger.info("=" * 60)
    logger.info("ENHANCED MODEL TRAINING PIPELINE")
    logger.info("=" * 60)
    
    # Initialize config
    config = Config()
    
    # Load datasets
    dataset_loader = DatasetLoader(config)
    image_paths, labels, label_map = dataset_loader.load_all_datasets()
    
    if len(image_paths) == 0:
        logger.error("❌ No images loaded! Please check dataset paths.")
        return
    
    # Split data
    logger.info("Splitting data into train/validation sets...")
    train_paths, val_paths, train_labels, val_labels = train_test_split(
        image_paths, labels,
        test_size=0.15,
        random_state=42,
        shuffle=True
    )
    
    logger.info(f"Training samples: {len(train_paths)}")
    logger.info(f"Validation samples: {len(val_paths)}")
    
    # Create data generators
    train_generator = DataGenerator(train_paths, train_labels, config, augment=True)
    val_generator = DataGenerator(val_paths, val_labels, config, augment=False, shuffle=False)
    
    # Build and train model
    trainer = EnhancedModelTrainer(config)
    trainer.build_model(num_classes=len(label_map))
    
    # Stage 1: Warmup training with frozen base
    trainer.compile_model(learning_rate=config.LEARNING_RATE_WARMUP)
    trainer.train(train_generator, val_generator, stage='warmup')
    
    # Stage 2: Fine-tuning with unfrozen layers
    trainer.unfreeze_model(layers_to_unfreeze=-30)
    trainer.compile_model(learning_rate=config.LEARNING_RATE_FINETUNE)
    trainer.train(train_generator, val_generator, stage='finetune')
    
    # Save final model
    trainer.save_model(label_map)
    
    logger.info("=" * 60)
    logger.info("✅ TRAINING COMPLETED SUCCESSFULLY!")
    logger.info("=" * 60)
    logger.info(f"Model saved at: {config.MODEL_SAVE_PATH}")
    logger.info(f"Label map saved at: {config.LABEL_MAP_PATH}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
