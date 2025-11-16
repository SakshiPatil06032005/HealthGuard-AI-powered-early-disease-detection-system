# HealthGuard Medical ChatBot Component

A sophisticated two-way AI medical chatbot for the HealthGuard system that provides conversational health assistance, disease prediction, medicine recommendations, and safety guidance.

## 📋 Features

### ✅ Core Features Implemented

1. **Two-Way Conversational Chat**
   - WhatsApp/ChatGPT style UI
   - User messages on the right, bot messages on the left
   - Smooth animations and transitions
   - Auto-scroll to latest message
   - Typing indicators for bot responses

2. **Disease Prediction**
   - Integrates with HuggingFace Inference API
   - Uses environment variables for API keys (never hardcoded)
   - Analyzes user symptoms to predict potential diseases
   - Supports multiple models via HuggingFace

3. **Medicine Recommendation**
   - Fetches from FDA Drug Label API (free, no authentication required)
   - Extracts medicine names, usage, and warnings
   - Displays up to 3 recommended medicines
   - Shows manufacturer information

4. **Severity & Safety Logic**
   - **Severe Symptoms**: "You should visit a hospital or doctor immediately"
   - **Moderate Symptoms**: "Monitor your condition and consult a doctor if symptoms worsen"
   - **Mild Symptoms**: "This can be treated with rest and basic medicines"
   - Keyword-based detection for quick severity assessment

5. **Voice Input (Web Speech API)**
   - Microphone button for voice-to-text conversion
   - Real-time speech recognition
   - Visual feedback (listening indicator)
   - Fallback for unsupported browsers

6. **Professional UI**
   - Modern gradient design
   - Responsive layout (mobile, tablet, desktop)
   - Accessibility features
   - Clean typography and spacing
   - Smooth animations

## 🚀 Quick Start

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- React 16.8+ (for hooks support)
- axios installed

### Installation

1. **Install Dependencies**
   ```bash
   npm install axios
   ```

2. **Setup Environment Variables**
   
   Create a `.env` or `.env.local` file in your project root:
   
   ```bash
   # For Vite projects:
   VITE_HF_API_KEY=your_huggingface_api_key_here
   VITE_HF_API_KEY_EXTRA=your_backup_key_here
   VITE_OPENAI_KEY=your_openai_key_here
   
   # For Create React App:
   REACT_APP_HF_API_KEY=your_huggingface_api_key_here
   REACT_APP_HF_API_KEY_EXTRA=your_backup_key_here
   REACT_APP_OPENAI_KEY=your_openai_key_here
   ```

   **Note**: Adjust the prefix based on your build tool:
   - **Vite**: Use `VITE_` prefix
   - **Create React App**: Use `REACT_APP_` prefix
   - Update the import statement in `MedicalChatBot.jsx` accordingly

3. **Import Component**
   ```jsx
   import MedicalChatBot from './MedicalChatBot';
   
   function App() {
     return <MedicalChatBot />;
   }
   
   export default App;
   ```

## 📝 API Keys Configuration

### Getting HuggingFace API Key

1. Visit [HuggingFace Tokens](https://huggingface.co/settings/tokens)
2. Create a new token (read-only is sufficient)
3. Copy the token and add it to your `.env` file
4. The key format: `hf_xxxxxxxxxxxxx`

### FDA Drug Label API

- **No API key required!** 
- Public endpoint: `https://api.fda.gov/drug/label.json`
- Rate limited to 240 requests per minute
- No authentication headers needed

## 🏗️ Project Structure

```
Chat_bot2/
├── MedicalChatBot.jsx          # Main component (all logic)
├── MedicalChatBot.css          # Styling (WhatsApp/ChatGPT style)
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## 📚 Component Functions

### `getDiseasePrediction(userMessage)`
- **Purpose**: Send user message to HuggingFace API for disease prediction
- **Parameters**: User symptom description
- **Returns**: Predicted disease/condition
- **Error Handling**: Returns null if API key missing or request fails

### `getMedicineInfo(disease)`
- **Purpose**: Fetch medicine information from FDA API
- **Parameters**: Disease/condition name
- **Returns**: Array of medicine objects with name, usage, warnings
- **Rate Limiting**: Respects FDA API limits

### `handleSeverityLevel(userMessage)`
- **Purpose**: Determine urgency level and provide recommendations
- **Parameters**: User message
- **Returns**: Object with level and recommendation message
- **Levels**: 'severe', 'moderate', 'mild'

### `generateBotResponse(userMessage)`
- **Purpose**: Orchestrate disease prediction, medicine recommendations, and response generation
- **Parameters**: User message
- **Side Effects**: Updates messages state, shows typing indicator

### `startVoiceRecognition()`
- **Purpose**: Toggle Web Speech API voice input
- **Parameters**: None
- **Returns**: Void
- **Browser Support**: Chrome, Edge, Safari (partial), Firefox (partial)

## 🎨 UI Components

### Chat Interface
- Message bubbles with timestamps
- Typing indicator animation
- Smooth scroll to latest message
- Responsive design for all screen sizes

### Input Area
- Text input field with placeholder
- Voice input button (🎤)
- Send button with state feedback
- Disclaimer text

### Header
- App title with icon
- Status indicator ("Online • Ready to help")
- Gradient background

## ⚠️ Important Notes

### Security
1. **Never commit `.env` files** with real API keys
2. Add `.env` and `.env.local` to `.gitignore`
3. Use `.env.example` as a template for developers
4. Environment variables are only loaded at build time
5. Client-side code should only use public endpoints

### Error Handling
- API failures show user-friendly error messages
- Voice recognition errors are caught and reported
- Missing API keys are logged to console
- Network errors gracefully degrade functionality

### Limitations
1. Disease prediction is for informational purposes only
2. Not a substitute for professional medical advice
3. Medicine recommendations are generic and not personalized
4. Voice input may not work in all browsers
5. FDA API has rate limits (240 requests/minute)

## 🔧 Customization

### Change API Models
```jsx
// In getDiseasePrediction():
// Current: https://api-inference.huggingface.co/models/bert-base-uncased
// Available models: medical-qa, clinical-bert, biobert, etc.
```

### Modify Severity Keywords
```jsx
// In handleSeverityLevel():
const severeKeywords = ['chest pain', 'bleeding', ...];
const moderateKeywords = ['fever', 'infection', ...];
```

### Customize UI Colors
```css
/* In MedicalChatBot.css */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
/* Change gradient colors to match your brand */
```

## 🌐 Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| Web Speech API | ✅ | ❌ | ⚠️ | ✅ |
| Fetch API | ✅ | ✅ | ✅ | ✅ |
| CSS Grid/Flexbox | ✅ | ✅ | ✅ | ✅ |
| Async/Await | ✅ | ✅ | ✅ | ✅ |

## 📊 Data Flow

```
User Input
    ↓
[Message added to chat]
    ↓
[Severity check (keyword-based)]
    ↓
[HuggingFace API → Disease Prediction]
    ↓
[FDA API → Medicine Info]
    ↓
[Generate Response]
    ↓
[Display in Chat]
```

## 🐛 Troubleshooting

### Issue: "API key not configured"
- **Solution**: Create `.env` file with `VITE_HF_API_KEY` or `REACT_APP_HF_API_KEY`
- Restart dev server after adding .env

### Issue: Voice input not working
- **Solution**: Ensure browser supports Web Speech API
- Check browser permissions for microphone access
- Try a different browser

### Issue: No medicine recommendations appearing
- **Solution**: Check FDA API status at `status.fda.gov`
- Ensure disease name is in FDA database
- Check browser console for error details

### Issue: Slow responses
- **Solution**: HuggingFace API may be loading model from cache
- First request takes longer than subsequent ones
- Check internet connection

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error messages in browser console
3. Verify API keys are correct and have proper permissions
4. Ensure all dependencies are installed

## 📄 Disclaimer

⚠️ **Medical Disclaimer**: This chatbot is for informational purposes only and not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider before making any medical decisions. In case of medical emergencies, call emergency services immediately.

## 📦 Dependencies

- **React**: UI framework
- **axios**: HTTP client for API calls
- **Web Speech API**: Built-in browser API (no installation needed)

## 🔄 Version History

- **v1.0.0**: Initial release with all core features
  - Two-way conversation
  - Disease prediction
  - Medicine recommendations
  - Severity logic
  - Voice input
  - Professional UI

## 📄 File Structure

### MedicalChatBot.jsx
- React functional component with hooks
- ~400 lines of code
- All logic in one file for easy integration
- Well-commented for maintainability

### MedicalChatBot.css
- ~350 lines of styling
- Mobile-responsive design
- Smooth animations
- Professional gradient design

## 🚀 Performance Optimization

- Lazy loading of API responses
- Debounced voice recognition
- Efficient re-renders with React hooks
- CSS animations for smooth UX
- Message caching to prevent re-renders

---

**Created**: 2024
**Status**: Production Ready
**License**: For HealthGuard System Use
