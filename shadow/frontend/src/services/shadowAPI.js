/**
 * Shadow AI API service for handling backend communication.
 * 
 * This service manages all API calls to the Shadow AI backend,
 * including request processing, health checks, and session management.
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

/**
 * Shadow AI API client class.
 */
class ShadowAPI {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.sessionId = null;
    this.conversationHistory = [];
  }

  /**
   * Initialize a new session.
   */
  initializeSession() {
    this.sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.conversationHistory = [];
    
    // Store session in localStorage for persistence
    localStorage.setItem('shadow_session_id', this.sessionId);
    localStorage.setItem('shadow_conversation_history', JSON.stringify(this.conversationHistory));
    
    return this.sessionId;
  }

  /**
   * Restore session from localStorage.
   */
  restoreSession() {
    const storedSessionId = localStorage.getItem('shadow_session_id');
    const storedHistory = localStorage.getItem('shadow_conversation_history');
    
    if (storedSessionId) {
      this.sessionId = storedSessionId;
    }
    
    if (storedHistory) {
      try {
        this.conversationHistory = JSON.parse(storedHistory);
      } catch (error) {
        console.error('Failed to parse stored conversation history:', error);
        this.conversationHistory = [];
      }
    }
    
    return {
      sessionId: this.sessionId,
      conversationHistory: this.conversationHistory
    };
  }

  /**
   * Clear current session and start fresh.
   */
  clearSession() {
    this.sessionId = null;
    this.conversationHistory = [];
    localStorage.removeItem('shadow_session_id');
    localStorage.removeItem('shadow_conversation_history');
    this.initializeSession();
  }

  /**
   * Add a message to the conversation history.
   */
  addMessage(message) {
    this.conversationHistory.push(message);
    
    // Keep only the last 50 messages to prevent localStorage from getting too large
    if (this.conversationHistory.length > 50) {
      this.conversationHistory = this.conversationHistory.slice(-50);
    }
    
    // Store updated history in localStorage
    localStorage.setItem('shadow_conversation_history', JSON.stringify(this.conversationHistory));
  }

  /**
   * Send a message to the Shadow AI system.
   * 
   * @param {string} message - The user's message
   * @returns {Promise<Object>} The response from the Shadow AI system
   */
  async sendMessage(message) {
    if (!this.sessionId) {
      this.initializeSession();
    }

    try {
      const response = await fetch(`${this.baseURL}/api/shadow`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: message,
          session_id: this.sessionId,
          metadata: {
            timestamp: new Date().toISOString(),
            conversation_length: this.conversationHistory.length
          }
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Add user message to history
      const userMessage = {
        id: Date.now(),
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      };
      this.addMessage(userMessage);

      // Add assistant response to history
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
        agents_used: data.agents_used || [],
        processing_time: data.processing_time,
        session_id: data.session_id
      };
      this.addMessage(assistantMessage);

      return {
        success: true,
        data: data,
        userMessage: userMessage,
        assistantMessage: assistantMessage
      };

    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message to history
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'I apologize, but I encountered an error while processing your request. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true
      };
      this.addMessage(errorMessage);

      return {
        success: false,
        error: error.message,
        errorMessage: errorMessage
      };
    }
  }

  /**
   * Check the health status of the Shadow AI system.
   * 
   * @returns {Promise<Object>} The health status response
   */
  async checkHealth() {
    try {
      const response = await fetch(`${this.baseURL}/api/health`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return {
        success: true,
        data: data
      };

    } catch (error) {
      console.error('Error checking health:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Get conversation statistics.
   */
  getConversationStats() {
    const userMessages = this.conversationHistory.filter(msg => msg.role === 'user');
    const assistantMessages = this.conversationHistory.filter(msg => msg.role === 'assistant');
    
    // Calculate total processing time
    const totalProcessingTime = assistantMessages
      .filter(msg => msg.processing_time)
      .reduce((total, msg) => total + msg.processing_time, 0);

    // Calculate agent usage
    const agentUsage = {};
    assistantMessages.forEach(msg => {
      if (msg.agents_used) {
        msg.agents_used.forEach(agent => {
          agentUsage[agent] = (agentUsage[agent] || 0) + 1;
        });
      }
    });

    return {
      totalMessages: this.conversationHistory.length,
      userMessages: userMessages.length,
      assistantMessages: assistantMessages.length,
      totalProcessingTime: Math.round(totalProcessingTime),
      averageProcessingTime: assistantMessages.length > 0 
        ? Math.round(totalProcessingTime / assistantMessages.length) 
        : 0,
      agentUsage: agentUsage,
      sessionDuration: this.sessionId ? this.getSessionDuration() : 0
    };
  }

  /**
   * Calculate session duration in minutes.
   */
  getSessionDuration() {
    if (!this.sessionId || this.conversationHistory.length === 0) {
      return 0;
    }

    const firstMessage = this.conversationHistory[0];
    const lastMessage = this.conversationHistory[this.conversationHistory.length - 1];
    
    if (!firstMessage.timestamp || !lastMessage.timestamp) {
      return 0;
    }

    const start = new Date(firstMessage.timestamp);
    const end = new Date(lastMessage.timestamp);
    const durationMs = end - start;
    
    return Math.round(durationMs / (1000 * 60)); // Convert to minutes
  }

  /**
   * Export conversation history as JSON.
   */
  exportConversation() {
    const exportData = {
      sessionId: this.sessionId,
      exportTimestamp: new Date().toISOString(),
      conversationHistory: this.conversationHistory,
      stats: this.getConversationStats()
    };

    const dataStr = JSON.stringify(exportData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `shadow-ai-conversation-${this.sessionId}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  }
}

// Create and export a singleton instance
const shadowAPI = new ShadowAPI();

export default shadowAPI;
