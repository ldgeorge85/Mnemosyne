import React from 'react';
import ReactMarkdown from 'react-markdown';
import '../styles/MessageList.css';

/**
 * Component for displaying a list of conversation messages.
 * 
 * This component renders both user and assistant messages with
 * appropriate styling and formatting.
 */
function MessageList({ messages, isLoading }) {
  /**
   * Format timestamp for display.
   */
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  /**
   * Get agent badge styling based on agents used.
   */
  const getAgentBadges = (agentsUsed) => {
    if (!agentsUsed || agentsUsed.length === 0) return null;

    const agentColors = {
      engineer: '#4CAF50',
      librarian: '#2196F3', 
      priest: '#9C27B0'
    };

    return agentsUsed.map(agent => (
      <span 
        key={agent}
        className="agent-badge"
        style={{ backgroundColor: agentColors[agent] || '#757575' }}
      >
        {agent.charAt(0).toUpperCase() + agent.slice(1)}
      </span>
    ));
  };

  return (
    <div className="message-list">
      {messages.map((message) => (
        <div key={message.id} className={`message ${message.role}`}>
          <div className="message-header">
            <span className="message-role">
              {message.role === 'user' ? 'You' : 'Shadow AI'}
            </span>
            <span className="message-time">
              {formatTime(message.timestamp)}
            </span>
          </div>

          <div className={`message-content ${message.isError ? 'error' : ''}`}>
            {message.role === 'assistant' ? (
              <ReactMarkdown>{message.content}</ReactMarkdown>
            ) : (
              <p>{message.content}</p>
            )}
          </div>

          {message.agents_used && message.agents_used.length > 0 && (
            <div className="message-footer">
              <div className="agents-used">
                <span className="agents-label">Agents:</span>
                {getAgentBadges(message.agents_used)}
              </div>
              {message.processing_time && (
                <span className="processing-time">
                  {message.processing_time}ms
                </span>
              )}
            </div>
          )}
        </div>
      ))}

      {isLoading && (
        <div className="message assistant loading">
          <div className="message-header">
            <span className="message-role">Shadow AI</span>
            <span className="message-time">Processing...</span>
          </div>
          <div className="message-content">
            <div className="typing-indicator">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default MessageList;
