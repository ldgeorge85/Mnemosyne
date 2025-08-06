/**
 * Shared API types
 */

/**
 * Standard API response wrapper
 */
export interface ApiResponse<T = any> {
  data: T;
  status: number;
  message?: string;
}

/**
 * Paginated response shape used by many list endpoints
 */
export interface PaginatedResponse<T = any> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

/**
 * Message model returned by conversation endpoints
 */
export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  updated_at: string;
}

/**
 * Conversation model
 */
export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages?: Message[];
}
