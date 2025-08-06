/**
 * Authentication Store
 * 
 * This module provides a Zustand store for managing authentication state,
 * including login, logout, and user profile data.
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '../types';

/**
 * Authentication store state interface
 */
interface AuthState {
  // Authentication state
  isAuthenticated: boolean;
  token: string | null;
  user: User | null;
  
  // Actions
  login: (token: string, user: User) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
}

/**
 * Create the authentication store with persistence
 */
const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      // Initial state
      isAuthenticated: false,
      token: null,
      user: null,
      
      // Login action
      login: (token, user) => set({
        isAuthenticated: true,
        token,
        user,
      }),
      
      // Logout action
      logout: () => set({
        isAuthenticated: false,
        token: null,
        user: null,
      }),
      
      // Update user data
      updateUser: (userData) => set((state) => ({
        user: state.user ? { ...state.user, ...userData } : null,
      })),
    }),
    {
      name: 'mnemosyne-auth-storage',
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
        token: state.token,
        user: state.user,
      }),
    }
  )
);

export default useAuthStore;
