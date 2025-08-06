import React, { useState, useRef, useEffect } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import '../styles/ChatInterface.css';

/**
 * Main chat interface component for the Shadow AI system.
 * 
 * This component manages the chat UI, including message display,
 * input handling, and conversation management.
 */
function ChatInterface({ conversation, isLoading, onSendMessage, onClearConversation }) {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  /**
   * Scroll to the bottom of the message list.
   */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  /**
   * Handle sending a message.
   */
  const handleSend = () => {
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  /**
   * Handle input key press events.
   */
  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  /**
   * Handle input value changes.
   */
  const handleInputChange = (event) => {
    setInputValue(event.target.value);
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>Shadow AI Conversation</h2>
        <div className="chat-controls">
          <button 
            onClick={onClearConversation}
            className="clear-button"
            disabled={isLoading || conversation.length === 0}
          >
            Clear Chat
          </button>
        </div>
      </div>

      <div className="messages-container">
        <MessageList 
          messages={conversation}
          isLoading={isLoading}
        />
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <MessageInput
          value={inputValue}
          onChange={handleInputChange}
          onSend={handleSend}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
          placeholder="Ask the Shadow AI system anything..."
        />
      </div>

      {conversation.length === 0 && (
        <div className="welcome-message">
          <h3>Welcome to Shadow AI</h3>
          <p>I'm a multi-agent AI system with specialized cognitive agents:</p>
          <ul>
            <li><strong>Engineer</strong> - Technical problem-solving, design, and system architecture</li>
            <li><strong>Librarian</strong> - Information retrieval, research, and knowledge organization</li>
            <li><strong>Priest</strong> - Ethical reasoning and philosophical perspectives</li>
          </ul>
          <p>Ask me anything, and I'll route your question to the most appropriate agent(s)!</p>
        </div>
      )}
    </div>
  );
}

export default ChatInterface;
