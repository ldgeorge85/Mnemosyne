// Simple test to verify API client configuration
import { apiClient } from './api/client.ts';

console.log('Testing API client configuration...');
console.log('Base URL:', apiClient.defaults.baseURL);

// Test a simple API call
apiClient.get('/conversations/')
  .then(response => {
    console.log('API test successful:', response.status);
  })
  .catch(error => {
    console.error('API test failed:', error.message);
    console.error('Request URL:', error.config?.url);
    console.error('Base URL:', error.config?.baseURL);
  });
