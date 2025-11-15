"""
Dataset Downloader Utility
Helper script to download public medical imaging datasets for training
- NIH Chest X-Ray Dataset
- Kaggle Chest X-Ray Pneumonia Dataset
- COVID-19 Radiography Dataset
- Instructions for manual download

Author: AI-Enhanced Medical Imaging System
Date: 2025-11-13
"""

import os
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatasetDownloader:
    """Download and setup medical imaging datasets"""
    
    def __init__(self):
        self.base_dir = Path("app/model_train")
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def print_instructions(self):
        """Print dataset download instructions"""
        
        instructions = """
╔══════════════════════════════════════════════════════════════════════════╗
║                    MEDICAL IMAGING DATASETS SETUP                         ║
║           Download Instructions for Enhanced Model Training               ║
╚══════════════════════════════════════════════════════════════════════════╝

📦 DATASET 1: NIH Chest X-Ray Dataset (112,120 images, 14 diseases)
═══════════════════════════════════════════════════════════════════════════
📍 Source: NIH Clinical Center
🔗 Download Link: https://nihcc.app.box.com/v/ChestXray-NIHCC

📋 Steps:
1. Visit the link above
2. Download all image files (images_001.tar.gz through images_012.tar.gz)
3. Download Data_Entry_2017.csv and BBox_List_2017.csv
4. Extract all files to: {self.base_dir}/NIH_CHEST_XRAY/
5. The final structure should be:
   {self.base_dir}/
   ├── NIH_CHEST_XRAY/
   │   ├── images/
   │   │   ├── 00000001_000.png
   │   │   ├── 00000001_001.png
   │   │   └── ... (112,120 images)
   ├── Data_Entry_2017.csv
   └── BBox_List_2017.csv

📊 Dataset Info:
   - Size: ~42 GB
   - Images: 112,120 frontal-view X-rays
   - Patients: 30,805 unique patients
   - Labels: 14 disease categories (multi-label)
   

📦 DATASET 2: Kaggle Chest X-Ray Pneumonia Dataset (5,863 images)
═══════════════════════════════════════════════════════════════════════════
📍 Source: Kaggle
🔗 Download Link: https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia

📋 Steps:
1. Install Kaggle API: pip install kaggle
2. Setup Kaggle API credentials:
   - Go to https://www.kaggle.com/account
   - Click "Create New API Token"
   - Place kaggle.json in ~/.kaggle/ (Linux/Mac) or C:\\Users\\<Username>\\.kaggle\\ (Windows)
3. Run command:
   kaggle datasets download -d paultimothymooney/chest-xray-pneumonia
4. Extract to: {self.base_dir}/chest_xray/
5. The final structure should be:
   {self.base_dir}/chest_xray/
   ├── train/
   │   ├── NORMAL/
   │   └── PNEUMONIA/
   ├── test/
   │   ├── NORMAL/
   │   └── PNEUMONIA/
   └── val/
       ├── NORMAL/
       └── PNEUMONIA/

📊 Dataset Info:
   - Size: ~1.2 GB
   - Images: 5,863 X-ray images
   - Classes: Normal, Pneumonia (bacterial and viral)
   - Split: Train (5,216), Val (16), Test (624)


📦 DATASET 3: COVID-19 Radiography Dataset (21,165 images)
═══════════════════════════════════════════════════════════════════════════
📍 Source: Kaggle / University of Dhaka
🔗 Download Link: https://www.kaggle.com/datasets/tawsifurrahman/covid19-radiography-database

📋 Steps:
1. Use Kaggle API or download manually from Kaggle
2. Command:
   kaggle datasets download -d tawsifurrahman/covid19-radiography-database
3. Extract to: {self.base_dir}/COVID-19_Radiography_Dataset/
4. The final structure should be:
   {self.base_dir}/COVID-19_Radiography_Dataset/
   ├── COVID/
   │   └── images/
   ├── Normal/
   │   └── images/
   ├── Lung_Opacity/
   │   └── images/
   └── Viral Pneumonia/
       └── images/

📊 Dataset Info:
   - Size: ~1.5 GB
   - Images: 21,165 chest X-rays
   - Classes: COVID-19, Normal, Lung Opacity, Viral Pneumonia
   - Format: PNG images


═══════════════════════════════════════════════════════════════════════════
📚 ALTERNATIVE DATASETS (Optional - for further improvement)
═══════════════════════════════════════════════════════════════════════════

4. RSNA Pneumonia Detection Challenge Dataset
   🔗 https://www.kaggle.com/c/rsna-pneumonia-detection-challenge/data
   📊 ~25,000 images with pneumonia annotations

5. CheXpert Dataset (Stanford)
   🔗 https://stanfordmlgroup.github.io/competitions/chexpert/
   📊 224,316 chest radiographs from 65,240 patients
   ⚠️  Requires registration and agreement to terms

6. MIMIC-CXR Database
   🔗 https://physionet.org/content/mimic-cxr/2.0.0/
   📊 377,110 images from 227,835 studies
   ⚠️  Requires PhysioNet credentialing


═══════════════════════════════════════════════════════════════════════════
🚀 QUICK START COMMANDS
═══════════════════════════════════════════════════════════════════════════

# Install required tools
pip install kaggle

# Setup Kaggle API (after placing kaggle.json)
chmod 600 ~/.kaggle/kaggle.json  # Linux/Mac only

# Download datasets
cd app/model_train

# Kaggle Pneumonia Dataset
kaggle datasets download -d paultimothymooney/chest-xray-pneumonia
unzip chest-xray-pneumonia.zip -d chest_xray

# COVID-19 Dataset
kaggle datasets download -d tawsifurrahman/covid19-radiography-database
unzip covid19-radiography-database.zip -d COVID-19_Radiography_Dataset


═══════════════════════════════════════════════════════════════════════════
📝 AFTER DOWNLOADING
═══════════════════════════════════════════════════════════════════════════

1. Verify dataset structure matches the paths in enhanced_train_model.py
2. Update Config class in enhanced_train_model.py if paths differ
3. Run training:
   python app/model_train/enhanced_train_model.py

4. Training will automatically:
   ✓ Load all available datasets
   ✓ Apply data augmentation
   ✓ Train with transfer learning
   ✓ Save best model to app/models/enhanced_chest_xray_model.keras


═══════════════════════════════════════════════════════════════════════════
⚠️  IMPORTANT NOTES
═══════════════════════════════════════════════════════════════════════════

• Total download size: ~45 GB (NIH + Kaggle + COVID)
• Ensure you have sufficient disk space (100+ GB recommended with extraction)
• NIH dataset download can take several hours depending on connection
• GPU recommended for training (NVIDIA with CUDA support)
• Training time: 8-24 hours depending on hardware and dataset size
• Model file size: ~100-200 MB


═══════════════════════════════════════════════════════════════════════════
📧 DATASET CITATIONS
═══════════════════════════════════════════════════════════════════════════

NIH Chest X-Ray:
  Wang, X., Peng, Y., Lu, L., Lu, Z., Bagheri, M., & Summers, R. M. (2017).
  ChestX-Ray8: Hospital-scale chest X-ray database and benchmarks on
  weakly-supervised classification and localization of common thorax diseases.
  
Kaggle Pneumonia:
  Kermany, D. S., Goldbaum, M., et al. (2018).
  Identifying Medical Diagnoses and Treatable Diseases by Image-Based Deep Learning.
  Cell, 172(5), 1122-1131.
  
COVID-19 Radiography:
  M.E.H. Chowdhury, T. Rahman, et al. (2020).
  Can AI help in screening Viral and COVID-19 pneumonia?
  IEEE Access, Vol. 8, 2020, pp. 132665 - 132676.

═══════════════════════════════════════════════════════════════════════════
✅ READY TO TRAIN
═══════════════════════════════════════════════════════════════════════════

Once datasets are downloaded and extracted, you can start training:

    python app/model_train/enhanced_train_model.py

The script will automatically detect available datasets and train accordingly.

═══════════════════════════════════════════════════════════════════════════
"""
        print(instructions)
    
    def check_dataset_availability(self):
        """Check which datasets are already downloaded"""
        logger.info("\n" + "="*70)
        logger.info("CHECKING DATASET AVAILABILITY")
        logger.info("="*70)
        
        datasets = {
            "NIH Chest X-Ray": {
                "path": self.base_dir / "NIH_CHEST_XRAY",
                "csv": self.base_dir / "Data_Entry_2017.csv"
            },
            "Kaggle Pneumonia": {
                "path": self.base_dir / "chest_xray"
            },
            "COVID-19 Radiography": {
                "path": self.base_dir / "COVID-19_Radiography_Dataset"
            }
        }
        
        available = []
        missing = []
        
        for name, paths in datasets.items():
            if paths["path"].exists():
                available.append(name)
                logger.info(f"✓ {name}: FOUND at {paths['path']}")
            else:
                missing.append(name)
                logger.info(f"✗ {name}: NOT FOUND (expected at {paths['path']})")
        
        logger.info("="*70)
        logger.info(f"Available datasets: {len(available)}/3")
        
        if missing:
            logger.info(f"Missing datasets: {', '.join(missing)}")
            logger.info("Run with --instructions flag to see download instructions")
        else:
            logger.info("✓ All datasets are available! Ready to train.")
        
        logger.info("="*70)
        
        return available, missing


def main():
    """Main function"""
    downloader = DatasetDownloader()
    
    if len(sys.argv) > 1 and sys.argv[1] in ['--instructions', '-i', '--help', '-h']:
        downloader.print_instructions()
    else:
        available, missing = downloader.check_dataset_availability()
        
        if missing:
            print("\n" + "="*70)
            print("To see detailed download instructions, run:")
            print("  python dataset_downloader.py --instructions")
            print("="*70)


if __name__ == "__main__":
    main()
