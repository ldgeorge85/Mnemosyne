/**
 * Conversations API client
 * 
 * This module provides functions for interacting with the conversation API endpoints.
 */
import { get, post, put, del } from './client-simple';
import type { Conversation, Message, PaginatedResponse } from '../types';

/**
 * Fetch a paginated list of conversations
 * @param limit Maximum number of items to return
 * @param offset Pagination offset
 * @returns Promise resolving to conversations list
 */
export const getConversations = async (limit = 20, offset = 0) => {
  return get<PaginatedResponse<Conversation>>(`/conversations/?limit=${limit}&offset=${offset}`);
};

/**
 * Fetch a specific conversation with its messages
 * @param id Conversation ID
 * @param limit Maximum number of messages to return
 * @param offset Pagination offset for messages
 * @returns Promise resolving to conversation with messages
 */
export const getConversation = async (id: string, limit = 50, offset = 0) => {
  return get<Conversation>(`/conversations/${id}?limit=${limit}&offset=${offset}`);
};

/**
 * Create a new conversation
 * @param title Conversation title
 * @returns Promise resolving to the created conversation
 */
export const createConversation = async (title: string) => {
  return post<Conversation>('/conversations/', { title });
};

/**
 * Update an existing conversation
 * @param id Conversation ID
 * @param title New conversation title
 * @returns Promise resolving to the updated conversation
 */
export const updateConversation = async (id: string, title: string) => {
  return put<Conversation>(`/conversations/${id}`, { title });
};

/**
 * Delete a conversation
 * @param id Conversation ID
 * @returns Promise resolving to success status
 */
export const deleteConversation = async (id: string) => {
  return del<{ success: boolean }>(`/conversations/${id}`);
};

/**
 * Send a message in a conversation
 * @param conversationId Conversation ID
 * @param content Message content
 * @param role Message role (user or system)
 * @returns Promise resolving to the created message with assistant response
 */
export const sendMessage = async (conversationId: string, content: string, role = 'user') => {
  return post<Message & { assistant_response: Message | null }>(
    `/conversations/${conversationId}/messages`, 
    { content, role }
  );
};

/**
 * Send a message with streaming response
 * @param conversationId Conversation ID
 * @param content Message content
 * @param role Message role (user or system)
 * @param onChunk Callback for each streaming chunk
 * @param onComplete Callback when streaming is complete
 * @returns Promise resolving when streaming starts
 */
export const sendMessageStream = async (
  conversationId: string, 
  content: string, 
  onChunk: (chunk: string) => void,
  onComplete: (fullMessage: string) => void,
  onError?: (error: Error) => void,
  role = 'user'
) => {
  try {
    const response = await fetch(`/api/v1/conversations/${conversationId}/messages/stream/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
      body: JSON.stringify({ content, role }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Response body is not readable');
    }

    const decoder = new TextDecoder();
    let fullMessage = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim();
            
            if (data === '[DONE]') {
              onComplete(fullMessage);
              return;
            }

            try {
              const parsed = JSON.parse(data);
              // Streaming protocol v2: events include type and nested data
                const eventType = parsed.type || null;
                if (eventType === 'chunk' && parsed.data?.content) {
                  fullMessage += parsed.data.content;
                  onChunk(parsed.data.content);
                } else if (eventType === 'assistant_complete' && parsed.data?.content) {
                  fullMessage += parsed.data.content;
                  onChunk(parsed.data.content);
                  onComplete(fullMessage);
                  return;
                } else if (eventType === 'done') {
                  onComplete(fullMessage);
                  return;
                } else {
                  // Fallback: support old schema with content at top level
                  if (parsed.content) {
                    fullMessage += parsed.content;
                    onChunk(parsed.content);
                  }
                }
            } catch (e) {
              // Skip invalid JSON lines
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }

    onComplete(fullMessage);
  } catch (error) {
    if (onError) {
      onError(error as Error);
    }
    throw error;
  }
};

/**
 * Delete a message from a conversation
 * @param conversationId Conversation ID
 * @param messageId Message ID
 * @returns Promise resolving to success status
 */
export const deleteMessage = async (conversationId: string, messageId: string) => {
  return del<{ success: boolean }>(`/conversations/${conversationId}/messages/${messageId}/`);
};

export default {
  getConversations,
  getConversation,
  createConversation,
  updateConversation,
  deleteConversation,
  sendMessage,
  sendMessageStream,
  deleteMessage,
};
