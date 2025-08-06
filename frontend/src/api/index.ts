/**
 * API Module Exports
 * 
 * This module re-exports all API functions and clients for easy importing
 * throughout the application.
 */
export { get, post, put, del } from "./client-simple";

// Re-export API modules
export * from "./conversations";
export * from "./auth";
export * from "./tasks";
export * from "./memories";
export * from "./health";

// Legacy exports for compatibility
import { get, post, put, del } from "./client-simple";
import { healthService, getHealthStatus } from "./health";
import conversationsDefault from "./conversations";

export const client = { get, post, put, del };
export const apiClient = { get, post, put, del };
export const conversationsService = conversationsDefault;

// Create a default export with all services
export default {
  client: { get, post, put, del },
  apiClient: { get, post, put, del },
  health: healthService,
  conversations: conversationsDefault
};
