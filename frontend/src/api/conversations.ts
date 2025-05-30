/**
 * Conversations API client
 * 
 * This module provides functions for interacting with the conversation API endpoints.
 */
import { Conversation, Message, PaginatedResponse } from '../types';
import { get, post, put, del } from './client';

/**
 * Fetch a paginated list of conversations
 * @param limit Maximum number of items to return
 * @param offset Pagination offset
 * @returns Promise resolving to conversations list
 */
export const getConversations = async (limit = 20, offset = 0) => {
  return get<PaginatedResponse<Conversation>>(`/conversations?limit=${limit}&offset=${offset}`);
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
  return post<Conversation>('/conversations', { title });
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
 * Delete a message from a conversation
 * @param conversationId Conversation ID
 * @param messageId Message ID
 * @returns Promise resolving to success status
 */
export const deleteMessage = async (conversationId: string, messageId: string) => {
  return del<{ success: boolean }>(`/conversations/${conversationId}/messages/${messageId}`);
};

export default {
  getConversations,
  getConversation,
  createConversation,
  updateConversation,
  deleteConversation,
  sendMessage,
  deleteMessage,
};
