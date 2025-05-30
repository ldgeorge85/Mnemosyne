/**
 * Store exports
 * 
 * This file exports all state stores to provide a unified import point
 * for application state management.
 */

// Import all stores
import useAuthStore from './authStore';
import useUIStore from './uiStore';
import useConversationStore from './conversationStore';

// Export all stores
export {
  useAuthStore,
  useUIStore,
  useConversationStore
};

export default {
  auth: useAuthStore,
  ui: useUIStore,
  conversation: useConversationStore
};
