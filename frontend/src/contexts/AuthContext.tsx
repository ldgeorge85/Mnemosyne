/**
 * Authentication Context
 * 
 * Provides centralized authentication state management with token validation,
 * refresh handling, and secure token storage.
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useToast } from '@chakra-ui/react';
import { apiClient } from '../api/client';

/**
 * User interface
 */
export interface User {
  id: string;
  username: string;
  email: string;
  created_at: string;
  updated_at: string;
}

/**
 * Authentication state interface
 */
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

/**
 * Authentication context interface
 */
interface AuthContextType extends AuthState {
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  register: (username: string, email: string, password: string) => Promise<boolean>;
  validateToken: () => Promise<boolean>;
  refreshToken: () => Promise<boolean>;
}

/**
 * Authentication context
 */
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Authentication provider props
 */
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Authentication provider component
 */
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
  });
  
  const toast = useToast();

  /**
   * Update authentication state
   */
  const updateAuthState = (updates: Partial<AuthState>) => {
    setState(prev => ({ ...prev, ...updates }));
  };

  /**
   * Set authentication data
   */
  const setAuthData = (user: User) => {
    // No longer storing tokens in localStorage - using httpOnly cookies
    updateAuthState({
      token: 'cookie-based', // Placeholder to indicate auth is active
      user,
      isAuthenticated: true,
      isLoading: false,
    });
  };

  /**
   * Clear authentication data
   */
  const clearAuthData = () => {
    // Clear refresh token from localStorage
    localStorage.removeItem('refresh_token');
    // Cookies handled by backend
    updateAuthState({
      token: null,
      user: null,
      isAuthenticated: false,
      isLoading: false,
    });
  };

  /**
   * Validate token with backend
   */
  const validateToken = async (): Promise<boolean> => {
    try {
      // Call backend to validate token using cookie-based auth
      const response = await apiClient.get('/auth/me');

      if (response.status === 200 && response.data) {
        // Map backend user structure to frontend structure
        const backendUser = response.data.data || response.data;
        const userData: User = {
          id: backendUser.id || backendUser.user_id,
          username: backendUser.username,
          email: backendUser.email,
          created_at: backendUser.created_at || new Date().toISOString(),
          updated_at: backendUser.updated_at || new Date().toISOString(),
        };
        setAuthData(userData);
        return true;
      } else {
        clearAuthData();
        return false;
      }
    } catch (error) {
      clearAuthData();
      return false;
    }
  };

  /**
   * Refresh authentication token
   */
  const refreshToken = async (): Promise<boolean> => {
    try {
      // Need to get refresh token from somewhere - for now skip if not available
      // The backend handles cookies automatically
      const refreshTokenValue = localStorage.getItem('refresh_token');
      if (!refreshTokenValue) {
        // No refresh token available, need to re-login
        return false;
      }
      
      const response = await apiClient.post('/auth/refresh', {
        refresh_token: refreshTokenValue,
        method: 'static',
      });
      
      if (response.status === 200) {
        // Store new refresh token if provided
        if (response.data?.refresh_token) {
          localStorage.setItem('refresh_token', response.data.refresh_token);
        }
        // Cookies are automatically updated by backend
        // Just update our state to indicate we're still authenticated
        updateAuthState({ token: 'cookie-based' });
        return true;
      } else {
        clearAuthData();
        return false;
      }
    } catch (error) {
      clearAuthData();
      return false;
    }
  };

  /**
   * Login user
   */
  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      updateAuthState({ isLoading: true });

      // Send JSON body matching backend expectations
      const response = await apiClient.post('/auth/login', {
        username,
        password,
        method: 'static', // Using static auth method for development
      });

      if (response.status === 200) {
        // Store refresh token if provided
        if (response.data?.refresh_token) {
          localStorage.setItem('refresh_token', response.data.refresh_token);
        }
        
        // Cookies are set by backend automatically
        // Get user information
        const userResponse = await apiClient.get('/auth/me');

        if (userResponse.status === 200 && userResponse.data) {
          // Map backend user structure to frontend structure
          const backendUser = userResponse.data.data || userResponse.data;
          const userData: User = {
            id: backendUser.id || backendUser.user_id,
            username: backendUser.username,
            email: backendUser.email,
            created_at: backendUser.created_at || new Date().toISOString(),
            updated_at: backendUser.updated_at || new Date().toISOString(),
          };
          setAuthData(userData);
          
          toast({
            title: 'Login successful',
            description: `Welcome back, ${userData.username}!`,
            status: 'success',
            duration: 3000,
            isClosable: true,
          });
          
          return true;
        }
      }

      toast({
        title: 'Login failed',
        description: 'Invalid username or password',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      
      clearAuthData();
      return false;
    } catch (error: any) {
      
      const message = error.response?.data?.detail || 'Login failed. Please try again.';
      toast({
        title: 'Login error',
        description: message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      
      clearAuthData();
      return false;
    }
  };

  /**
   * Register new user
   */
  const register = async (username: string, email: string, password: string): Promise<boolean> => {
    try {
      updateAuthState({ isLoading: true });

      const response = await apiClient.post('/auth/register', {
        username,
        email,
        password,
      });

      if (response.success) {
        toast({
          title: 'Registration successful',
          description: 'Please log in with your new account',
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
        
        updateAuthState({ isLoading: false });
        return true;
      }

      toast({
        title: 'Registration failed',
        description: 'Please check your information and try again',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      
      updateAuthState({ isLoading: false });
      return false;
    } catch (error: any) {
      
      let message = 'Registration failed. Please try again.';
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          message = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) {
          message = error.response.data.detail.map((err: any) => err.msg).join(', ');
        }
      }
      
      toast({
        title: 'Registration error',
        description: message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      
      updateAuthState({ isLoading: false });
      return false;
    }
  };

  /**
   * Logout user
   */
  const logout = async () => {
    try {
      // Call backend to clear cookies
      await apiClient.post('/auth/logout');
    } catch (error) {
      // Continue with logout even if backend call fails
    }
    
    clearAuthData();
    toast({
      title: 'Logged out',
      description: 'You have been successfully logged out',
      status: 'info',
      duration: 3000,
      isClosable: true,
    });
  };

  /**
   * Initialize authentication state on mount
   */
  useEffect(() => {
    const initializeAuth = async () => {
      // Try to validate existing session via cookies
      const isValid = await validateToken();
      if (!isValid) {
        updateAuthState({ isLoading: false });
      }
    };

    initializeAuth();
  }, []);

  /**
   * Set up automatic token refresh
   */
  useEffect(() => {
    if (!state.isAuthenticated) return;

    // Refresh token every 25 minutes (assuming 30-minute expiry)
    const refreshInterval = setInterval(async () => {
      const success = await refreshToken();
      if (!success) {
        toast({
          title: 'Session expired',
          description: 'Please log in again',
          status: 'warning',
          duration: 5000,
          isClosable: true,
        });
      }
    }, 25 * 60 * 1000);

    return () => clearInterval(refreshInterval);
  }, [state.isAuthenticated]);

  const contextValue: AuthContextType = {
    ...state,
    login,
    logout,
    register,
    validateToken,
    refreshToken,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

/**
 * Hook to use authentication context
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
