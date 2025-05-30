/**
 * Conversation Store
 * 
 * This module provides a Zustand store for managing conversations and messages,
 * including fetching, caching, and updating conversation data.
 */
import { create } from 'zustand';
import { Conversation, Message } from '../types';

/**
 * Conversation store state interface
 */
interface ConversationState {
  // Conversation data
  conversations: Conversation[];
  currentConversation: Conversation | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  fetchConversations: () => Promise<void>;
  getConversation: (id: string) => Promise<void>;
  createConversation: (title: string) => Promise<string>;
  updateConversation: (id: string, data: Partial<Conversation>) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  
  // Message actions
  sendMessage: (conversationId: string, content: string) => Promise<void>;
  deleteMessage: (conversationId: string, messageId: string) => Promise<void>;
}

/**
 * Create the conversation store
 */
const useConversationStore = create<ConversationState>((set, get) => ({
  // Initial state
  conversations: [],
  currentConversation: null,
  isLoading: false,
  error: null,
  
  /**
   * Fetch all conversations for the current user
   */
  fetchConversations: async () => {
    set({ isLoading: true, error: null });
    
    try {
      // In a real app, you would fetch from your API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock data for demonstration
      const mockConversations: Conversation[] = [
        {
          id: '1',
          title: 'Project Kickoff Discussion',
          messages: [
            {
              id: '101',
              conversationId: '1',
              content: 'Let\'s discuss the project requirements.',
              role: 'user',
              createdAt: new Date().toISOString(),
            },
            {
              id: '102',
              conversationId: '1',
              content: 'I can help you organize the project requirements. What are the main goals?',
              role: 'assistant',
              createdAt: new Date().toISOString(),
            },
          ],
          userId: 'user123',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
        {
          id: '2',
          title: 'Weekly Team Sync',
          messages: [],
          userId: 'user123',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      ];
      
      set({ conversations: mockConversations, isLoading: false });
    } catch (error) {
      set({ error: 'Failed to fetch conversations', isLoading: false });
      console.error('Error fetching conversations:', error);
    }
  },
  
  /**
   * Fetch a specific conversation by ID
   */
  getConversation: async (id: string) => {
    set({ isLoading: true, error: null });
    
    try {
      // Check if we already have this conversation in state
      const existingConversation = get().conversations.find(conv => conv.id === id);
      
      if (existingConversation) {
        set({ currentConversation: existingConversation, isLoading: false });
        return;
      }
      
      // In a real app, you would fetch from your API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock data for demonstration
      const mockConversation: Conversation = {
        id,
        title: 'New Conversation',
        messages: [],
        userId: 'user123',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      
      set({ 
        currentConversation: mockConversation,
        conversations: [...get().conversations, mockConversation],
        isLoading: false 
      });
    } catch (error) {
      set({ error: `Failed to fetch conversation ${id}`, isLoading: false });
      console.error('Error fetching conversation:', error);
    }
  },
  
  /**
   * Create a new conversation
   */
  createConversation: async (title: string) => {
    set({ isLoading: true, error: null });
    
    try {
      // In a real app, you would create via your API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Generate a unique ID (in a real app, this would come from the server)
      const newId = Date.now().toString();
      
      // Create a new conversation object
      const newConversation: Conversation = {
        id: newId,
        title,
        messages: [],
        userId: 'user123',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      
      // Add to state
      set({
        conversations: [...get().conversations, newConversation],
        currentConversation: newConversation,
        isLoading: false,
      });
      
      return newId;
    } catch (error) {
      set({ error: 'Failed to create conversation', isLoading: false });
      console.error('Error creating conversation:', error);
      return '';
    }
  },
  
  /**
   * Update an existing conversation
   */
  updateConversation: async (id: string, data: Partial<Conversation>) => {
    set({ isLoading: true, error: null });
    
    try {
      // In a real app, you would update via your API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const updatedConversations = get().conversations.map(conv => 
        conv.id === id ? { ...conv, ...data, updatedAt: new Date().toISOString() } : conv
      );
      
      const updatedCurrentConversation = get().currentConversation?.id === id
        ? { ...get().currentConversation, ...data, updatedAt: new Date().toISOString() }
        : get().currentConversation;
      
      set({
        conversations: updatedConversations,
        currentConversation: updatedCurrentConversation,
        isLoading: false,
      });
    } catch (error) {
      set({ error: `Failed to update conversation ${id}`, isLoading: false });
      console.error('Error updating conversation:', error);
    }
  },
  
  /**
   * Delete a conversation
   */
  deleteConversation: async (id: string) => {
    set({ isLoading: true, error: null });
    
    try {
      // In a real app, you would delete via your API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const filteredConversations = get().conversations.filter(conv => conv.id !== id);
      
      set({
        conversations: filteredConversations,
        currentConversation: get().currentConversation?.id === id ? null : get().currentConversation,
        isLoading: false,
      });
    } catch (error) {
      set({ error: `Failed to delete conversation ${id}`, isLoading: false });
      console.error('Error deleting conversation:', error);
    }
  },
  
  /**
   * Send a message in a conversation
   */
  sendMessage: async (conversationId: string, content: string) => {
    try {
      // Create a new message
      const newMessage: Message = {
        id: Date.now().toString(),
        conversationId,
        content,
        role: 'user',
        createdAt: new Date().toISOString(),
      };
      
      // Get the current conversation
      const conversation = get().conversations.find(conv => conv.id === conversationId);
      
      if (!conversation) {
        throw new Error(`Conversation ${conversationId} not found`);
      }
      
      // Add message to conversation
      const updatedConversation = {
        ...conversation,
        messages: [...conversation.messages, newMessage],
        updatedAt: new Date().toISOString(),
      };
      
      // Update conversations in state
      const updatedConversations = get().conversations.map(conv => 
        conv.id === conversationId ? updatedConversation : conv
      );
      
      set({
        conversations: updatedConversations,
        currentConversation: updatedConversation,
      });
      
      // Simulate an AI response (in a real app, this would come from the API)
      setTimeout(() => {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          conversationId,
          content: 'This is a simulated response from the assistant.',
          role: 'assistant',
          createdAt: new Date().toISOString(),
        };
        
        const conversation = get().conversations.find(conv => conv.id === conversationId);
        
        if (conversation) {
          const updatedConversation = {
            ...conversation,
            messages: [...conversation.messages, assistantMessage],
            updatedAt: new Date().toISOString(),
          };
          
          const updatedConversations = get().conversations.map(conv => 
            conv.id === conversationId ? updatedConversation : conv
          );
          
          set({
            conversations: updatedConversations,
            currentConversation: updatedConversation,
          });
        }
      }, 1500);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  },
  
  /**
   * Delete a message from a conversation
   */
  deleteMessage: async (conversationId: string, messageId: string) => {
    try {
      // Get the current conversation
      const conversation = get().conversations.find(conv => conv.id === conversationId);
      
      if (!conversation) {
        throw new Error(`Conversation ${conversationId} not found`);
      }
      
      // Remove message from conversation
      const updatedConversation = {
        ...conversation,
        messages: conversation.messages.filter(msg => msg.id !== messageId),
        updatedAt: new Date().toISOString(),
      };
      
      // Update conversations in state
      const updatedConversations = get().conversations.map(conv => 
        conv.id === conversationId ? updatedConversation : conv
      );
      
      set({
        conversations: updatedConversations,
        currentConversation: updatedConversation,
      });
    } catch (error) {
      console.error('Error deleting message:', error);
    }
  },
}));

export default useConversationStore;
