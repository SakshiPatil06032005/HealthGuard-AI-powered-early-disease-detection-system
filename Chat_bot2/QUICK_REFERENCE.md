# HealthGuard Medical ChatBot - Quick Reference Guide

## 🚀 5-Minute Quick Start

### 1. Copy Files
```
MedicalChatBot.jsx → your-project/src/components/
MedicalChatBot.css → your-project/src/components/
```

### 2. Install Dependency
```bash
npm install axios
```

### 3. Create .env File
```env
VITE_HF_API_KEY=your_huggingface_key_here
```

### 4. Import Component
```jsx
import MedicalChatBot from './components/MedicalChatBot';

function App() {
  return <MedicalChatBot />;
}
```

### 5. Restart Dev Server
```bash
npm run dev
```

---

## 📁 File Structure

| File | Purpose | Lines |
|------|---------|-------|
| `MedicalChatBot.jsx` | Main React component | ~500 |
| `MedicalChatBot.css` | Styling (responsive) | ~350 |
| `.env.example` | API keys template | 30 |
| `README.md` | Full documentation | 400 |
| `SETUP_GUIDE.md` | Integration guide | 500 |
| `USAGE_EXAMPLES.jsx` | Code examples | 300 |
| `TEST_CONFIG.js` | Testing utilities | 400 |

---

## 🔑 Key Functions

```jsx
// Disease Prediction
getDiseasePrediction(userMessage)  // → HuggingFace API

// Medicine Info
getMedicineInfo(disease)            // → FDA Drug Label API

// Severity Assessment
handleSeverityLevel(userMessage)    // → 'severe'|'moderate'|'mild'

// Generate Response
generateBotResponse(userMessage)    // → orchestrates above

// Voice Input
startVoiceRecognition()             // → toggles Web Speech API
```

---

## 🔧 Configuration

### Environment Variables

**For Vite:**
```env
VITE_HF_API_KEY=hf_xxxxx
```

**For Create React App:**
```env
REACT_APP_HF_API_KEY=hf_xxxxx
```

### Update Vite vs CRA

**MedicalChatBot.jsx line ~142:**

```jsx
// Vite ✅
const apiKey = import.meta.env.VITE_HF_API_KEY;

// Create React App ✅
// const apiKey = process.env.REACT_APP_HF_API_KEY;
```

---

## 🎨 UI Layout

```
┌─────────────────────────────────┐
│  HealthGuard Medical Assistant  │ ← Header
├─────────────────────────────────┤
│  Bot: Hello! How are you?       │
│                                 │
│                  You: I have... │
│  Bot: Based on your...          │
│  [Typing indicator]             │
│                                 │
│                                 │ ← Message Area
│                                 │
├─────────────────────────────────┤
│  [Input] [🎤] [Send]            │ ← Input Area
│  ⚠️ Medical Disclaimer           │
└─────────────────────────────────┘
```

---

## 📊 Component Features

### ✅ Implemented

- [x] Two-way chat interface
- [x] HuggingFace disease prediction
- [x] FDA drug recommendations
- [x] Severity level detection
- [x] Web Speech API (voice input)
- [x] Responsive design (mobile/tablet/desktop)
- [x] Auto-scroll to latest message
- [x] Typing indicator animation
- [x] Error handling & fallbacks
- [x] No hardcoded API keys
- [x] Professional gradient UI
- [x] Message timestamps

### 🔄 How It Works

```
User Message
    ↓
Check Severity (Keywords)
    ↓
Send to HuggingFace (Disease Prediction)
    ↓
Send to FDA API (Medicine Info)
    ↓
Generate Response
    ↓
Display in Chat
```

---

## 🐛 Common Issues & Fixes

### ❌ "API key not configured"
```bash
# Solution: Restart dev server after adding .env
npm run dev
```

### ❌ "Cannot find module axios"
```bash
# Solution: Install axios
npm install axios
```

### ❌ Voice input not working
```
Solution:
1. Use Chrome, Edge, or Safari
2. Ensure HTTPS (or localhost)
3. Grant microphone permission
```

### ❌ "process is not defined" (Vite)
```jsx
// ❌ Wrong
const key = process.env.VITE_HF_API_KEY;

// ✅ Correct
const key = import.meta.env.VITE_HF_API_KEY;
```

---

## 🔐 Security Checklist

- [ ] Never commit `.env` file to git
- [ ] Add `.env` to `.gitignore`
- [ ] Use environment-specific keys
- [ ] Regenerate keys if exposed
- [ ] Don't log API keys to console
- [ ] Use HTTPS in production
- [ ] Validate user inputs
- [ ] Implement rate limiting

---

## 📱 Responsive Breakpoints

| Device | Width | Message Width |
|--------|-------|---------------|
| Desktop | >768px | 70% |
| Tablet | 481-768px | 85% |
| Mobile | <480px | 90% |

---

## 🎯 Severity Keywords

### 🔴 SEVERE (Urgent)
- chest pain, breathing difficulty, bleeding, unconscious, emergency, critical, collapsed, fracture, burn, poisoning

### 🟡 MODERATE
- fever, infection, persistent, painful, nausea, vomiting, headache, dizziness, abdominal pain

### 🟢 MILD
- mild fever, slight headache, minor cough, tired, fatigue

---

## 🌐 API Endpoints

### HuggingFace
```
https://api-inference.huggingface.co/models/bert-base-uncased
Authorization: Bearer {VITE_HF_API_KEY}
```

### FDA Drug Label
```
https://api.fda.gov/drug/label.json?search=indications_and_usage:{DISEASE}
(No authentication required)
```

---

## 💬 State Management

```jsx
// Messages State
messages: [
  {
    id: 1,
    text: "...",
    sender: 'bot'|'user',
    timestamp: Date
  }
]

// UI State
inputValue: string
isLoading: boolean
isListening: boolean
```

---

## 🧪 Testing

### Mock API Response
```jsx
// In getDiseasePrediction():
return Promise.resolve({
  label: 'Common Cold',
  score: 0.85
});
```

### Test Severity Detection
```jsx
handleSeverityLevel("chest pain")  // → 'severe'
handleSeverityLevel("fever")       // → 'moderate'
handleSeverityLevel("tiredness")   // → 'mild'
```

### Test Voice Input
```
Click 🎤 button → browser requests microphone
Speak naturally → converted to text
Text appears in input → ready to send
```

---

## 📊 Performance Tips

1. **Cache API responses** to avoid repeated calls
2. **Debounce voice input** to prevent multiple recognition
3. **Lazy load images** if adding media
4. **Optimize CSS** with CSS-in-JS if needed
5. **Monitor API rate limits** (HF: 30/min, FDA: 240/min)

---

## 🚀 Deployment

### Vercel
```bash
1. Add env variables in Vercel dashboard
2. Push to GitHub
3. Auto-deploys
```

### Netlify
```bash
1. Add env variables in Site Settings
2. Push to GitHub
3. Auto-deploys
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install && npm run build
CMD ["npm", "run", "preview"]
```

---

## 📚 Required Knowledge

- ✅ React Hooks (useState, useEffect, useRef)
- ✅ JavaScript async/await
- ✅ axios HTTP requests
- ✅ CSS Flexbox/Grid
- ✅ Environment variables
- ✅ Web Speech API basics

---

## 🔗 Useful Links

| Resource | URL |
|----------|-----|
| HuggingFace Tokens | https://huggingface.co/settings/tokens |
| FDA API Docs | https://open.fda.gov |
| React Hooks | https://react.dev/reference/react/hooks |
| axios Docs | https://axios-http.com |
| Web Speech API | https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API |

---

## ⚡ Performance Metrics

| Operation | Expected Time |
|-----------|----------------|
| Component Load | <500ms |
| User Message Display | <100ms |
| Severity Check | <50ms |
| Disease Prediction API | 2-5s |
| Medicine Fetch API | 1-3s |
| Voice Recognition | Variable |

---

## 🎓 Learning Resources

1. **Start Here**: Read `README.md`
2. **Setup**: Follow `SETUP_GUIDE.md`
3. **Examples**: Check `USAGE_EXAMPLES.jsx`
4. **Testing**: Use `TEST_CONFIG.js`
5. **Deep Dive**: Read component comments

---

## 📋 Pre-Deployment Checklist

- [ ] `.env` file created with all API keys
- [ ] `.env` added to `.gitignore`
- [ ] All dependencies installed (`npm install`)
- [ ] Component imports work correctly
- [ ] No console errors
- [ ] Tested in target browsers
- [ ] Mobile responsiveness verified
- [ ] Voice input works (Chrome/Edge/Safari)
- [ ] API keys are production-ready
- [ ] Disclaimer visible to users
- [ ] Error handling tested
- [ ] Performance acceptable

---

## 🆘 Getting Help

1. **Check browser console** for errors
2. **Verify `.env` file** exists and is correct
3. **Restart dev server** after any .env changes
4. **Test with mock data** to isolate issues
5. **Check API status** (HF and FDA)
6. **Review error handling** in component

---

## 📝 Notes

- Component uses **client-side rendering** only
- **No backend server required**
- APIs called directly from browser
- **CORS handling** done by API providers
- **Fully responsive** design included
- **Production ready** as-is

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: ✅ Production Ready  
**Support**: All modern browsers (except IE)
