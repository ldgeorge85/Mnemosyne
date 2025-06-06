/**
 * Shared API types
 */

/**
 * Standard API response wrapper
 */
export interface ApiResponse<T = any> {
  data: T;
  status: number;
  message?: string;
}
