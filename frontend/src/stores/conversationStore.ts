/**
 * Conversation Store
 * 
 * This module provides a Zustand store for managing conversations and messages,
 * including fetching, caching, and updating conversation data.
 */
import { create } from 'zustand';
import { Conversation, Message, PaginatedResponse } from '../types';
import { conversationsService } from '../api';

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
const useConversationStore = create<ConversationState>((set: any, get: any) => ({
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
      const response = await conversationsService.getConversations();
      
      if (response.status >= 400) {
        throw new Error(response.message || 'Failed to fetch conversations');
      }
      
      const data = response.data as PaginatedResponse<Conversation>;
      set({ conversations: data.items, isLoading: false });
    } catch (error) {
      set({ error: 'Failed to fetch conversations', isLoading: false });
    }
  },
  
  /**
   * Fetch a specific conversation by ID
   */
  getConversation: async (id: string) => {
    set({ isLoading: true, error: null });
    
    try {
      // Check if we already have this conversation in state with messages
      const existingConversation = get().conversations.find((conv: Conversation) => 
        conv.id === id && conv.messages && conv.messages.length > 0
      );
      
      if (existingConversation) {
        set({ currentConversation: existingConversation, isLoading: false });
        return;
      }
      
      const response = await conversationsService.getConversation(id);
      
      if (response.status >= 400) {
        throw new Error(response.message || `Failed to fetch conversation ${id}`);
      }
      
      const conversation = response.data as Conversation;
      
      // Format messages from the API response
      const formattedConversation = {
        ...conversation,
        messages: (conversation as any).messages?.items || []
      };
      
      // Update both the current conversation and the conversations list
      const updatedConversations = get().conversations.map((conv: Conversation) => 
        conv.id === id ? formattedConversation : conv
      );
      
      // If the conversation wasn't in the list, add it
      if (!updatedConversations.some((conv: Conversation) => conv.id === id)) {
        updatedConversations.push(formattedConversation);
      }
      
      set({ 
        currentConversation: formattedConversation,
        conversations: updatedConversations,
        isLoading: false 
      });
    } catch (error) {
      set({ error: `Failed to fetch conversation ${id}`, isLoading: false });
    }
  },
  
  /**
   * Create a new conversation
   */
  createConversation: async (title: string) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await conversationsService.createConversation(title);
      
      if (response.status >= 400) {
        throw new Error(response.message || 'Failed to create conversation');
      }
      
      const newConversation = response.data as Conversation;
      
      // Initialize empty messages array if not present
      if (!newConversation.messages) {
        newConversation.messages = [];
      }
      
      // Add to state
      set({
        conversations: [...get().conversations, newConversation],
        currentConversation: newConversation,
        isLoading: false,
      });
      
      return newConversation.id;
    } catch (error) {
      set({ error: 'Failed to create conversation', isLoading: false });
      return '';
    }
  },
  
  /**
   * Update an existing conversation
   */
  updateConversation: async (id: string, data: Partial<Conversation>) => {
    set({ isLoading: true, error: null });
    
    try {
      // Only send the title to the API
      const response = await conversationsService.updateConversation(id, data.title || '');
      
      if (response.status >= 400) {
        throw new Error(response.message || `Failed to update conversation ${id}`);
      }
      
      const updatedConversation = response.data as Conversation;
      
      // Update state with the response from the API
      const updatedConversations = get().conversations.map((conv: Conversation) => 
        conv.id === id ? { ...conv, ...updatedConversation } : conv
      );
      
      const updatedCurrentConversation = get().currentConversation?.id === id
        ? { ...get().currentConversation, ...updatedConversation }
        : get().currentConversation;
      
      set({
        conversations: updatedConversations,
        currentConversation: updatedCurrentConversation,
        isLoading: false,
      });
    } catch (error) {
      set({ error: `Failed to update conversation ${id}`, isLoading: false });
    }
  },
  
  /**
   * Delete a conversation
   */
  deleteConversation: async (id: string) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await conversationsService.deleteConversation(id);
      
      if (response.status >= 400) {
        throw new Error(response.message || `Failed to delete conversation ${id}`);
      }
      
      // Remove the conversation from state
      const filteredConversations = get().conversations.filter((conv: Conversation) => conv.id !== id);
      const updatedCurrentConversation = get().currentConversation?.id === id
        ? null
        : get().currentConversation;
      
      set({
        conversations: filteredConversations,
        currentConversation: updatedCurrentConversation,
        isLoading: false,
      });
    } catch (error) {
      set({ error: `Failed to delete conversation ${id}`, isLoading: false });
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
      const conversation = get().conversations.find((conv: Conversation) => conv.id === conversationId);
      
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
      const updatedConversations = get().conversations.map((conv: Conversation) => 
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
        
        const conversation = get().conversations.find((conv: Conversation) => conv.id === conversationId);
        
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
      // Handle error silently
    }
  },
  
  /**
   * Delete a message from a conversation
   */
  deleteMessage: async (conversationId: string, messageId: string) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await conversationsService.deleteMessage(conversationId, messageId);
      
      if (response.status >= 400) {
        throw new Error(response.message || 'Failed to delete message');
      }
      
      // Get the target conversation
      const conversation = get().conversations.find((conv: Conversation) => conv.id === conversationId);
      
      if (!conversation) {
        throw new Error(`Conversation ${conversationId} not found`);
      }
      
      // Remove the message from the conversation
      const updatedConversation = {
        ...conversation,
        messages: (conversation.messages || []).filter((msg: Message) => msg.id !== messageId),
        updatedAt: new Date().toISOString(),
      };
      
      // Update state
      const updatedConversations = get().conversations.map((conv: Conversation) => 
        conv.id === conversationId ? updatedConversation : conv
      );
      
      set({
        conversations: updatedConversations,
        currentConversation: updatedConversation,
        isLoading: false,
      });
    } catch (error) {
      set({ error: 'Failed to delete message', isLoading: false });
    }
  },
}));

export default useConversationStore;
