# Quick Start Guide

## Setup
1. Install requirements:
```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

2. Optional: Set OpenAI API key for medical explanations
```powershell
$env:API_TOKEN = "your-openai-key"  # Replace with your key
```

## Run the Demo
1. Run with sample images (downloads test X-rays automatically):
```powershell
python demo_prediction.py
```

2. Or run with your own X-ray:
```powershell
python demo_prediction.py path/to/your/xray.png
```

## Use the Web Interface
1. Start the server:
```powershell
python run.py
```

2. Open http://localhost:3000 in your browser

3. Login as doctor:
   - Username: mahima
   - Password: mahima

4. Click "Upload X-ray" and select an image

## What the Results Mean

The model can detect these conditions:
- Atelectasis
- Cardiomegaly
- Consolidation
- Edema
- Effusion
- Emphysema
- Fibrosis
- Hernia
- Infiltration
- Mass
- Nodule
- Pleural Thickening
- Pneumonia
- Pneumothorax

The output includes:
1. Predicted conditions (if any)
2. Heatmap showing areas of interest
3. Medical explanation (if API_TOKEN is set)

## Troubleshooting

1. If you see "Model not found":
   - Ensure `app/models/chest_xray_model.keras` exists
   - Re-download or restore the model file

2. If you get image errors:
   - Use PNG or JPEG format
   - Ensure the image is a chest X-ray
   - Try the sample images first

3. For OpenAI/chat errors:
   - Set the API_TOKEN environment variable
   - Check your API key is valid