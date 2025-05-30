/**
 * API client for making requests to the backend
 * 
 * This module provides a centralized way to make API requests to the backend
 * with consistent error handling, authentication, and response formatting.
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiResponse } from '../types';

// Create an axios instance with default configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor for adding authentication tokens and other headers
 */
apiClient.interceptors.request.use(
  (config) => {
    // Get the token from local storage
    const token = localStorage.getItem('token');
    
    // If token exists, add it to the headers
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor for handling common error cases
 */
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle unauthorized errors (401)
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

/**
 * Generic request function with proper typing
 * 
 * @param config - Axios request configuration
 * @returns Promise resolving to the response data
 */
export const request = async <T>(config: AxiosRequestConfig): Promise<ApiResponse<T>> => {
  try {
    const response: AxiosResponse<ApiResponse<T>> = await apiClient(config);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      return error.response.data as ApiResponse<T>;
    }
    
    // Create a standardized error response
    return {
      data: {} as T,
      status: 500,
      message: 'An unexpected error occurred',
    };
  }
};

/**
 * GET request helper function
 * 
 * @param url - Endpoint URL
 * @param config - Additional Axios configuration
 * @returns Promise resolving to the response data
 */
export const get = <T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
  return request<T>({ ...config, method: 'GET', url });
};

/**
 * POST request helper function
 * 
 * @param url - Endpoint URL
 * @param data - Request payload
 * @param config - Additional Axios configuration
 * @returns Promise resolving to the response data
 */
export const post = <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
  return request<T>({ ...config, method: 'POST', url, data });
};

/**
 * PUT request helper function
 * 
 * @param url - Endpoint URL
 * @param data - Request payload
 * @param config - Additional Axios configuration
 * @returns Promise resolving to the response data
 */
export const put = <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
  return request<T>({ ...config, method: 'PUT', url, data });
};

/**
 * DELETE request helper function
 * 
 * @param url - Endpoint URL
 * @param config - Additional Axios configuration
 * @returns Promise resolving to the response data
 */
export const del = <T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
  return request<T>({ ...config, method: 'DELETE', url });
};

export default {
  get,
  post,
  put,
  delete: del,
};
