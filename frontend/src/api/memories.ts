/**
 * Memories API client
 * 
 * This module provides functions for memory management operations.
 */
import { get, post, put, del } from './client-simple';

/**
 * Memory interfaces
 */
export interface Memory {
  id: string;
  title: string;
  content: string;
  tags?: string[];
  importance_score?: number;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  user_id: string;
  metadata?: {
    source?: string;
    conversation_id?: string;
    entities?: Array<{text: string; type: string; confidence: number}>;
    domain?: string;
    extraction_method?: string;
    confidence?: number;
    [key: string]: any;
  };
  similarity?: number; // For search results
}

export interface MemoryCreate {
  user_id: string; // backend requires the user id of the memory owner
  title: string;
  content: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

export interface MemoryUpdate {
  title?: string;
  content?: string;
  tags?: string[];
  metadata?: Record<string, any>;
  is_active?: boolean;
}

export interface MemorySearchQuery {
  query: string;
  limit?: number;
  offset?: number;
  include_inactive?: boolean;
}

export interface MemoryStatistics {
  total_memories: number;
  active_memories: number;
  inactive_memories: number;
  total_chunks: number;
  average_importance_score: number;
}

/**
 * List memories for the current user
 */
export const listMemories = async (params?: {
  limit?: number;
  offset?: number;
  include_inactive?: boolean;
}) => {
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());
  if (params?.include_inactive) queryParams.append('include_inactive', params.include_inactive.toString());
  
  const url = `/memories/${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  return get<Memory[]>(url);
};

/**
 * Get a specific memory by ID
 */
export const getMemory = async (memoryId: string, includeChunks: boolean = false) => {
  const queryParams = includeChunks ? '?include_chunks=true' : '';
  return get<Memory>(`/memories/${memoryId}${queryParams}`);
};

/**
 * Create a new memory
 */
export const createMemory = async (memoryData: MemoryCreate) => {
  return post<Memory>('/memories/', memoryData);
};

/**
 * Update an existing memory
 */
export const updateMemory = async (memoryId: string, memoryData: MemoryUpdate) => {
  return put<Memory>(`/memories/${memoryId}`, memoryData);
};

/**
 * Delete a memory
 */
export const deleteMemory = async (memoryId: string, permanent: boolean = false) => {
  const queryParams = permanent ? '?permanent=true' : '';
  return del(`/memories/${memoryId}${queryParams}`);
};

/**
 * Search memories
 */
export const searchMemories = async (searchQuery: MemorySearchQuery) => {
  return post<Memory[]>('/memories/search', searchQuery);
};

/**
 * Get memories by tag
 */
export const getMemoriesByTag = async (tag: string, params?: {
  limit?: number;
  offset?: number;
  include_inactive?: boolean;
}) => {
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());
  if (params?.include_inactive) queryParams.append('include_inactive', params.include_inactive.toString());
  
  const url = `/memories/tag/${tag}${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  return get<Memory[]>(url);
};

/**
 * Get memory statistics
 */
export const getMemoryStatistics = async () => {
  return get<MemoryStatistics>('/memories/statistics');
};

/**
 * Trigger memory reflection for an agent
 */
export const reflectMemory = async (agentId: string, memories: any[]) => {
  return post('/memories/reflect', { agent_id: agentId, memories });
};

/**
 * Get importance scores for memories
 */
export const getImportanceScores = async (agentId: string) => {
  return get(`/memories/importance?agent_id=${agentId}`);
};

/**
 * Get hierarchical organization of memories
 */
export const getMemoryHierarchy = async (agentId: string) => {
  return get(`/memories/hierarchy?agent_id=${agentId}`);
};

/**
 * Extract memories from a conversation
 */
export const extractMemoriesFromConversation = async (conversationId: string) => {
  return post<{
    conversation_id: string;
    memories_created: number;
    entities_extracted: number;
    facts_extracted: number;
  }>(`/memories/extract/${conversationId}`, {});
};

export default {
  listMemories,
  getMemory,
  createMemory,
  updateMemory,
  deleteMemory,
  searchMemories,
  getMemoriesByTag,
  getMemoryStatistics,
  reflectMemory,
  getImportanceScores,
  getMemoryHierarchy,
  extractMemoriesFromConversation,
};
