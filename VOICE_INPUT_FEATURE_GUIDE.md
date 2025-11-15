# Voice Input Feature - Implementation Guide

## 🎙️ Overview

A complete voice-based symptom checker has been successfully integrated into the patient dashboard. Users can now speak their symptoms in English, and the system will:

1. **Convert speech to text** using speech recognition
2. **Detect the language** and ensure it's English
3. **Extract symptoms** from natural language
4. **Predict diseases** using AI
5. **Suggest medicines** for the predicted condition
6. **Provide voice feedback** if non-English is detected

---

## 📁 Files Created/Modified

### New Files Created:

1. **`app/voice_processor.py`** - Speech-to-text processing module
   - Transcribes audio to text
   - Validates language (English only)
   - Generates voice feedback
   - Handles audio format conversion

2. **`app/symptom_extractor.py`** - Natural language symptom extraction
   - Extracts symptoms from spoken text
   - Maps 30+ symptom keywords
   - Handles negations ("no fever", "don't have cough")
   - Validates symptom detection

### Modified Files:

3. **`app/dashboard_routes.py`**
   - Added `/dashboard/speech-to-text` endpoint (POST)
   - Added `/dashboard/voice-feedback/<user_id>` endpoint (GET)
   - Integrated voice processor and symptom extractor

4. **`app/templates/dashboards/symptom_prediction.html`**
   - Added voice input UI section
   - Added recording indicator with animation
   - Implemented MediaRecorder API integration
   - Added real-time feedback display

---

## 🔧 Technical Implementation

### Backend Architecture

```
Voice Input Flow:
1. Audio File (WebM) → Flask Endpoint
2. Save to Temp File
3. Convert to WAV (if needed)
4. Speech Recognition (Google API - Free Tier)
5. Language Detection (langdetect)
6. Symptom Extraction (NLP)
7. Disease Prediction (AI Model)
8. Medicine Recommendation
9. Save to Database
10. Return JSON Response
```

### Frontend Architecture

```
User Interface Flow:
1. Click "🎙 Speak Symptoms" button
2. Request microphone permission
3. Record for 5 seconds (MediaRecorder API)
4. Show recording indicator
5. Send audio to backend (FormData)
6. Display processing status
7. Show results or errors
8. Play voice feedback if needed
```

---

## 🎯 Features Implemented

### ✅ Core Features

- **Voice Recording**: 5-second audio capture using MediaRecorder API
- **Speech-to-Text**: Converts audio to text using Google Speech Recognition (free tier)
- **Language Detection**: Validates English-only input using `langdetect`
- **Symptom Extraction**: Extracts 30+ symptoms from natural language
- **Disease Prediction**: Uses existing AI model for disease prediction
- **Medicine Suggestions**: Provides 2-3 medicines based on predicted disease
- **Voice Feedback**: Speaks "Please speak in English" if non-English detected

### 🛡️ Error Handling

The system handles:
- ❌ No audio input
- ❌ Microphone permission denied
- ❌ No speech detected in audio
- ❌ Wrong file format
- ❌ Non-English language detected
- ❌ No symptoms found in speech
- ❌ API call failures
- ❌ Network errors

### 📱 User Experience Features

- **Visual feedback**: Recording indicator with pulse animation
- **Timer display**: Shows "0s / 5s" during recording
- **Status updates**: "Listening...", "Processing...", "Recognizing symptoms..."
- **Results display**: Shows transcript, detected symptoms, predictions, and medicines
- **Error messages**: Clear, actionable error messages
- **Voice feedback**: Audio response for language errors

---

## 🚀 How to Use

### For Patients:

1. Navigate to **Dashboard → Symptom Checker**
2. Click the **"🎙 Speak Symptoms"** button
3. Allow microphone access when prompted
4. Speak your symptoms clearly in English (e.g., "I have fever, cough, and headache")
5. Wait for the system to process (5 seconds recording + processing time)
6. View your results:
   - Transcribed text
   - Detected symptoms
   - Disease predictions with confidence scores
   - Recommended medicines

### Example Voice Inputs:

✅ **Good Examples:**
- "I have fever and cough for three days"
- "I'm feeling tired, have body pain and headache"
- "I can't breathe properly and have chest pain"

❌ **Bad Examples:**
- Speaking in Hindi/Marathi (will show error + voice feedback)
- Too quiet or unclear speech
- Background noise

---

## 🔐 Security & Privacy

- Audio files are saved temporarily and deleted after processing
- No permanent storage of voice recordings
- Patient data saved to database with appropriate access controls
- Only authorized roles (patient, doctor) can access the endpoint

---

## 📊 Database Schema

Voice predictions are saved with:
```python
{
    'prediction_type': 'voice_symptoms',
    'predicted_disease': 'Top disease',
    'confidence': 85.5,
    'symptoms': 'Fever, Cough, Fatigue',
    'notes': {
        'transcript': 'I have fever and cough',
        'detected_symptoms': ['fever', 'cough'],
        'medicines': { ... }
    }
}
```

---

## 🧪 Testing Guide

### Test Case 1: Successful Voice Input
1. Click voice button
2. Say: "I have fever, cough, and body pain"
3. **Expected**: Shows transcript, symptoms, predictions, medicines

### Test Case 2: Non-English Language
1. Click voice button
2. Speak in Hindi/Marathi
3. **Expected**: Error message + "Please speak in English" voice feedback

### Test Case 3: No Speech Detected
1. Click voice button
2. Stay silent for 5 seconds
3. **Expected**: Error message "No speech detected"

### Test Case 4: Microphone Permission Denied
1. Click voice button
2. Deny microphone permission
3. **Expected**: Error message about permissions

---

## 🛠️ Dependencies Installed

```bash
pip install SpeechRecognition  # Google Speech API (free)
pip install gtts              # Text-to-speech
pip install langdetect        # Language detection
pip install pydub             # Audio format conversion
pip install PyAudio           # Audio capture (optional)
```

---

## ⚙️ Configuration

### Using Google Cloud Speech API (Optional - More Accurate):

1. Set environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

2. Modify `voice_processor.py`:
```python
voice_processor = VoiceProcessor(use_google_cloud=True)
```

### Using Free Speech Recognition (Default):

No configuration needed! Works out of the box using Google's free API.

---

## 🎨 UI Components

### Voice Input Section Styling:
- **Purple-blue gradient background**
- **Animated recording indicator** (pulsing red dot)
- **Recording timer** (shows 0s / 5s)
- **Results box** (green border for success)
- **Error box** (red border for errors)

### CSS Classes Used:
- `.recording-indicator` - Animated recording dot
- `.recording-dot` - Pulsing red circle
- `@keyframes pulse-recording` - Animation
- `@keyframes ripple` - Ripple effect

---

## 📝 API Endpoints

### POST `/dashboard/speech-to-text`

**Request:**
```
Content-Type: multipart/form-data
Body: audio file (WebM format)
```

**Success Response (200):**
```json
{
    "status": "success",
    "transcript": "I have fever and cough",
    "confidence": 0.95,
    "symptom_summary": "Detected symptoms: Fever and Cough",
    "detected_symptoms": ["Fever", "Cough"],
    "predictions": [
        {
            "disease": "Flu",
            "confidence": 75.5,
            "severity": "moderate"
        }
    ],
    "medicine_suggestions": {
        "primary_medicines": [...],
        "supportive_care": [...],
        "precautions": [...]
    },
    "selected_disease": "Flu"
}
```

**Error Response (400):**
```json
{
    "status": "error",
    "message": "Please speak in English",
    "error_type": "wrong_language",
    "detected_language": "hi",
    "transcript": "मुझे बुखार है",
    "voice_feedback_url": "/dashboard/voice-feedback/123"
}
```

### GET `/dashboard/voice-feedback/<user_id>`

Returns audio file (MP3) with voice feedback message.

---

## 🐛 Known Limitations

1. **Recording Duration**: Fixed at 5 seconds (can be adjusted in `RECORDING_DURATION`)
2. **Language Support**: English only (by design)
3. **Audio Format**: WebM/Opus (browser-dependent)
4. **Background Noise**: May affect recognition accuracy
5. **Internet Required**: Speech recognition requires internet connection

---

## 🔮 Future Enhancements

- [ ] Multi-language support (Hindi, Marathi)
- [ ] Adjustable recording duration
- [ ] Real-time transcription (streaming)
- [ ] Better audio noise cancellation
- [ ] Offline speech recognition
- [ ] Voice commands for navigation
- [ ] Medical terminology recognition

---

## 📞 Support

For issues or questions, contact the development team or check the logs at:
- Backend logs: Flask console output
- Frontend logs: Browser developer console (F12)

---

## ✅ Testing Checklist

- [x] Voice recording works in Chrome/Firefox
- [x] Speech recognition converts audio to text
- [x] Language detection identifies English
- [x] Symptom extraction finds keywords
- [x] Disease prediction returns results
- [x] Medicine suggestions display properly
- [x] Error handling works for all cases
- [x] Voice feedback plays for non-English
- [x] Database saves voice predictions
- [x] UI animations work smoothly

---

**Implementation Date**: November 13, 2025
**Status**: ✅ Complete and Functional
**Version**: 1.0

---

## 🎉 Success Criteria Met

✅ Speech-to-Text working (English only)
✅ Language validation with voice feedback
✅ Symptom extraction from natural language
✅ Disease prediction integrated
✅ Medicine suggestions displayed (2-3 items)
✅ All error scenarios handled
✅ Professional UI with animations
✅ Database integration complete
✅ Security measures in place
✅ Comprehensive documentation provided
