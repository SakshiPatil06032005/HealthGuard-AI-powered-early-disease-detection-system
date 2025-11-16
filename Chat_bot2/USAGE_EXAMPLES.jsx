/**
 * MedicalChatBot Component Usage Examples
 * 
 * This file demonstrates various ways to use and integrate the MedicalChatBot component
 * into your HealthGuard application.
 */

// ============================================
// Example 1: Basic Integration
// ============================================
import React, { useState, useContext, useEffect } from 'react';
import MedicalChatBot from './components/MedicalChatBot';

export function App() {
  return (
    <div className="app">
      <MedicalChatBot />
    </div>
  );
}
// ============================================
// Example 2: With Layout & Navigation
// ============================================
export function HealthGuardApp() {
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>HealthGuard - Your Medical Assistant</h1>
        <nav>
          <a href="/dashboard">Dashboard</a>
          <a href="/appointments">Appointments</a>
          <a href="/chatbot">Chat</a>
        </nav>
      </header>
      
      <main className="app-main">
        <aside className="sidebar">
          {/* Your sidebar content */}
        </aside>
        
        <section className="chatbot-section">
          <MedicalChatBot />
        </section>
      </main>
    </div>
  );
}


// ============================================
// Example 3: With State Management (Redux/Context)
// ============================================
export function ChatbotWithAuth() {
  const { user, isAuthenticated } = useContext(AuthContext);

  if (!isAuthenticated) {
    return <div>Please log in to access the medical chatbot.</div>;
  }

  return (
    <div className="authenticated-chatbot">
      <div className="user-info">
        <p>Welcome, {user.name}!</p>
      </div>
      <MedicalChatBot />
    </div>
  );
}


// ============================================
// Example 4: As a Modal/Pop-up
// ============================================
export function ChatbotModal() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button onClick={() => setIsOpen(true)} className="chatbot-toggle">
        💬 Chat with Assistant
      </button>

      {isOpen && (
        <div className="modal-overlay" onClick={() => setIsOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button 
              className="close-btn" 
              onClick={() => setIsOpen(false)}
            >
              ✕
            </button>
            <MedicalChatBot />
          </div>
        </div>
      )}
    </>
  );
}


// ============================================
// Example 5: Full-Page Chat Interface
// ============================================
export function ChatbotPage() {
  return (
    <div className="chatbot-page">
      <MedicalChatBot />
    </div>
  );
}


// ============================================
// Example 6: With Custom CSS Theme
// ============================================
export function ThemedChatbot() {
  return (
    <div style={{ 
      '--primary-color': '#667eea',
      '--secondary-color': '#764ba2'
    }}>
      <MedicalChatBot />
    </div>
  );
}


// ============================================
// Example 7: Using in a Dashboard
// ============================================
export function HealthDashboard() {
  return (
    <div className="dashboard">
      <div className="dashboard-grid">
        {/* Other dashboard widgets */}
        <div className="widget health-stats">
          {/* Health statistics */}
        </div>

        <div className="widget appointments">
          {/* Upcoming appointments */}
        </div>

        <div className="widget chatbot">
          <div className="widget-header">
            <h3>Medical Assistant</h3>
          </div>
          <div className="widget-body">
            <MedicalChatBot />
          </div>
        </div>
      </div>
    </div>
  );
}


// ============================================
// Example 8: Environment Variable Configuration
// ============================================

/**
 * VITE PROJECT (.env file)
 */
// .env
// VITE_HF_API_KEY=hf_xxxxx
// VITE_OPENAI_KEY=sk_xxxxx

/**
 * CREATE REACT APP (.env file)
 */
// .env
// REACT_APP_HF_API_KEY=hf_xxxxx
// REACT_APP_OPENAI_KEY=sk_xxxxx

/**
 * In component:
 * For Vite: import.meta.env.VITE_HF_API_KEY
 * For CRA: process.env.REACT_APP_HF_API_KEY
 */


// ============================================
// Example 9: Logging & Analytics Integration
// ============================================
export function ChatbotWithAnalytics() {
  const trackChatbotInteraction = (action, data) => {
    console.log(`Analytics: ${action}`, data);
    // Send to analytics service
    // analytics.track(action, data);
  };

  React.useEffect(() => {
    trackChatbotInteraction('chatbot_opened', {
      timestamp: new Date(),
      user_id: 'user_123'
    });

    return () => {
      trackChatbotInteraction('chatbot_closed', {
        timestamp: new Date()
      });
    };
  }, []);

  return <MedicalChatBot />;
}


// ============================================
// Example 10: Error Boundary Wrapper
// ============================================
export class ChatbotErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Chatbot error:', error, errorInfo);
    // Log to error reporting service
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-fallback">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false })}>
            Try Again
          </button>
        </div>
      );
    }

    return <MedicalChatBot />;
  }
}


// ============================================
// Example 11: CSS Customization
// ============================================

/**
 * Override styles in your app's main CSS file:
 * 
 * :root {
 *   --chatbot-primary: #667eea;
 *   --chatbot-secondary: #764ba2;
 *   --chatbot-message-user-bg: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
 *   --chatbot-message-bot-bg: #e9ecef;
 * }
 * 
 * .chatbot-header {
 *   background: var(--chatbot-primary);
 * }
 * 
 * .message.user {
 *   background: var(--chatbot-message-user-bg);
 * }
 */


// ============================================
// Example 12: Accessibility Features
// ============================================
export function AccessibleChatbot() {
  return (
    <div 
      role="region" 
      aria-label="Medical Assistant Chat"
      aria-live="polite"
    >
      <MedicalChatBot />
    </div>
  );
}


// ============================================
// Tips & Best Practices
// ============================================

/**
 * 1. ENVIRONMENT VARIABLES
 *    - Never hardcode API keys
 *    - Use .env files for local development
 *    - Add .env to .gitignore
 *    - Use different keys for dev/prod
 * 
 * 2. ERROR HANDLING
 *    - Wrap component in Error Boundary
 *    - Check browser console for API errors
 *    - Implement retry logic for failed requests
 *    - Show user-friendly error messages
 * 
 * 3. PERFORMANCE
 *    - Implement response caching
 *    - Use React.memo for optimization
 *    - Lazy load heavy components
 *    - Monitor API response times
 * 
 * 4. ACCESSIBILITY
 *    - Use semantic HTML
 *    - Add ARIA labels
 *    - Test with screen readers
 *    - Ensure keyboard navigation works
 * 
 * 5. TESTING
 *    - Mock API responses for unit tests
 *    - Test with different screen sizes
 *    - Verify all features work in target browsers
 *    - Test error states and edge cases
 * 
 * 6. MOBILE OPTIMIZATION
 *    - Component is fully responsive
 *    - Test touch interactions
 *    - Optimize for slower connections
 *    - Minimize data usage
 * 
 * 7. SECURITY
 *    - Validate user inputs
 *    - Sanitize displayed content
 *    - Use HTTPS in production
 *    - Implement rate limiting on APIs
 */


export {
  App,
  HealthGuardApp,
  ChatbotWithAuth,
  ChatbotModal,
  ChatbotPage,
  ThemedChatbot,
  HealthDashboard,
  ChatbotWithAnalytics,
  ChatbotErrorBoundary,
  AccessibleChatbot
};
