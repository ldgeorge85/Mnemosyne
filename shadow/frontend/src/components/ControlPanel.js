import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ControlPanel.css';

const ControlPanel = () => {
  // State management
  const [activeTab, setActiveTab] = useState('agents');
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Agent control state
  const [agentQuery, setAgentQuery] = useState('');
  const [selectedAgents, setSelectedAgents] = useState([]);
  const [forceMode, setForceMode] = useState('single');

  // Memory control state
  const [memoryQueryType, setMemoryQueryType] = useState('history');
  const [searchTerm, setSearchTerm] = useState('');
  const [memoryResults, setMemoryResults] = useState([]);
  const [filterPatterns, setFilterPatterns] = useState('');

  // Agent config state
  const [configAgent, setConfigAgent] = useState('');
  const [configType, setConfigType] = useState('prompt');
  const [configData, setConfigData] = useState('');

  // Routing config state
  const [enableCollaboration, setEnableCollaboration] = useState(false);
  const [routingStrategy, setRoutingStrategy] = useState('keyword');

  // Available agents (from system status)
  const availableAgents = systemStatus?.agents ? Object.keys(systemStatus.agents) : [];

  // Fetch system status on mount
  useEffect(() => {
    fetchSystemStatus();
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const response = await axios.get('/api/control/status');
      setSystemStatus(response.data);
      setEnableCollaboration(response.data.routing_config?.collaboration_enabled || false);
      setRoutingStrategy(response.data.routing_config?.routing_strategy || 'keyword');
    } catch (error) {
      showMessage('error', 'Failed to fetch system status');
    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 5000);
  };

  // Agent Override Handler
  const handleAgentOverride = async () => {
    if (!agentQuery || selectedAgents.length === 0) {
      showMessage('error', 'Please enter a query and select at least one agent');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/control/agent/override', {
        query: agentQuery,
        agents: selectedAgents,
        force_single: forceMode === 'single',
        force_all: forceMode === 'all'
      });
      showMessage('success', 'Agent override successful');
      // Could display the response here
    } catch (error) {
      showMessage('error', 'Failed to override agent selection');
    }
    setLoading(false);
  };

  // Memory Query Handler
  const handleMemoryQuery = async () => {
    setLoading(true);
    try {
      const params = {
        query_type: memoryQueryType,
        limit: 20
      };
      if (searchTerm && memoryQueryType === 'search') {
        params.search_term = searchTerm;
      }

      const response = await axios.get('/api/control/memory/query', { params });
      setMemoryResults(response.data.results || []);
      showMessage('success', `Found ${response.data.count} results`);
    } catch (error) {
      showMessage('error', 'Failed to query memory');
    }
    setLoading(false);
  };

  // Memory Management Handlers
  const handleClearMemory = async (clearType) => {
    if (!window.confirm(`Are you sure you want to clear ${clearType} memory?`)) {
      return;
    }

    setLoading(true);
    try {
      const filters = clearType === 'all' ? { all: true } : { [clearType]: true };
      await axios.post('/api/control/memory/manage', {
        operation: 'clear',
        filters
      });
      showMessage('success', `${clearType} memory cleared`);
      if (clearType === 'history' || clearType === 'all') {
        setMemoryResults([]);
      }
    } catch (error) {
      showMessage('error', 'Failed to clear memory');
    }
    setLoading(false);
  };

  const handleFilterMemory = async () => {
    if (!filterPatterns) {
      showMessage('error', 'Please enter patterns to filter');
      return;
    }

    setLoading(true);
    try {
      const patterns = filterPatterns.split(',').map(p => p.trim());
      const response = await axios.post('/api/control/memory/manage', {
        operation: 'filter',
        filters: { patterns }
      });
      showMessage('success', `Removed ${response.data.removed_count} items`);
      handleMemoryQuery(); // Refresh results
    } catch (error) {
      showMessage('error', 'Failed to filter memory');
    }
    setLoading(false);
  };

  // Agent Configuration Handler
  const handleAgentConfig = async () => {
    if (!configAgent || !configData) {
      showMessage('error', 'Please select an agent and provide configuration data');
      return;
    }

    setLoading(true);
    try {
      let parsedData;
      try {
        parsedData = JSON.parse(configData);
      } catch (e) {
        showMessage('error', 'Invalid JSON configuration data');
        setLoading(false);
        return;
      }

      await axios.post('/api/control/agent/config', {
        agent_name: configAgent,
        config_type: configType,
        config_data: parsedData,
        persist: true
      });
      showMessage('success', `${configAgent} ${configType} updated`);
    } catch (error) {
      showMessage('error', 'Failed to update agent configuration');
    }
    setLoading(false);
  };

  // Routing Configuration Handler
  const handleRoutingConfig = async () => {
    setLoading(true);
    try {
      await axios.post('/api/control/routing/config', {
        enable_collaboration: enableCollaboration,
        enable_multi_agent: true,
        routing_strategy: routingStrategy
      });
      showMessage('success', 'Routing configuration updated');
      fetchSystemStatus(); // Refresh status
    } catch (error) {
      showMessage('error', 'Failed to update routing configuration');
    }
    setLoading(false);
  };

  return (
    <div className="control-panel">
      <h2>Shadow AI Control Panel</h2>
      
      {/* Message Display */}
      {message.text && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="tab-nav">
        <button 
          className={activeTab === 'agents' ? 'active' : ''} 
          onClick={() => setActiveTab('agents')}
        >
          Agent Control
        </button>
        <button 
          className={activeTab === 'memory' ? 'active' : ''} 
          onClick={() => setActiveTab('memory')}
        >
          Memory Management
        </button>
        <button 
          className={activeTab === 'config' ? 'active' : ''} 
          onClick={() => setActiveTab('config')}
        >
          Configuration
        </button>
        <button 
          className={activeTab === 'status' ? 'active' : ''} 
          onClick={() => setActiveTab('status')}
        >
          System Status
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {/* Agent Control Tab */}
        {activeTab === 'agents' && (
          <div className="agent-control">
            <h3>Force Agent Selection</h3>
            <div className="form-group">
              <label>Query:</label>
              <input
                type="text"
                value={agentQuery}
                onChange={(e) => setAgentQuery(e.target.value)}
                placeholder="Enter your query..."
                className="full-width"
              />
            </div>
            
            <div className="form-group">
              <label>Select Agents:</label>
              <div className="agent-checkboxes">
                {availableAgents.map(agent => (
                  <label key={agent}>
                    <input
                      type="checkbox"
                      checked={selectedAgents.includes(agent)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedAgents([...selectedAgents, agent]);
                        } else {
                          setSelectedAgents(selectedAgents.filter(a => a !== agent));
                        }
                      }}
                    />
                    {agent}
                  </label>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label>Force Mode:</label>
              <select value={forceMode} onChange={(e) => setForceMode(e.target.value)}>
                <option value="single">Single Agent (First Selected)</option>
                <option value="all">All Selected Agents</option>
                <option value="normal">Normal (Selected Pool)</option>
              </select>
            </div>

            <button 
              onClick={handleAgentOverride} 
              disabled={loading}
              className="primary-button"
            >
              Override Agent Selection
            </button>
          </div>
        )}

        {/* Memory Management Tab */}
        {activeTab === 'memory' && (
          <div className="memory-management">
            <h3>Memory Query</h3>
            <div className="form-group">
              <label>Query Type:</label>
              <select 
                value={memoryQueryType} 
                onChange={(e) => setMemoryQueryType(e.target.value)}
              >
                <option value="history">Conversation History</option>
                <option value="documents">Documents</option>
                <option value="search">Semantic Search</option>
                <option value="entities">Entities</option>
              </select>
            </div>

            {memoryQueryType === 'search' && (
              <div className="form-group">
                <label>Search Term:</label>
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Enter search term..."
                />
              </div>
            )}

            <button onClick={handleMemoryQuery} disabled={loading}>
              Query Memory
            </button>

            {/* Memory Results */}
            {memoryResults.length > 0 && (
              <div className="memory-results">
                <h4>Results:</h4>
                <pre>{JSON.stringify(memoryResults, null, 2)}</pre>
              </div>
            )}

            <h3>Memory Operations</h3>
            <div className="memory-operations">
              <button onClick={() => handleClearMemory('history')} disabled={loading}>
                Clear History
              </button>
              <button onClick={() => handleClearMemory('documents')} disabled={loading}>
                Clear Documents
              </button>
              <button onClick={() => handleClearMemory('all')} disabled={loading} className="danger">
                Clear All Memory
              </button>
            </div>

            <h3>Filter Memory</h3>
            <div className="form-group">
              <label>Filter Patterns (comma-separated):</label>
              <input
                type="text"
                value={filterPatterns}
                onChange={(e) => setFilterPatterns(e.target.value)}
                placeholder="test message, error generating, ..."
                className="full-width"
              />
            </div>
            <button onClick={handleFilterMemory} disabled={loading}>
              Filter Out Patterns
            </button>
          </div>
        )}

        {/* Configuration Tab */}
        {activeTab === 'config' && (
          <div className="configuration">
            <h3>Agent Configuration</h3>
            <div className="form-group">
              <label>Agent:</label>
              <select 
                value={configAgent} 
                onChange={(e) => setConfigAgent(e.target.value)}
              >
                <option value="">Select Agent</option>
                {availableAgents.map(agent => (
                  <option key={agent} value={agent}>{agent}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Configuration Type:</label>
              <select 
                value={configType} 
                onChange={(e) => setConfigType(e.target.value)}
              >
                <option value="prompt">Prompts</option>
                <option value="keywords">Keywords</option>
                <option value="parameters">Parameters</option>
              </select>
            </div>

            <div className="form-group">
              <label>Configuration Data (JSON):</label>
              <textarea
                value={configData}
                onChange={(e) => setConfigData(e.target.value)}
                placeholder={configType === 'keywords' ? 
                  '{"add": ["new", "keywords"], "remove": ["old"]}' :
                  '{"system_prompt": "New prompt..."}'
                }
                rows={6}
                className="full-width"
              />
            </div>

            <button onClick={handleAgentConfig} disabled={loading}>
              Update Configuration
            </button>

            <h3>Routing Configuration</h3>
            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={enableCollaboration}
                  onChange={(e) => setEnableCollaboration(e.target.checked)}
                />
                Enable Agent Collaboration
              </label>
            </div>

            <div className="form-group">
              <label>Routing Strategy:</label>
              <select 
                value={routingStrategy} 
                onChange={(e) => setRoutingStrategy(e.target.value)}
              >
                <option value="keyword">Keyword-based</option>
                <option value="semantic">Semantic Similarity</option>
                <option value="manual">Manual Selection</option>
              </select>
            </div>

            <button onClick={handleRoutingConfig} disabled={loading}>
              Update Routing Configuration
            </button>
          </div>
        )}

        {/* System Status Tab */}
        {activeTab === 'status' && systemStatus && (
          <div className="system-status">
            <h3>System Status</h3>
            <button onClick={fetchSystemStatus} disabled={loading}>
              Refresh Status
            </button>

            <div className="status-section">
              <h4>Agents</h4>
              <table>
                <thead>
                  <tr>
                    <th>Agent</th>
                    <th>Status</th>
                    <th>Keywords</th>
                    <th>Usage Count</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(systemStatus.agents).map(([name, info]) => (
                    <tr key={name}>
                      <td>{name}</td>
                      <td>{info.active ? '✓ Active' : '✗ Inactive'}</td>
                      <td>{info.keywords_count}</td>
                      <td>{info.usage_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="status-section">
              <h4>Memory Status</h4>
              <p>History Length: {systemStatus.memory_status.conversation_history_length} / {systemStatus.memory_status.max_history_length}</p>
              <p>Vector Store: {systemStatus.memory_status.stores.vector}</p>
              <p>Document Store: {systemStatus.memory_status.stores.document}</p>
              <p>Relational Store: {systemStatus.memory_status.stores.relational}</p>
            </div>

            <div className="status-section">
              <h4>Routing Configuration</h4>
              <p>Collaboration: {systemStatus.routing_config.collaboration_enabled ? 'Enabled' : 'Disabled'}</p>
              <p>Strategy: {systemStatus.routing_config.routing_strategy}</p>
              <p>Custom Rules: {systemStatus.routing_config.custom_rules_active ? 'Active' : 'None'}</p>
            </div>

            <div className="status-section">
              <h4>Performance Stats</h4>
              <pre>{JSON.stringify(systemStatus.performance_stats, null, 2)}</pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ControlPanel;
