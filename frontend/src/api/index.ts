/**
 * API module exports
 * 
 * This file exports all API services to provide a unified API interface.
 */

import apiClient from './client';
import healthService from './health';

// Export all service modules
export {
  apiClient,
  healthService
};

// Export default object with all services
export default {
  client: apiClient,
  health: healthService
};
