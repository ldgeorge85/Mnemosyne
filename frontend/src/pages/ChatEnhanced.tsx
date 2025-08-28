/**
 * Enhanced Chat Page with Conversation Tracking and SSE Support
 * 
 * Features:
 * - Conversation persistence (local storage)
 * - Streaming support with SSE
 * - New conversation creation
 * - Chat history tracking
 */

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { countMessageTokens, truncateMessages, checkTokenLimit } from '@/utils/tokenCounter';
import ToolPalette from '@/components/ToolPalette';
import { 
  Send, 
  Plus, 
  Loader2,
  Sparkles,
  Shield,
  Brain,
  Users,
  Eye,
  Trash2,
  Wrench
} from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  streaming?: boolean;
  personaMode?: string;
  reasoning?: string;  // Store reasoning for transparency
}

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
  persona_mode?: string;
}

// Persona modes configuration
const PERSONA_MODES = {
  confidant: { 
    name: 'Confidant', 
    icon: Shield, 
    color: 'bg-blue-100 text-blue-800',
    description: 'Deep listener with empathic presence'
  },
  mentor: { 
    name: 'Mentor', 
    icon: Brain, 
    color: 'bg-green-100 text-green-800',
    description: 'Guide for skill development'
  },
  mediator: { 
    name: 'Mediator', 
    icon: Users, 
    color: 'bg-purple-100 text-purple-800',
    description: 'Navigate conflicts with neutrality'
  },
  guardian: { 
    name: 'Guardian', 
    icon: Shield, 
    color: 'bg-orange-100 text-orange-800',
    description: 'Protector of wellbeing'
  },
  mirror: { 
    name: 'Mirror', 
    icon: Eye, 
    color: 'bg-cyan-100 text-cyan-800',
    description: 'Reflect patterns without judgment'
  }
};

const ChatEnhanced: React.FC = () => {
  // Load conversations from localStorage
  const loadConversations = (): Conversation[] => {
    const stored = localStorage.getItem('mnemosyne_conversations');
    if (!stored) return [];
    try {
      const parsed = JSON.parse(stored);
      return parsed.map((conv: any) => ({
        ...conv,
        createdAt: new Date(conv.createdAt),
        updatedAt: new Date(conv.updatedAt),
        messages: conv.messages.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }))
      }));
    } catch {
      return [];
    }
  };

  // Save conversations to localStorage
  const saveConversations = (conversations: Conversation[]) => {
    localStorage.setItem('mnemosyne_conversations', JSON.stringify(conversations));
  };

  const [conversations, setConversations] = useState<Conversation[]>(loadConversations());
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState<string>('');
  const [personaMode, setPersonaMode] = useState<string>('confidant');
  const [enableStreaming, setEnableStreaming] = useState(true);
  const [useAgentic, setUseAgentic] = useState(true);  // Toggle for agentic mode - defaulted to ON
  const [agenticStatus, setAgenticStatus] = useState<string>('');  // Status messages
  const [agenticReasoning, setAgenticReasoning] = useState<string>('');
  const [streamingPersonaMode, setStreamingPersonaMode] = useState<string>('');  // Reasoning display
  const [agenticSuggestions, setAgenticSuggestions] = useState<any[]>([]);  // Suggestions
  const [selectedTools, setSelectedTools] = useState<string[]>([]);  // Selected tools from palette
  const [showToolPalette, setShowToolPalette] = useState(false);  // Tool palette visibility
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Get current conversation
  const currentConversation = conversations.find(c => c.id === currentConversationId);
  const messages = currentConversation?.messages || [];

  // Save conversations when they change
  useEffect(() => {
    if (conversations.length > 0) {
      saveConversations(conversations);
    }
  }, [conversations]);

  // Update sidebar with conversation history
  useEffect(() => {
    // Dispatch custom event for sidebar to listen to
    window.dispatchEvent(new CustomEvent('conversationsUpdated', { 
      detail: conversations 
    }));
  }, [conversations]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage]);

  // Auto-focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Listen for conversation events from sidebar
  useEffect(() => {
    const handleLoadConversation = (event: CustomEvent) => {
      const conversationId = event.detail;
      setCurrentConversationId(conversationId);
    };

    const handleCreateNew = () => {
      createNewConversation();
    };

    window.addEventListener('loadConversation', handleLoadConversation as EventListener);
    window.addEventListener('createNewConversation', handleCreateNew);
    
    return () => {
      window.removeEventListener('loadConversation', handleLoadConversation as EventListener);
      window.removeEventListener('createNewConversation', handleCreateNew);
    };
  }, [personaMode]); // Add personaMode as dependency since createNewConversation uses it

  // Start with fresh chat on page load if no conversation selected
  useEffect(() => {
    if (!currentConversationId) {
      createNewConversation();
    }
  }, []);

  // Delete conversation
  const deleteConversation = (conversationId: string) => {
    if (!confirm('Are you sure you want to delete this conversation?')) return;
    
    setConversations(prev => prev.filter(c => c.id !== conversationId));
    
    // If we deleted the current conversation, create a new one
    if (conversationId === currentConversationId) {
      createNewConversation();
    }
  };

  // Create new conversation
  const createNewConversation = () => {
    const newConversation: Conversation = {
      id: `conv-${Date.now()}`,
      title: 'New Conversation',
      messages: [{
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: `Hello! I'm Mnemosyne in ${PERSONA_MODES[personaMode as keyof typeof PERSONA_MODES].name} mode. ${PERSONA_MODES[personaMode as keyof typeof PERSONA_MODES].description}. How can I help you today?`,
        timestamp: new Date()
      }],
      createdAt: new Date(),
      updatedAt: new Date(),
      persona_mode: personaMode
    };

    setConversations(prev => [newConversation, ...prev]);
    setCurrentConversationId(newConversation.id);
  };

  // Update conversation
  const updateConversation = (conversationId: string, updater: (conv: Conversation) => Conversation) => {
    setConversations(prev => prev.map(conv => 
      conv.id === conversationId ? updater(conv) : conv
    ));
  };

  // Handle streaming response
  const handleStreamingResponse = async (response: Response, conversationId: string) => {
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let assistantMessage = '';
    let detectedPersonaMode = '';
    let capturedReasoning = '';  // Local variable to capture reasoning
    const assistantMessageId = `msg-${Date.now()}`;

    if (!reader) throw new Error('No reader available');

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          // Handle SSE events (both regular and agentic)
          if (line.startsWith('event: ')) {
            const eventType = line.slice(7);
            
            // Handle agentic event types
            if (eventType === 'status') {
              // Status update from agentic flow
              continue;
            } else if (eventType === 'reasoning') {
              // Reasoning explanation
              continue;
            } else if (eventType === 'suggestions') {
              // Proactive suggestions
              continue;
            }
          } else if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;
            
            try {
              const parsed = JSON.parse(data);
              
              // Check if it's an agentic status/reasoning/suggestion
              if (parsed.status) {
                setAgenticStatus(parsed.status);
                // Extract persona mode from status like "Activated confidant mode"
                const modeMatch = parsed.status.match(/Activated (\w+) mode/);
                if (modeMatch) {
                  detectedPersonaMode = modeMatch[1];
                  setStreamingPersonaMode(modeMatch[1]);
                }
              } else if (parsed.reasoning) {
                setAgenticReasoning(parsed.reasoning);
                capturedReasoning = parsed.reasoning;  // Capture locally
              } else if (parsed.suggestions) {
                setAgenticSuggestions(parsed.suggestions);
              } else if (parsed.content) {
                // Direct content from agentic flow
                assistantMessage += parsed.content;
                setStreamingMessage(assistantMessage);
              } else {
                // Regular streaming format
                const content = parsed.choices?.[0]?.delta?.content || '';
                assistantMessage += content;
                setStreamingMessage(assistantMessage);
              }
            } catch (e) {
              // Skip unparseable lines
            }
          }
        }
      }

      // Add complete message to conversation with detected persona mode and reasoning
      updateConversation(conversationId, conv => ({
        ...conv,
        messages: [...conv.messages, {
          id: assistantMessageId,
          role: 'assistant',
          content: assistantMessage,
          timestamp: new Date(),
          personaMode: detectedPersonaMode || personaMode,
          reasoning: capturedReasoning  // Save captured reasoning for transparency
        }],
        updatedAt: new Date()
      }));

      setStreamingMessage('');
      setStreamingPersonaMode(''); // Clear for next message
      // Don't clear reasoning - let it persist in the message
    } catch (error) {
      console.error('Streaming error:', error);
      throw error;
    }
  };

  // Handle regular response
  const handleRegularResponse = async (response: Response, conversationId: string) => {
    const data = await response.json();
    
    const assistantMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'assistant',
      content: data.choices[0].message.content,
      timestamp: new Date()
    };

    updateConversation(conversationId, conv => ({
      ...conv,
      messages: [...conv.messages, assistantMessage],
      updatedAt: new Date()
    }));
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    
    // Get max tokens from env or use default
    const maxTokens = parseInt(import.meta.env.VITE_MAX_CONTEXT_TOKENS || '8000');

    let conversationId = currentConversationId;
    
    // Create new conversation if none exists
    if (!conversationId) {
      createNewConversation();
      conversationId = `conv-${Date.now()}`;
      // Wait for state update
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    // Add user message to conversation
    updateConversation(conversationId, conv => ({
      ...conv,
      messages: [...conv.messages, userMessage],
      title: conv.messages.length === 1 ? input.slice(0, 50) : conv.title,
      updatedAt: new Date()
    }));

    setInput('');
    setIsLoading(true);
    // Clear agentic states
    setAgenticStatus('');
    setAgenticReasoning('');
    setAgenticSuggestions([]);

    // Create abort controller for cancellation
    abortControllerRef.current = new AbortController();

    try {
      // Get conversation messages for context - INCLUDING the user message we just added
      const currentConv = conversations.find(c => c.id === conversationId);
      
      // Build messages array including the NEW user message (since state might not have updated yet)
      const existingMessages = currentConv?.messages.map(m => ({
          role: m.role,
          content: m.content
        })) || [];
      
      // Add the user message we just created (in case state hasn't updated)
      let conversationMessages = [...existingMessages, {
        role: userMessage.role,
        content: userMessage.content
      }];
      
      // Check token limits and truncate if needed
      const tokenCheck = checkTokenLimit(conversationMessages, maxTokens);
      console.log(`Token count: ${tokenCheck.tokens}/${maxTokens}`);
      
      if (!tokenCheck.withinLimit) {
        console.warn(`Truncating messages: ${tokenCheck.tokens} tokens exceeds limit of ${maxTokens}`);
        conversationMessages = truncateMessages(conversationMessages, maxTokens, 3);
        const newTokenCount = countMessageTokens(conversationMessages);
        console.log(`After truncation: ${newTokenCount} tokens`);
      }
      
      console.log('Messages being sent:', conversationMessages);

      // Use streaming endpoint if enabled, agentic if toggled
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const endpoint = useAgentic 
        ? '/api/v1/chat/agentic/stream'
        : (enableStreaming ? '/api/v1/chat/stream' : '/api/v1/chat/chat');
      
      // Get auth token from localStorage
      const token = localStorage.getItem('token');
      
      // Format body differently for agentic vs regular endpoint
      const requestBody = useAgentic ? {
        messages: conversationMessages,  // Already in correct format
        use_agentic: true,
        max_iterations: 3,
        stream_status: true,
        include_reasoning: true,
        parallel_actions: true,
        selected_tools: selectedTools.length > 0 ? selectedTools : undefined  // Add selected tools if any
      } : {
        messages: conversationMessages,
        persona_mode: personaMode,
        stream: enableStreaming
      };
      
      console.log('Auth token present:', !!token);
      console.log('Using endpoint:', endpoint);
      console.log('Request body:', requestBody);
      
      const response = await fetch(`${baseUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
        body: JSON.stringify(requestBody),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        let errorMessage = 'Chat request failed';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
          console.error('API Error:', errorData);
        } catch (e) {
          // If response isn't JSON, use status text
          errorMessage = `${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      // Handle streaming vs regular response
      if (enableStreaming && response.headers.get('content-type')?.includes('text/event-stream')) {
        await handleStreamingResponse(response, conversationId);
      } else {
        await handleRegularResponse(response, conversationId);
      }

    } catch (error: any) {
      if (error.name !== 'AbortError') {
        console.error('Chat error:', error);
        updateConversation(conversationId, conv => ({
          ...conv,
          messages: [...conv.messages, {
            id: `msg-${Date.now()}`,
            role: 'assistant',
            content: 'Sorry, I encountered an error. Please try again.',
            timestamp: new Date()
          }],
          updatedAt: new Date()
        }));
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
      setAgenticReasoning(''); // Clear reasoning for next message
      setAgenticStatus('');    // Clear status for next message
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Cancel streaming
  const cancelStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setStreamingMessage('');
      setIsLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-background">
      <div className="flex-1 flex flex-col py-8 min-h-0">
        <Card className="h-full flex flex-col border-0 shadow-none mx-0">
          <CardHeader className="flex-shrink-0 container mx-auto px-4 max-w-4xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <CardTitle>
                  {currentConversation?.title || 'New Conversation'}
                </CardTitle>
              </div>
              <div className="flex items-center gap-2">
                {/* Delete Button - Only show for existing conversations */}
                {currentConversation && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => deleteConversation(currentConversation.id)}
                    title="Delete conversation"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
                
                {/* Agentic Mode Toggle */}
                <div className="flex items-center gap-2 px-3 py-1.5 border rounded-md">
                  <label className="text-sm font-medium flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={useAgentic}
                      onChange={(e) => setUseAgentic(e.target.checked)}
                      className="rounded"
                      disabled={isLoading}
                    />
                    <Sparkles className="h-4 w-4" />
                    Agentic
                  </label>
                </div>
                
                {/* Persona Mode Selector - Only enabled when not agentic */}
                <div className="relative group">
                  <select 
                    value={personaMode}
                    onChange={(e) => setPersonaMode(e.target.value)}
                    className={`px-3 py-1.5 text-sm border rounded-md bg-background text-foreground appearance-none pr-8 cursor-pointer hover:bg-accent ${useAgentic ? 'opacity-50 cursor-not-allowed' : ''}`}
                    disabled={isLoading || useAgentic}
                    title={useAgentic ? "Persona is auto-selected in Agentic mode" : "Select AI persona mode"}
                  >
                    {Object.entries(PERSONA_MODES).map(([key, mode]) => (
                      <option key={key} value={key}>{mode.name}</option>
                    ))}
                  </select>
                  <div className="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                  {/* Tooltip */}
                  <div className="absolute left-0 top-full mt-1 w-64 p-2 bg-popover border rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
                    <p className="text-xs font-medium mb-1">
                      {useAgentic ? 'Auto-Selected by AI' : `${PERSONA_MODES[personaMode as keyof typeof PERSONA_MODES].name} Mode`}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {useAgentic 
                        ? 'AI analyzes your message and selects the best persona automatically'
                        : PERSONA_MODES[personaMode as keyof typeof PERSONA_MODES].description}
                    </p>
                  </div>
                </div>
                
                {/* Tool Palette Toggle */}
                <Button
                  onClick={() => setShowToolPalette(!showToolPalette)}
                  variant={showToolPalette ? "default" : "outline"}
                  size="sm"
                  disabled={isLoading}
                  title="Toggle tool palette"
                >
                  <Wrench className="w-4 h-4 mr-1" />
                  Tools
                  {selectedTools.length > 0 && (
                    <Badge variant="secondary" className="ml-1">
                      {selectedTools.length}
                    </Badge>
                  )}
                </Button>
                
                {/* Streaming Toggle - Improved */}
                <label className="flex items-center gap-2 text-sm cursor-pointer hover:bg-accent px-2 py-1 rounded" title="Enable real-time streaming responses">
                  <input
                    type="checkbox"
                    checked={enableStreaming}
                    onChange={(e) => setEnableStreaming(e.target.checked)}
                    disabled={isLoading}
                    className="cursor-pointer"
                  />
                  <span className="select-none">Stream</span>
                </label>
                
                {/* New Conversation Button */}
                <Button 
                  onClick={createNewConversation}
                  variant="outline"
                  size="sm"
                  disabled={isLoading}
                  title="Start a new conversation"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  New
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col min-h-0 px-0">
            
            {/* Tool Palette - Show when toggled */}
            {showToolPalette && (
              <div className="container mx-auto px-4 max-w-4xl mb-4">
                <ToolPalette 
                  onToolsChange={setSelectedTools}
                  className="animate-in slide-in-from-top-2"
                />
              </div>
            )}
            
            <div className="flex-1 overflow-y-auto mb-4 custom-scrollbar">
              <div className="container mx-auto px-4 max-w-4xl space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[70%] rounded-lg px-4 py-2 ${
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm font-semibold flex items-center gap-2">
                        {message.role === 'user' ? 'You' : (
                          <>
                            <Sparkles className="w-3 h-3" />
                            Mnemosyne
                          </>
                        )}
                      </p>
                      {message.role === 'assistant' && message.personaMode && (
                        <Badge 
                          variant="outline" 
                          className={`text-xs ${PERSONA_MODES[message.personaMode as keyof typeof PERSONA_MODES]?.color || ''}`}
                        >
                          {PERSONA_MODES[message.personaMode as keyof typeof PERSONA_MODES]?.name || message.personaMode}
                        </Badge>
                      )}
                    </div>
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    {message.reasoning && (
                      <details className="mt-2 text-xs text-muted-foreground border rounded p-2 bg-background/50">
                        <summary className="cursor-pointer font-semibold hover:text-foreground select-none">
                          View Reasoning (Technical Details)
                        </summary>
                        <div className="mt-2 pt-2 border-t">
                          <pre className="whitespace-pre-wrap break-words font-mono text-[10px] overflow-x-auto max-h-48 overflow-y-auto">
                            {message.reasoning}
                          </pre>
                        </div>
                      </details>
                    )}
                    <p className="text-xs opacity-70 mt-1">
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
              
              {/* Streaming message */}
              {streamingMessage && (
                <div className="flex justify-start">
                  <div className="bg-muted rounded-lg px-4 py-2 max-w-[70%]">
                    <p className="text-sm font-semibold mb-1 flex items-center gap-2">
                      <Sparkles className="w-3 h-3 animate-pulse" />
                      Mnemosyne
                    </p>
                    <p className="whitespace-pre-wrap">{streamingMessage}</p>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={cancelStreaming}
                      className="mt-2"
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              )}
              
              {/* Loading indicator with agentic status */}
              {isLoading && !streamingMessage && (
                <div className="flex justify-start">
                  <div className="bg-muted rounded-lg px-4 py-2">
                    <p className="text-sm font-semibold mb-1 flex items-center gap-2">
                      <Sparkles className="w-3 h-3" />
                      Mnemosyne {useAgentic && <span className="text-xs font-normal text-blue-600">(Agentic Mode)</span>}
                    </p>
                    <div className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>{agenticStatus || 'Thinking...'}</span>
                    </div>
                    {agenticReasoning && (
                      <details className="mt-2 text-xs text-muted-foreground border rounded p-2 bg-muted/30">
                        <summary className="cursor-pointer font-semibold hover:text-foreground select-none">
                          View Reasoning (Technical Details)
                        </summary>
                        <div className="mt-2 pt-2 border-t">
                          <pre className="whitespace-pre-wrap break-words font-mono text-[10px] overflow-x-auto max-h-48 overflow-y-auto">
                            {agenticReasoning}
                          </pre>
                        </div>
                      </details>
                    )}
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
              </div>
            </div>

            <div className="border-t pt-4 container mx-auto px-4 max-w-4xl flex flex-col gap-2 flex-shrink-0">
              {/* Agentic Suggestions Display */}
              {agenticSuggestions.length > 0 && (
                <div className="mb-2 p-2 bg-muted/50 dark:bg-muted rounded-lg border border-border">
                  <p className="text-xs font-semibold text-foreground mb-1">💡 Suggestions:</p>
                  <div className="flex flex-wrap gap-1">
                    {agenticSuggestions.slice(0, 3).map((suggestion, idx) => {
                      const text = typeof suggestion === 'string' 
                        ? suggestion 
                        : (suggestion?.text || suggestion?.suggestion || '');
                      if (!text) return null;
                      return (
                        <button
                          key={idx}
                          onClick={() => setInput(text)}
                          className="text-xs px-2 py-1 bg-background dark:bg-background rounded border border-border hover:bg-muted dark:hover:bg-muted transition-colors text-foreground"
                        >
                          {text.slice(0, 50)}...
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}
              <div className="flex gap-2">
                <Input
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  disabled={isLoading}
                  className="flex-1"
                />
                <Button 
                  onClick={handleSend} 
                  disabled={isLoading || !input.trim()}
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>💡 Your conversations are private and encrypted</span>
                {conversations.length > 0 && (
                  <span>{conversations.length} conversation{conversations.length !== 1 ? 's' : ''} stored locally</span>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ChatEnhanced;