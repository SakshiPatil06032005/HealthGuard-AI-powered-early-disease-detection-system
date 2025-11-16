import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './MedicalChatBot.css';

const MedicalChatBot = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! 👋 I'm your HealthGuard medical assistant. How are you feeling today? Please describe your symptoms or any health concerns you have.",
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  // Initialize Web Speech API
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            setInputValue((prev) => prev + transcript);
          } else {
            interimTranscript += transcript;
          }
        }
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        addBotMessage("Sorry, I couldn't understand your voice. Please try typing your message.");
      };
    }
  }, []);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  /**
   * Get disease prediction from HuggingFace API
   */
  const getDiseasePrediction = async (userMessage) => {
    try {
      const apiKey = import.meta.env.VITE_HF_API_KEY;
      
      if (!apiKey) {
        console.error('HuggingFace API key not configured');
        return null;
      }

      const payload = {
        inputs: userMessage,
      };

      const response = await axios.post(
        'https://api-inference.huggingface.co/models/bert-base-uncased',
        payload,
        {
          headers: {
            Authorization: `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );

      // Extract prediction (adjust based on actual model response)
      if (response.data && response.data.length > 0) {
        return response.data[0];
      }
      return null;
    } catch (error) {
      console.error('Disease prediction error:', error.message);
      return null;
    }
  };

  /**
   * Get medicine information from FDA drug label API
   */
  const getMedicineInfo = async (disease) => {
    try {
      const searchQuery = disease.toLowerCase().replace(/\s+/g, '_');
      const response = await axios.get(
        `https://api.fda.gov/drug/label.json?search=indications_and_usage:${searchQuery}&limit=5`
      );

      if (response.data && response.data.results && response.data.results.length > 0) {
        const medicines = response.data.results.map((drug) => ({
          name: drug.openfda?.brand_name?.[0] || drug.openfda?.generic_name?.[0] || 'Unknown Medicine',
          usage: drug.indications_and_usage?.[0] || 'Usage information not available',
          warnings: drug.warnings?.[0] || 'No specific warnings',
          manufacturer: drug.openfda?.manufacturer_name?.[0] || 'Unknown',
        }));
        return medicines;
      }
      return [];
    } catch (error) {
      console.error('Medicine info error:', error.message);
      return [];
    }
  };

  /**
   * Determine severity level and provide recommendations
   */
  const handleSeverityLevel = (userMessage) => {
    const severeKeywords = [
      'chest pain',
      'breathing',
      'bleeding',
      'unconscious',
      'severe',
      'emergency',
      'critical',
      'collapse',
      'fracture',
      'burn',
      'poisoning',
    ];
    const moderateKeywords = [
      'fever',
      'infection',
      'persistent',
      'worsening',
      'painful',
      'nausea',
      'vomiting',
      'headache',
      'dizziness',
    ];

    const messageLower = userMessage.toLowerCase();
    
    if (severeKeywords.some((keyword) => messageLower.includes(keyword))) {
      return {
        level: 'severe',
        message: '⚠️ Based on your symptoms, you should visit a hospital or doctor immediately. This needs urgent medical attention!',
      };
    } else if (moderateKeywords.some((keyword) => messageLower.includes(keyword))) {
      return {
        level: 'moderate',
        message: '📋 Monitor your condition and consult a doctor if symptoms worsen. Rest well and stay hydrated.',
      };
    }
    return {
      level: 'mild',
      message: '✅ This can usually be treated with rest, hydration, and basic medicines. However, consult a healthcare provider if it persists.',
    };
  };

  /**
   * Start voice recognition
   */
  const startVoiceRecognition = () => {
    if (recognitionRef.current) {
      if (isListening) {
        recognitionRef.current.stop();
        setIsListening(false);
      } else {
        recognitionRef.current.start();
        setIsListening(true);
      }
    } else {
      addBotMessage(
        "Sorry, your browser doesn't support voice recognition. Please type your message instead."
      );
    }
  };

  /**
   * Generate bot response based on user message
   */
  const generateBotResponse = async (userMessage) => {
    setIsLoading(true);

    try {
      // Get severity level
      const severity = handleSeverityLevel(userMessage);

      // Get disease prediction
      const prediction = await getDiseasePrediction(userMessage);

      // Build response
      let response = `I understand you're experiencing these symptoms. Based on what you've described, here's my assessment:\n\n`;

      // Add severity recommendation
      response += `${severity.message}\n\n`;

      // Try to get medicine information
      if (prediction && prediction.label) {
        const medicines = await getMedicineInfo(prediction.label);
        
        if (medicines.length > 0) {
          response += `💊 **Recommended Medicines:**\n`;
          medicines.slice(0, 3).forEach((med, index) => {
            response += `\n${index + 1}. **${med.name}**\n`;
            response += `   Usage: ${med.usage.substring(0, 150)}...\n`;
            if (med.warnings !== 'No specific warnings') {
              response += `   ⚠️ Warnings: ${med.warnings.substring(0, 100)}...\n`;
            }
          });
        } else {
          response += `Please consult with a healthcare provider for personalized medicine recommendations.`;
        }
      } else {
        response += `For specific medicine recommendations, please consult with a licensed healthcare provider.`;
      }

      response += `\n\n📞 If symptoms persist or worsen, don't hesitate to contact your doctor or visit a healthcare facility.`;

      addBotMessage(response);
    } catch (error) {
      console.error('Error generating response:', error);
      addBotMessage(
        "I'm having trouble processing this right now, please try again. 😔"
      );
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Add bot message to chat
   */
  const addBotMessage = (text) => {
    const newMessage = {
      id: messages.length + 1,
      text,
      sender: 'bot',
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newMessage]);
  };

  /**
   * Handle user message submission
   */
  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!inputValue.trim()) return;

    // Add user message
    const userMessage = {
      id: messages.length + 1,
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');

    // Generate bot response
    await generateBotResponse(inputValue);
  };

  /**
   * Format timestamp
   */
  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <div className="header-content">
          <h1>🏥 HealthGuard Medical Assistant</h1>
          <p className="status">Online • Ready to help</p>
        </div>
      </div>

      <div className="chatbot-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message-wrapper ${message.sender}`}
          >
            <div className={`message ${message.sender}`}>
              <p className="message-text">{message.text}</p>
              <span className="message-time">{formatTime(message.timestamp)}</span>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message-wrapper bot">
            <div className="message bot typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chatbot-input-area">
        <form onSubmit={handleSendMessage} className="input-form">
          <div className="input-group">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Describe your symptoms or ask a health question..."
              disabled={isLoading}
              className="message-input"
            />
            <button
              type="button"
              onClick={startVoiceRecognition}
              disabled={isLoading}
              className={`voice-btn ${isListening ? 'listening' : ''}`}
              title={isListening ? 'Stop listening' : 'Start voice input'}
            >
              🎤
            </button>
            <button
              type="submit"
              disabled={isLoading || !inputValue.trim()}
              className="send-btn"
            >
              {isLoading ? '⏳' : '➤'}
            </button>
          </div>
        </form>
        <p className="disclaimer">
          ⚠️ Disclaimer: This chatbot is for informational purposes only and not a substitute for
          professional medical advice. Always consult with a licensed healthcare provider.
        </p>
      </div>
    </div>
  );
};

export default MedicalChatBot;
