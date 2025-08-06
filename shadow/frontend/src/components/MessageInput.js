import React from 'react';
import '../styles/MessageInput.css';

/**
 * Message input component for sending messages to the Shadow AI system.
 * 
 * This component provides a text input with send functionality,
 * supporting both button clicks and keyboard shortcuts.
 */
function MessageInput({ value, onChange, onSend, onKeyPress, disabled, placeholder }) {
  return (
    <div className="message-input">
      <div className="input-wrapper">
        <textarea
          value={value}
          onChange={onChange}
          onKeyPress={onKeyPress}
          disabled={disabled}
          placeholder={placeholder}
          className="message-textarea"
          rows="1"
          maxLength="2000"
        />
        <button
          onClick={onSend}
          disabled={disabled || !value.trim()}
          className="send-button"
          title="Send message (Enter)"
        >
          <svg 
            width="20" 
            height="20" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2"
          >
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22,2 15,22 11,13 2,9"></polygon>
          </svg>
        </button>
      </div>
      <div className="input-footer">
        <span className="character-count">
          {value.length}/2000
        </span>
        <span className="input-hint">
          Press Enter to send, Shift+Enter for new line
        </span>
      </div>
    </div>
  );
}

export default MessageInput;
