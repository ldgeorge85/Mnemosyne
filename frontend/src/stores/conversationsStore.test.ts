import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useConversationsStore } from './conversationsStore';
import { apiClient } from '../services/api/client';

// Mock the API client
vi.mock('../services/api/client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  }
}));

describe('useConversationsStore', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    // Reset the store state between tests
    const { result } = renderHook(() => useConversationsStore());
    act(() => {
      result.current.reset();
    });
  });

  it('should initialize with default values', () => {
    const { result } = renderHook(() => useConversationsStore());
    
    expect(result.current.conversations).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it('should fetch conversations successfully', async () => {
    const mockConversations = [
      { id: '1', title: 'Conversation 1', created_at: '2025-06-01T12:00:00Z', updated_at: '2025-06-01T12:00:00Z' },
      { id: '2', title: 'Conversation 2', created_at: '2025-06-02T12:00:00Z', updated_at: '2025-06-02T12:00:00Z' },
    ];
    
    (apiClient.get as any).mockResolvedValue({ data: mockConversations });
    
    const { result } = renderHook(() => useConversationsStore());
    
    await act(async () => {
      await result.current.fetchConversations();
    });
    
    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/conversations');
    expect(result.current.conversations).toEqual(mockConversations);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it('should handle fetch error', async () => {
    const errorMessage = 'Network Error';
    (apiClient.get as any).mockRejectedValue(new Error(errorMessage));
    
    const { result } = renderHook(() => useConversationsStore());
    
    await act(async () => {
      await result.current.fetchConversations();
    });
    
    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/conversations');
    expect(result.current.conversations).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(errorMessage);
  });

  it('should create a conversation successfully', async () => {
    const newConversation = { id: '3', title: 'New Conversation', created_at: '2025-06-03T12:00:00Z', updated_at: '2025-06-03T12:00:00Z' };
    (apiClient.post as any).mockResolvedValue({ data: newConversation });
    
    const { result } = renderHook(() => useConversationsStore());
    
    await act(async () => {
      await result.current.createConversation('New Conversation');
    });
    
    expect(apiClient.post).toHaveBeenCalledWith('/api/v1/conversations', { title: 'New Conversation' });
    expect(result.current.conversations).toContainEqual(newConversation);
  });

  it('should delete a conversation successfully', async () => {
    const mockConversations = [
      { id: '1', title: 'Conversation 1', created_at: '2025-06-01T12:00:00Z', updated_at: '2025-06-01T12:00:00Z' },
      { id: '2', title: 'Conversation 2', created_at: '2025-06-02T12:00:00Z', updated_at: '2025-06-02T12:00:00Z' },
    ];
    
    // Setup initial state
    (apiClient.get as any).mockResolvedValue({ data: mockConversations });
    
    const { result } = renderHook(() => useConversationsStore());
    
    await act(async () => {
      await result.current.fetchConversations();
    });
    
    // Mock successful deletion
    (apiClient.delete as any).mockResolvedValue({});
    
    await act(async () => {
      await result.current.deleteConversation('1');
    });
    
    expect(apiClient.delete).toHaveBeenCalledWith('/api/v1/conversations/1');
    expect(result.current.conversations).toHaveLength(1);
    expect(result.current.conversations[0].id).toBe('2');
  });

  it('should handle delete error', async () => {
    const mockConversations = [
      { id: '1', title: 'Conversation 1', created_at: '2025-06-01T12:00:00Z', updated_at: '2025-06-01T12:00:00Z' },
    ];
    
    // Setup initial state
    (apiClient.get as any).mockResolvedValue({ data: mockConversations });
    
    const { result } = renderHook(() => useConversationsStore());
    
    await act(async () => {
      await result.current.fetchConversations();
    });
    
    // Mock deletion error
    const errorMessage = 'Failed to delete conversation';
    (apiClient.delete as any).mockRejectedValue(new Error(errorMessage));
    
    await act(async () => {
      await result.current.deleteConversation('1');
    });
    
    expect(apiClient.delete).toHaveBeenCalledWith('/api/v1/conversations/1');
    expect(result.current.error).toBe(errorMessage);
    expect(result.current.conversations).toHaveLength(1); // Conversation should still be there
  });
});
