/**
 * Authentication API client
 * 
 * This module provides functions for user authentication operations.
 */
import { post, get } from './client-simple';

/**
 * Login request interface
 */
export interface LoginRequest {
  username: string;
  password: string;
  method?: string;  // Auth method (e.g., 'static')
}

/**
 * Login response interface (matches backend Token schema)
 */
export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

/**
 * Registration request interface
 */
export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

/**
 * Login user
 * @param credentials User login credentials
 * @returns Promise resolving to login response with tokens
 */
export const login = async (credentials: LoginRequest) => {
  try {
    // Use the proper auth endpoint with AuthManager
    const loginData = {
      username: credentials.username,
      password: credentials.password,
      method: credentials.method || 'static'  // Default to static auth method
    };
    
    const response = await post<LoginResponse>('/auth/login', loginData, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    // Store tokens in localStorage
    if (response.access_token) {
      localStorage.setItem('token', response.access_token);
    }
    if (response.refresh_token) {
      localStorage.setItem('refresh_token', response.refresh_token);
    }
    
    return response;
  } catch (error: any) {
    // Enhance error messages for better UX
    if (error.response?.status === 401) {
      throw new Error('Invalid username or password');
    } else if (error.response?.status === 403) {
      throw new Error('Your account has been deactivated');
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timed out. Please try again.');
    } else if (!navigator.onLine) {
      throw new Error('No internet connection');
    }
    throw error;
  }
};

/**
 * Register new user
 * @param userData User registration data
 * @returns Promise resolving to the created user
 */
export const register = async (userData: RegisterRequest) => {
  return post('/auth/register', userData);
};

/**
 * Logout user
 */
export const logout = async () => {
  try {
    // Get refresh token from localStorage
    const refreshToken = localStorage.getItem('refresh_token');
    
    // Send logout request to backend
    const response = await post('/auth/logout', refreshToken ? { refresh_token: refreshToken } : {});
    
    // Clear tokens from localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    
    // Clear any auth-related cookies (backend handles httpOnly cookies)
    document.cookie = 'access_token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    document.cookie = 'refresh_token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    
    return response;
  } catch (error) {
    // Even if logout fails, clear local storage
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    document.cookie = 'access_token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    document.cookie = 'refresh_token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    throw error;
  }
};

/**
 * Get current user info
 * @returns Promise resolving to current user data
 */
export const getCurrentUser = async () => {
  return get('/auth/me');
};

/**
 * Refresh access token
 * @returns Promise resolving to new tokens
 */
export const refreshToken = async () => {
  const refresh_token = localStorage.getItem('refresh_token');
  if (!refresh_token) {
    throw new Error('No refresh token available');
  }
  
  const response = await post<LoginResponse>('/auth/refresh', {
    refresh_token,
    method: 'static'
  });
  
  // Store new tokens
  if (response.access_token) {
    localStorage.setItem('token', response.access_token);
  }
  if (response.refresh_token) {
    localStorage.setItem('refresh_token', response.refresh_token);
  }
  
  return response;
};

export default {
  login,
  register,
  logout,
  getCurrentUser,
  refreshToken,
};
