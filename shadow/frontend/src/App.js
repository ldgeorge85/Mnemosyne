import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import AgentStatus from './components/AgentStatus';
import ControlPanel from './components/ControlPanel';
import DarkModeToggle from './components/DarkModeToggle';
import { ThemeProvider } from './contexts/ThemeContext';
import shadowAPI from './services/shadowAPI';
import './styles/App.css';

/**
 * Main application component for the Shadow AI system.
 * 
 * This component manages the overall application state and provides
 * the main user interface for interacting with the Shadow AI agents.
 */
function App() {
  const [conversation, setConversation] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionInfo, setSessionInfo] = useState(null);
  const [systemStatus, setSystemStatus] = useState('initializing');
  const [showControlPanel, setShowControlPanel] = useState(false);

  // Initialize session on component mount
  useEffect(() => {
    initializeSession();
    checkSystemHealth();
  }, []);

  /**
   * Initialize or restore a conversation session with the Shadow system.
   */
  const initializeSession = async () => {
    try {
      // Try to restore existing session first
      const restored = shadowAPI.restoreSession();
      
      if (restored.sessionId && restored.conversationHistory.length > 0) {
        // Restore existing session
        setConversation(restored.conversationHistory);
        setSessionInfo({
          sessionId: restored.sessionId,
          startTime: restored.conversationHistory[0]?.timestamp || new Date().toISOString(),
          totalMessages: restored.conversationHistory.filter(msg => msg.role === 'user').length,
          isRestored: true
        });
      } else {
        // Create new session
        const sessionId = shadowAPI.initializeSession();
        setSessionInfo({
          sessionId: sessionId,
          startTime: new Date().toISOString(),
          totalMessages: 0,
          isRestored: false
        });
      }
    } catch (error) {
      console.error('Failed to initialize session:', error);
      // Fallback to basic session
      setSessionInfo({
        sessionId: `fallback_${Date.now()}`,
        startTime: new Date().toISOString(),
        totalMessages: 0,
        isRestored: false
      });
    }
  };

  /**
   * Check the health status of the Shadow AI system.
   */
  const checkSystemHealth = async () => {
    const result = await shadowAPI.checkHealth();
    if (result.success) {
      setSystemStatus('online');
    } else {
      setSystemStatus('offline');
      console.error('System health check failed:', result.error);
    }
  };

  /**
   * Handle sending a new message to the Shadow system.
   * 
   * @param {string} message - The user's message
   */
  const handleSendMessage = async (message) => {
    if (!message.trim() || isLoading) return;

    setIsLoading(true);

    try {
      const result = await shadowAPI.sendMessage(message);

      if (result.success) {
        // Update conversation with both user and assistant messages
        setConversation(shadowAPI.conversationHistory);

        // Update session info
        setSessionInfo(prev => ({
          ...prev,
          totalMessages: prev.totalMessages + 1,
          lastActivity: new Date().toISOString()
        }));
      } else {
        // Handle error case
        setConversation(shadowAPI.conversationHistory);
        console.error('Failed to send message:', result.error);
      }

    } catch (error) {
      console.error('Unexpected error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Clear the current conversation and start fresh.
   */
  const handleClearConversation = () => {
    shadowAPI.clearSession();
    setConversation([]);
    
    // Create new session info
    const newSessionId = shadowAPI.sessionId;
    setSessionInfo({
      sessionId: newSessionId,
      startTime: new Date().toISOString(),
      totalMessages: 0,
      isRestored: false
    });
  };

  /**
   * Export the current conversation.
   */
  const handleExportConversation = () => {
    if (conversation.length === 0) {
      alert('No conversation to export.');
      return;
    }
    
    try {
      shadowAPI.exportConversation();
    } catch (error) {
      console.error('Failed to export conversation:', error);
      alert('Failed to export conversation. Please try again.');
    }
  };

  /**
   * Get conversation statistics for display.
   */
  const getConversationStats = () => {
    return shadowAPI.getConversationStats();
  };

  return (
    <ThemeProvider>
      <div className="app">
        <header className="app-header">
          <h1>Shadow AI Agent System</h1>
          <p>Intelligent multi-agent system with specialized cognitive agents</p>
          <div className="dark-mode-toggle-header">
            <DarkModeToggle />
          </div>
          <div className="system-status">
            <span className={`status-indicator ${systemStatus}`}>
              {systemStatus === 'online' ? '🟢' : systemStatus === 'offline' ? '🔴' : '🟡'} 
              System {systemStatus}
            </span>
          </div>
          <button 
            className="control-toggle"
            onClick={() => setShowControlPanel(!showControlPanel)}
          >
            {showControlPanel ? 'Hide' : 'Show'} Control Panel
          </button>
        </header>

        {showControlPanel && <ControlPanel />}

        <main className="app-main">
          <div className="chat-container">
            <ChatInterface 
              conversation={conversation}
              isLoading={isLoading}
              onSendMessage={handleSendMessage}
              onClearConversation={handleClearConversation}
              onExportConversation={handleExportConversation}
              conversationStats={getConversationStats()}
            />
          </div>

          <aside className="sidebar">
            <AgentStatus 
              sessionInfo={sessionInfo}
              systemStatus={systemStatus}
              onRefreshHealth={checkSystemHealth}
              conversationStats={getConversationStats()}
            />
          </aside>
        </main>

        <footer className="app-footer">
          <p>Powered by Shadow AI • Multi-Agent Intelligence Platform</p>
          {sessionInfo && (
            <p className="session-info">
              Session: {sessionInfo.sessionId.slice(-8)} 
              {sessionInfo.isRestored && <span className="restored-badge"> (Restored)</span>}
            </p>
          )}
        </footer>
      </div>
    </ThemeProvider>
  );
}

export default App;
