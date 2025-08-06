/**
 * Core type definitions for the Mnemosyne application
 */

// User related types
export interface User {
  id: string;
  username: string;
  email: string;
  firstName?: string;
  lastName?: string;
  createdAt: string;
  updatedAt: string;
}

// Conversation related types
export interface MessageAttachment {
  type: 'image' | 'video' | 'audio' | 'pdf' | 'other';
  url: string;
  fileName?: string;
  fileSize?: number;
}

export interface Message {
  id: string;
  conversationId: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  createdAt: string;
  attachments?: MessageAttachment[];
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  userId: string;
  createdAt: string;
  updatedAt: string;
}

export interface ConversationSummary {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
}

// Memory related types
export interface Memory {
  id: string;
  content: string;
  source: string;
  importance: number;
  embedding?: number[];
  userId: string;
  createdAt: string;
  updatedAt: string;
}

// Task related types
export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  dueDate?: string;
  priority: 'low' | 'medium' | 'high';
  userId: string;
  createdAt: string;
  updatedAt: string;
}

// API response types
export interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
}

// Paginated response type
export interface PaginatedResponse<T> {
  total: number;
  offset: number;
  limit: number;
  items: T[];
}

// Health check response
export interface HealthStatus {
  status: string;
  service: string;
  version: string;
  environment: string;
  components?: Record<string, { status: string; message: string }>;
}
