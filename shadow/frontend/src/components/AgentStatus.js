import React, { useState, useEffect } from 'react';
import '../styles/AgentStatus.css';

/**
 * Component for displaying agent status and system information.
 * 
 * This component shows the current status of the Shadow AI system,
 * including session information and agent availability.
 */
function AgentStatus({ sessionInfo }) {
  const [systemStatus, setSystemStatus] = useState('checking');
  const [agentInfo, setAgentInfo] = useState({
    engineer: { status: 'unknown', description: 'Technical problem-solving and design' },
    librarian: { status: 'unknown', description: 'Information retrieval and research' },
    priest: { status: 'unknown', description: 'Ethical reasoning and philosophy' }
  });

  // Check system status on component mount
  useEffect(() => {
    checkSystemStatus();
  }, []);

  /**
   * Check the status of the Shadow AI system and agents.
   */
  const checkSystemStatus = async () => {
    try {
      const response = await fetch('/api/health');
      
      if (response.ok) {
        const data = await response.json();
        setSystemStatus('online');
        
        // Update agent status if provided by the backend
        if (data.agents) {
          setAgentInfo(prev => ({
            ...prev,
            ...Object.fromEntries(
              Object.entries(data.agents).map(([key, value]) => [
                key, 
                { ...prev[key], status: value.status || 'available' }
              ])
            )
          }));
        } else {
          // Default to available if no specific status provided
          setAgentInfo(prev => 
            Object.fromEntries(
              Object.entries(prev).map(([key, value]) => [
                key, 
                { ...value, status: 'available' }
              ])
            )
          );
        }
      } else {
        setSystemStatus('offline');
      }
    } catch (error) {
      console.error('Failed to check system status:', error);
      setSystemStatus('offline');
    }
  };

  /**
   * Get status indicator styling based on status.
   */
  const getStatusClass = (status) => {
    switch (status) {
      case 'available':
      case 'online':
        return 'status-online';
      case 'busy':
        return 'status-busy';
      case 'offline':
      case 'error':
        return 'status-offline';
      default:
        return 'status-unknown';
    }
  };

  /**
   * Format session duration.
   */
  const getSessionDuration = () => {
    if (!sessionInfo?.startTime) return 'N/A';
    
    const start = new Date(sessionInfo.startTime);
    const now = new Date();
    const duration = now - start;
    
    const minutes = Math.floor(duration / 60000);
    const seconds = Math.floor((duration % 60000) / 1000);
    
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="agent-status">
      <h3>System Status</h3>
      
      {/* Overall System Status */}
      <div className="status-section">
        <div className="status-item">
          <span className="status-label">Shadow AI System</span>
          <span className={`status-indicator ${getStatusClass(systemStatus)}`}>
            {systemStatus}
          </span>
        </div>
        <button 
          onClick={checkSystemStatus}
          className="refresh-button"
          title="Refresh system status"
        >
          ↻
        </button>
      </div>

      {/* Agent Status */}
      <div className="agents-section">
        <h4>Specialized Agents</h4>
        {Object.entries(agentInfo).map(([agentName, info]) => (
          <div key={agentName} className="agent-item">
            <div className="agent-header">
              <span className="agent-name">
                {agentName.charAt(0).toUpperCase() + agentName.slice(1)}
              </span>
              <span className={`status-indicator ${getStatusClass(info.status)}`}>
                {info.status}
              </span>
            </div>
            <p className="agent-description">{info.description}</p>
          </div>
        ))}
      </div>

      {/* Session Information */}
      <div className="session-section">
        <h4>Session Info</h4>
        {sessionInfo ? (
          <div className="session-details">
            <div className="session-item">
              <span className="session-label">Duration:</span>
              <span className="session-value">{getSessionDuration()}</span>
            </div>
            <div className="session-item">
              <span className="session-label">Messages:</span>
              <span className="session-value">{sessionInfo.totalMessages}</span>
            </div>
            <div className="session-item">
              <span className="session-label">Session ID:</span>
              <span className="session-value session-id">
                {sessionInfo.sessionId.slice(-8)}
              </span>
            </div>
          </div>
        ) : (
          <p className="no-session">No active session</p>
        )}
      </div>

      {/* System Information */}
      <div className="info-section">
        <h4>About Shadow AI</h4>
        <p className="system-description">
          Multi-agent AI system with specialized cognitive agents for 
          technical, informational, and ethical reasoning.
        </p>
        <div className="version-info">
          <span>Version 0.1.0</span>
        </div>
      </div>
    </div>
  );
}

export default AgentStatus;
