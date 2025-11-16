/**
 * MedicalChatBot - Testing & Debugging Configuration
 * 
 * This file contains mock data and configurations for testing the chatbot
 * without making actual API calls.
 */

// ============================================
// Mock Disease Predictions
// ============================================
export const mockDiseases = {
  'fever': {
    label: 'Viral Infection',
    score: 0.92,
    description: 'Likely a viral fever, common in cold and flu'
  },
  'chest pain': {
    label: 'Cardiac Condition',
    score: 0.88,
    description: 'Requires immediate medical attention',
    severity: 'severe'
  },
  'headache': {
    label: 'Migraine',
    score: 0.85,
    description: 'Common tension or migraine headache'
  },
  'cough': {
    label: 'Respiratory Infection',
    score: 0.80,
    description: 'Could be bronchitis or common cold'
  },
  'nausea': {
    label: 'Gastric Issue',
    score: 0.75,
    description: 'Possibly food poisoning or stomach infection'
  }
};

// ============================================
// Mock Medicine Data
// ============================================
export const mockMedicines = {
  'Viral Infection': [
    {
      name: 'Paracetamol (Acetaminophen)',
      usage: 'Used for pain relief and fever reduction. Typical dose: 500-1000mg every 4-6 hours',
      warnings: 'Do not exceed 4000mg per day. Consult if liver disease present',
      manufacturer: 'Various'
    },
    {
      name: 'Ibuprofen',
      usage: 'Anti-inflammatory pain reliever for fever and aches. Typical dose: 200-400mg every 4-6 hours',
      warnings: 'May cause stomach upset. Take with food. Not recommended if ulcer history',
      manufacturer: 'Various'
    },
    {
      name: 'Aspirin',
      usage: 'For fever and general pain relief in adults. Typical dose: 500mg every 4-6 hours',
      warnings: 'Do not give to children. May cause stomach irritation',
      manufacturer: 'Various'
    }
  ],
  'Migraine': [
    {
      name: 'Sumatriptan',
      usage: 'Specific migraine treatment. Typical dose: 25-100mg as needed',
      warnings: 'Only use for migraines, not regular headaches. May cause drowsiness',
      manufacturer: 'Glaxo SmithKline'
    },
    {
      name: 'Ibuprofen',
      usage: 'Standard pain relief for migraines. Typical dose: 400-600mg',
      warnings: 'Best taken early in migraine onset. Take with food',
      manufacturer: 'Various'
    }
  ],
  'Respiratory Infection': [
    {
      name: 'Dextromethorphan',
      usage: 'Cough suppressant. Typical dose: 10-20mg every 4-6 hours',
      warnings: 'Do not use if taking antidepressants. May cause drowsiness',
      manufacturer: 'Various'
    },
    {
      name: 'Guaifenesin',
      usage: 'Expectorant to thin mucus. Typical dose: 200-400mg every 4 hours',
      warnings: 'Generally safe. Drink plenty of water',
      manufacturer: 'Various'
    }
  ]
};

// ============================================
// Test Messages for Development
// ============================================
export const testMessages = [
  {
    user: 'I have a high fever and severe chills',
    expectedSeverity: 'moderate',
    expectedDisease: 'Viral Infection'
  },
  {
    user: 'I have a sudden chest pain and difficulty breathing',
    expectedSeverity: 'severe',
    expectedDisease: 'Cardiac Condition'
  },
  {
    user: 'I have a mild headache and stiffness in neck',
    expectedSeverity: 'moderate',
    expectedDisease: 'Headache'
  },
  {
    user: 'I have a persistent dry cough for 2 weeks',
    expectedSeverity: 'moderate',
    expectedDisease: 'Respiratory Infection'
  },
  {
    user: 'I feel nauseous after eating',
    expectedSeverity: 'mild',
    expectedDisease: 'Gastric Issue'
  }
];

// ============================================
// Severity Keywords Configuration
// ============================================
export const severityConfig = {
  severe: {
    keywords: [
      'chest pain',
      'breathing difficulty',
      'unconscious',
      'severe bleeding',
      'choking',
      'emergency',
      'critical',
      'collapsed',
      'fracture',
      'severe burn',
      'poisoning',
      'overdose',
      'allergic reaction',
      'anaphylaxis'
    ],
    message: '⚠️ URGENT: You should seek immediate medical attention at a hospital or call emergency services. Your symptoms suggest a serious condition.',
    actions: ['Call 911', 'Visit ER', 'Call Ambulance']
  },
  moderate: {
    keywords: [
      'persistent fever',
      'infection',
      'worsening symptoms',
      'severe pain',
      'vomiting',
      'dizziness',
      'confusion',
      'persistent cough',
      'difficult breathing',
      'severe headache',
      'abdominal pain'
    ],
    message: '📋 Important: Monitor your condition closely and consult a doctor soon. If symptoms worsen, seek immediate medical attention.',
    actions: ['See Doctor', 'Call Clinic', 'Wait & Monitor']
  },
  mild: {
    keywords: [
      'mild fever',
      'slight headache',
      'minor cough',
      'tired',
      'fatigue',
      'mild nausea',
      'slight ache'
    ],
    message: '✅ For now: Rest well, stay hydrated, and take basic medicines. If symptoms persist beyond 3 days, consult a healthcare provider.',
    actions: ['Rest', 'Hydrate', 'Take Medicine', 'Monitor']
  }
};

// ============================================
// API Configuration for Testing
// ============================================
export const apiConfig = {
  huggingface: {
    baseUrl: 'https://api-inference.huggingface.co',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 2000,
    models: {
      'bert': 'bert-base-uncased',
      'biobert': 'dmis-lab/biobert-base-cased-v1.1',
      'medical-qa': 'deepset/roberta-base-squad2'
    }
  },
  fda: {
    baseUrl: 'https://api.fda.gov',
    drugLabel: '/drug/label.json',
    timeout: 15000,
    rateLimit: 240, // requests per minute
    retryAttempts: 2
  }
};

// ============================================
// Mock Response Helper for Testing
// ============================================
export const mockApiResponses = {
  diseasePrediction: (symptom) => {
    const disease = mockDiseases[symptom.toLowerCase()] || {
      label: 'General Illness',
      score: 0.5,
      description: 'Unclear symptoms, please provide more details'
    };
    return Promise.resolve([disease]);
  },

  medicineInfo: (disease) => {
    const medicines = mockMedicines[disease] || [];
    return Promise.resolve({
      data: {
        results: medicines
      }
    });
  },

  error: (message) => {
    return Promise.reject(new Error(message));
  }
};

// ============================================
// Local Storage Mock for Persistent Data
// ============================================
export const chatHistoryStorage = {
  save: (messages) => {
    try {
      localStorage.setItem('chatbot_history', JSON.stringify(messages));
      return true;
    } catch (e) {
      console.error('Failed to save chat history:', e);
      return false;
    }
  },

  load: () => {
    try {
      const history = localStorage.getItem('chatbot_history');
      return history ? JSON.parse(history) : [];
    } catch (e) {
      console.error('Failed to load chat history:', e);
      return [];
    }
  },

  clear: () => {
    try {
      localStorage.removeItem('chatbot_history');
      return true;
    } catch (e) {
      console.error('Failed to clear chat history:', e);
      return false;
    }
  }
};

// ============================================
// Debug Logging Configuration
// ============================================
export const debugConfig = {
  logApiCalls: true,
  logMessages: true,
  logErrors: true,
  logPerformance: true,
  logVoiceInput: true
};

export const logger = {
  apiCall: (method, url, data) => {
    if (debugConfig.logApiCalls) {
      console.group(`🔗 API Call: ${method} ${url}`);
      console.log('Data:', data);
      console.groupEnd();
    }
  },

  message: (sender, text) => {
    if (debugConfig.logMessages) {
      console.log(`💬 ${sender}: ${text}`);
    }
  },

  error: (source, error) => {
    if (debugConfig.logErrors) {
      console.error(`❌ Error in ${source}:`, error);
    }
  },

  performance: (operation, duration) => {
    if (debugConfig.logPerformance) {
      console.log(`⏱️ ${operation} took ${duration}ms`);
    }
  },

  voice: (status) => {
    if (debugConfig.logVoiceInput) {
      console.log(`🎤 Voice: ${status}`);
    }
  }
};

// ============================================
// Testing Helper Functions
// ============================================
export const testHelpers = {
  /**
   * Simulate user message
   */
  simulateUserMessage: (text) => {
    return {
      id: Math.random(),
      text,
      sender: 'user',
      timestamp: new Date()
    };
  },

  /**
   * Simulate bot response
   */
  simulateBotResponse: (text) => {
    return {
      id: Math.random(),
      text,
      sender: 'bot',
      timestamp: new Date()
    };
  },

  /**
   * Get random test message
   */
  getRandomTestMessage: () => {
    return testMessages[Math.floor(Math.random() * testMessages.length)];
  },

  /**
   * Simulate API delay
   */
  delay: (ms = 1000) => {
    return new Promise(resolve => setTimeout(resolve, ms));
  },

  /**
   * Test severity detection
   */
  testSeverityDetection: (message) => {
    for (const [level, config] of Object.entries(severityConfig)) {
      if (config.keywords.some(kw => message.toLowerCase().includes(kw))) {
        return level;
      }
    }
    return 'unknown';
  }
};

// ============================================
// Component Testing Configuration
// ============================================
export const componentTestConfig = {
  // Initial messages for testing
  initialMessages: [
    {
      id: 1,
      text: "Hello! I'm your HealthGuard medical assistant.",
      sender: 'bot',
      timestamp: new Date()
    }
  ],

  // Mock environment variables
  mockEnv: {
    VITE_HF_API_KEY: 'hf_test_key_123456',
    VITE_OPENAI_KEY: 'sk_test_key_123456'
  },

  // Testing timeouts
  timeouts: {
    apiCall: 5000,
    voiceInput: 10000,
    messageDisplay: 2000
  }
};

// ============================================
// Export All for Easy Access
// ============================================
export default {
  mockDiseases,
  mockMedicines,
  testMessages,
  severityConfig,
  apiConfig,
  mockApiResponses,
  chatHistoryStorage,
  debugConfig,
  logger,
  testHelpers,
  componentTestConfig
};
