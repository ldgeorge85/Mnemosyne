/**
 * UI Store
 * 
 * This module provides a Zustand store for managing UI state,
 * including theme preferences, sidebar visibility, and global UI settings.
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * UI store state interface
 */
interface UIState {
  // Theme settings
  colorMode: 'light' | 'dark';
  toggleColorMode: () => void;
  
  // Sidebar state
  isSidebarOpen: boolean;
  openSidebar: () => void;
  closeSidebar: () => void;
  toggleSidebar: () => void;
  
  // Global loading state
  isLoading: boolean;
  setLoading: (isLoading: boolean) => void;
  
  // Toast messages queue
  toasts: Array<{
    id: string;
    message: string;
    type: 'info' | 'success' | 'warning' | 'error';
    duration?: number;
  }>;
  addToast: (message: string, type: 'info' | 'success' | 'warning' | 'error', duration?: number) => void;
  removeToast: (id: string) => void;
}

/**
 * Create the UI store with persistence for theme settings
 */
const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      // Initial theme state (default to light mode)
      colorMode: 'light',
      toggleColorMode: () => set((state) => ({
        colorMode: state.colorMode === 'light' ? 'dark' : 'light',
      })),
      
      // Initial sidebar state
      isSidebarOpen: false,
      openSidebar: () => set({ isSidebarOpen: true }),
      closeSidebar: () => set({ isSidebarOpen: false }),
      toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
      
      // Initial loading state
      isLoading: false,
      setLoading: (isLoading) => set({ isLoading }),
      
      // Toast messages
      toasts: [],
      addToast: (message, type, duration = 3000) => set((state) => ({
        toasts: [
          ...state.toasts,
          {
            id: `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            message,
            type,
            duration,
          },
        ],
      })),
      removeToast: (id) => set((state) => ({
        toasts: state.toasts.filter((toast) => toast.id !== id),
      })),
    }),
    {
      name: 'mnemosyne-ui-storage',
      partialize: (state) => ({
        colorMode: state.colorMode,
      }),
    }
  )
);

export default useUIStore;
