/**
 * API module index file
 * Re-exports all API services for clean imports
 */

// Import and re-export all API services
export { client, apiClient, get, post, put, del } from "./client";
export { healthService, getHealthStatus } from "./health";
export { default as conversationsService } from "./conversations";

// Import services
import { client as clientService } from "./client";
import { healthService } from "./health";
import conversationsDefault from "./conversations";

// Create a default export with all services
const api = {
  client: clientService,
  health: healthService,
  conversations: conversationsDefault
};

// Export default API object for compatibility
export default api;
