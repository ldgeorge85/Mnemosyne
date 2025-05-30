/**
 * Health API service
 * 
 * This service provides functions to check the health status of the backend API.
 */
import { get } from './client';
import { HealthStatus } from '../types';

/**
 * Get basic health status from the API
 * 
 * @returns Promise resolving to the health status response
 */
export const getHealthStatus = () => {
  return get<HealthStatus>('/health');
};

/**
 * Get detailed health status with component information
 * 
 * @returns Promise resolving to the detailed health status response
 */
export const getDetailedHealthStatus = () => {
  return get<HealthStatus>('/health/detailed');
};

export default {
  getHealthStatus,
  getDetailedHealthStatus
};
