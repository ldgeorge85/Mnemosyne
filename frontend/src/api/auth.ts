/**
 * Authentication API client
 * 
 * This module provides functions for user authentication operations.
 */
import { post } from './client-simple';

/**
 * Login request interface
 */
export interface LoginRequest {
  username: string;
  password: string;
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
    // Use dev endpoint for now since main auth has DB issues
    const loginData = {
      username: credentials.username,
      email: credentials.username.includes('@') ? credentials.username : `${credentials.username}@example.com`,
      password: credentials.password
    };
    
    return post<LoginResponse>('/auth/dev-login', loginData, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
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
    // Get refresh token from cookie if available
    const cookies = document.cookie.split(';');
    let refreshToken = null;
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'refresh_token') {
        refreshToken = decodeURIComponent(value);
        break;
      }
    }
    
    // Send refresh token in body to invalidate it
    const response = await post('/auth/logout', refreshToken ? { refresh_token: refreshToken } : {});
    
    // Clear all auth-related cookies
    document.cookie = 'access_token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    document.cookie = 'refresh_token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    
    return response;
  } catch (error) {
    // Even if logout fails, clear cookies
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
  return post('/auth/me');
};

export default {
  login,
  register,
  logout,
  getCurrentUser,
};
