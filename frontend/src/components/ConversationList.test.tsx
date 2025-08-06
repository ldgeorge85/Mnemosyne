import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import ConversationList from './ConversationList';
import { useConversationsStore } from '../stores/conversationsStore';
import { vi, describe, it, expect, beforeEach } from 'vitest';

// Mock the store
vi.mock('../stores/conversationsStore');

describe('ConversationList', () => {
  const mockConversations = [
    { id: '1', title: 'Conversation 1', created_at: '2025-06-01T12:00:00Z', updated_at: '2025-06-01T12:00:00Z' },
    { id: '2', title: 'Conversation 2', created_at: '2025-06-02T12:00:00Z', updated_at: '2025-06-02T12:00:00Z' },
    { id: '3', title: 'Conversation 3', created_at: '2025-06-03T12:00:00Z', updated_at: '2025-06-03T12:00:00Z' },
  ];

  const mockUseConversationsStore = {
    conversations: mockConversations,
    isLoading: false,
    error: null,
    fetchConversations: vi.fn(),
    createConversation: vi.fn(),
    deleteConversation: vi.fn(),
  };

  beforeEach(() => {
    (useConversationsStore as any).mockReturnValue(mockUseConversationsStore);
  });

  it('renders the conversation list', () => {
    render(
      <BrowserRouter>
        <ConversationList />
      </BrowserRouter>
    );
    
    // Check if all conversations are rendered
    expect(screen.getByText('Conversation 1')).toBeInTheDocument();
    expect(screen.getByText('Conversation 2')).toBeInTheDocument();
    expect(screen.getByText('Conversation 3')).toBeInTheDocument();
  });

  it('shows loading state when isLoading is true', () => {
    (useConversationsStore as any).mockReturnValue({
      ...mockUseConversationsStore,
      isLoading: true,
    });

    render(
      <BrowserRouter>
        <ConversationList />
      </BrowserRouter>
    );
    
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('shows error message when error exists', () => {
    (useConversationsStore as any).mockReturnValue({
      ...mockUseConversationsStore,
      error: 'Failed to fetch conversations',
    });

    render(
      <BrowserRouter>
        <ConversationList />
      </BrowserRouter>
    );
    
    expect(screen.getByText(/failed to fetch conversations/i)).toBeInTheDocument();
  });

  it('calls fetchConversations on mount', () => {
    render(
      <BrowserRouter>
        <ConversationList />
      </BrowserRouter>
    );
    
    expect(mockUseConversationsStore.fetchConversations).toHaveBeenCalled();
  });

  it('calls createConversation when new conversation button is clicked', async () => {
    const user = userEvent.setup();
    
    render(
      <BrowserRouter>
        <ConversationList />
      </BrowserRouter>
    );
    
    const newButton = screen.getByRole('button', { name: /new conversation/i });
    await user.click(newButton);
    
    expect(mockUseConversationsStore.createConversation).toHaveBeenCalled();
  });
});
