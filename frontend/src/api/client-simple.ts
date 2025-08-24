// NUCLEAR SIMPLE API CLIENT - NO AXIOS BULLSHIT
const BASE_URL = '/api/v1';

interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
  success: boolean;
}

async function makeRequest<T>(
  method: string,
  url: string,
  data?: any,
  options?: any
): Promise<ApiResponse<T>> {
  const token = localStorage.getItem('token'); // Changed from 'access_token' to 'token'
  const isFormData = data instanceof URLSearchParams;
  const response = await fetch(`${BASE_URL}${url}`, {
    method,
    credentials: 'same-origin', // Include cookies with requests
    headers: {
      'Content-Type': options?.headers?.['Content-Type'] || 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options?.headers,
    },
    ...(data && { body: isFormData ? data : JSON.stringify(data) }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorText}`);
  }

  const responseData = await response.json();
  
  return {
    data: responseData,
    status: response.status,
    message: response.statusText,
    success: response.ok,
  };
}

export const get = async <T>(url: string): Promise<ApiResponse<T>> => {
  const token = localStorage.getItem('token'); // Changed from 'access_token' to 'token'
  const response = await fetch(`${BASE_URL}${url}`, {
    method: 'GET',
    credentials: 'same-origin', // Include cookies with requests
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorText}`);
  }

  const data: T = await response.json();
  return {
    data,
    status: response.status,
    message: response.statusText,
    success: response.ok,
  };
};

export const post = <T>(url: string, data?: any, options?: any): Promise<ApiResponse<T>> => {
  return makeRequest<T>('POST', url, data, options);
};

export const put = <T>(url: string, data?: any): Promise<ApiResponse<T>> => {
  return makeRequest<T>('PUT', url, data);
};

export const del = <T>(url: string): Promise<ApiResponse<T>> => {
  return makeRequest<T>('DELETE', url);
};
