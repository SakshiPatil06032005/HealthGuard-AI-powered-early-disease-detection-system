# HealthGuard Medical ChatBot - Setup & Integration Guide

## 🎯 Quick Integration Guide

### Step 1: Copy Files to Your Project

Copy these files to your React project:
```
src/
├── components/
│   ├── MedicalChatBot.jsx
│   └── MedicalChatBot.css
└── ...other files
```

### Step 2: Install Dependencies

```bash
npm install axios
```

### Step 3: Configure Environment Variables

**For Vite Projects:**
```env
# .env or .env.local
VITE_HF_API_KEY=hf_your_actual_key_here
VITE_HF_API_KEY_EXTRA=hf_backup_key_here
VITE_OPENAI_KEY=sk_your_key_here
```

**For Create React App:**
```env
# .env or .env.local
REACT_APP_HF_API_KEY=hf_your_actual_key_here
REACT_APP_HF_API_KEY_EXTRA=hf_backup_key_here
REACT_APP_OPENAI_KEY=sk_your_key_here
```

**⚠️ IMPORTANT**: Update the environment variable access in `MedicalChatBot.jsx` line 142:

For **Vite**:
```jsx
const apiKey = import.meta.env.VITE_HF_API_KEY;
```

For **Create React App**:
```jsx
const apiKey = process.env.REACT_APP_HF_API_KEY;
```

### Step 4: Import & Use Component

```jsx
import MedicalChatBot from './components/MedicalChatBot';

function App() {
  return (
    <div className="app">
      <MedicalChatBot />
    </div>
  );
}

export default App;
```

### Step 5: Add to .gitignore

```gitignore
# Environment variables
.env
.env.local
.env.*.local

# Never commit API keys!
```

## 🔑 Obtaining API Keys

### HuggingFace API Key

1. **Create Account**
   - Go to https://huggingface.co
   - Sign up or log in

2. **Generate Token**
   - Navigate to Settings → Access Tokens
   - URL: https://huggingface.co/settings/tokens
   - Click "New token"
   - Name: "HealthGuard ChatBot"
   - Select "Read" permissions (minimum required)
   - Copy the token

3. **Add to .env**
   ```env
   VITE_HF_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxxxxx
   ```

### OpenAI API Key (Optional - for future use)

1. **Create Account**
   - Go to https://platform.openai.com
   - Sign up or log in

2. **Generate API Key**
   - Navigate to API Keys section
   - URL: https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy the key (you won't see it again)

3. **Add to .env**
   ```env
   VITE_OPENAI_KEY=sk_xxxxxxxxxxxxxxxxxxxxxxxx
   ```

### FDA Drug Label API

**No key needed!** It's a public API:
- Endpoint: `https://api.fda.gov/drug/label.json`
- Rate limit: 240 requests per minute
- Already integrated in the component

## 🔧 Configuration Options

### Modify HuggingFace Model

The component uses `bert-base-uncased` for disease prediction. You can change it:

**In `MedicalChatBot.jsx`, function `getDiseasePrediction()`:**

```jsx
// Current model
const response = await axios.post(
  'https://api-inference.huggingface.co/models/bert-base-uncased',
  // ...
);

// Alternative medical models:
// 'https://api-inference.huggingface.co/models/dmis-lab/biobert-base-cased-v1.1'
// 'https://api-inference.huggingface.co/models/medalpaca/medalpaca-7b'
// 'https://api-inference.huggingface.co/models/microsoft/biogpt'
```

### Customize Severity Keywords

**In `MedicalChatBot.jsx`, function `handleSeverityLevel()`:**

```jsx
const severeKeywords = [
  'chest pain',
  'breathing',
  'bleeding',
  'unconscious',
  'severe',
  'emergency',
  // Add your custom keywords
];

const moderateKeywords = [
  'fever',
  'infection',
  'persistent',
  // Add your custom keywords
];
```

### Adjust Medicine Display Count

**In `MedicalChatBot.jsx`, function `generateBotResponse()`:**

```jsx
// Change from 3 to desired number
medicines.slice(0, 3).forEach((med, index) => {
  // Display medicine
});
```

### Customize UI Colors

**In `MedicalChatBot.css`:**

```css
/* Primary gradient color */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
/* Change to your brand colors */

/* Example alternatives:
   Blue: linear-gradient(135deg, #1890ff 0%, #0050b3 100%)
   Green: linear-gradient(135deg, #00b96b 0%, #005a2f 100%)
   Purple: linear-gradient(135deg, #722ed1 0%, #391085 100%)
*/
```

## 🚀 Development Workflow

### Running in Development

```bash
# For Vite projects
npm run dev

# For Create React App
npm start

# Make sure .env file is in root directory
```

### Building for Production

```bash
# For Vite
npm run build

# For Create React App
npm run build

# Build output will include environment variables from .env.production
```

### Creating Production .env

Create a `.env.production` file with production API keys:
```env
VITE_HF_API_KEY=hf_production_key_here
VITE_OPENAI_KEY=sk_production_key_here
```

## 📱 Responsive Design

The component automatically adapts to screen sizes:

| Screen Size | Layout | Message Width |
|-------------|--------|---------------|
| Desktop (>768px) | Full UI | 70% |
| Tablet (481-768px) | Responsive | 85% |
| Mobile (<480px) | Compact | 90% |

## 🔐 Security Best Practices

### ✅ DO:
- Store API keys in `.env` files
- Use `.env.example` as template
- Regenerate keys if accidentally exposed
- Use environment-specific keys (.env.production, .env.development)
- Rotate keys regularly

### ❌ DON'T:
- Commit `.env` files to git
- Share API keys via email or chat
- Hardcode API keys in source code
- Use the same keys for development and production
- Log API keys to console in production

## 🧪 Testing

### Test Without Real APIs

To test the UI without making actual API calls, modify `getDiseasePrediction()`:

```jsx
const getDiseasePrediction = async (userMessage) => {
  // Mock response for testing
  return {
    label: 'Common Cold',
    score: 0.85
  };
};
```

### Test Voice Input

Voice input requires:
1. A browser that supports Web Speech API (Chrome, Edge, Safari)
2. HTTPS connection (or localhost)
3. Microphone permission granted

## 🐛 Common Issues & Solutions

### Issue 1: "process is not defined"
**Cause**: Using `process.env` in Vite  
**Solution**: Use `import.meta.env.VITE_*` instead

```jsx
// Wrong for Vite
const key = process.env.REACT_APP_HF_API_KEY;

// Correct for Vite
const key = import.meta.env.VITE_HF_API_KEY;
```

### Issue 2: API Key shows as undefined
**Cause**: Didn't restart dev server after adding .env  
**Solution**: 
```bash
# Stop dev server (Ctrl+C)
# Then restart:
npm run dev  # or npm start
```

### Issue 3: CORS errors
**Cause**: Browser blocking cross-origin requests  
**Solution**: 
- HuggingFace API should handle CORS
- FDA API should handle CORS
- If issues persist, use a backend proxy

### Issue 4: Voice input not working
**Cause**: Browser doesn't support Web Speech API  
**Solution**: 
- Use Chrome, Edge, or Safari
- Ensure HTTPS (or localhost)
- Check microphone permissions

## 📊 Performance Tips

1. **Cache Responses**: Implement response caching to avoid repeated API calls
2. **Debounce Voice Input**: Avoid sending multiple recognition requests
3. **Lazy Load Models**: HuggingFace loads models on first use
4. **Optimize CSS**: Consider using CSS-in-JS for dynamic theming

## 🔄 API Rate Limits

| API | Limit | Handling |
|-----|-------|----------|
| HuggingFace | 30 requests/minute (free tier) | Implement queue if needed |
| FDA Drug Label | 240 requests/minute | Implement caching |
| Web Speech API | Browser-based | No limit |

## 📚 Additional Resources

- **React Hooks**: https://react.dev/reference/react/hooks
- **HuggingFace API**: https://huggingface.co/inference-api
- **FDA OpenAPI**: https://open.fda.gov
- **Web Speech API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
- **axios Documentation**: https://axios-http.com/docs/intro

## 🎓 Learning Path

1. **Understand the code**: Read MedicalChatBot.jsx comments
2. **Test with mock data**: Modify APIs to return test responses
3. **Add logging**: Console.log key variables to track data flow
4. **Customize UI**: Modify CSS to match your brand
5. **Deploy**: Follow your deployment process

## 📞 Debugging Checklist

- [ ] .env file exists in root directory
- [ ] API keys are valid and not expired
- [ ] Dev server restarted after .env changes
- [ ] axios is installed (`npm list axios`)
- [ ] Browser console shows no errors
- [ ] Network tab shows successful API calls
- [ ] Microphone permissions granted (for voice input)
- [ ] All dependencies installed (`npm install`)

## 🚀 Deployment

### Vercel (Recommended for Next.js)
```bash
# Add env variables in Vercel dashboard
# Project Settings → Environment Variables
# Then deploy:
vercel
```

### Netlify
```bash
# Add env variables in Netlify dashboard
# Site Settings → Build & Deploy → Environment
# Then deploy:
netlify deploy
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build
ENV VITE_HF_API_KEY=$HF_API_KEY
CMD ["npm", "run", "preview"]
```

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Production Ready
