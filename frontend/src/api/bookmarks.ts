/**
 * Bookmarks API client
 * 
 * Provides CRUD operations for user bookmarks.
 */
import { get, post, put, del } from './client-simple';

export interface Bookmark {
  id: string;
  title: string;
  url: string;
  description?: string;
  tags: string[];
  created_at: string;
  user_id: string;
}

/**
 * Fetch bookmarks list
 * @param limit Optional limit
 * @param offset Optional offset
 */
export const listBookmarks = async (limit = 100, offset = 0) => {
  return get<Bookmark[]>(`/bookmarks?limit=${limit}&offset=${offset}`);
};

/**
 * Create a new bookmark
 */
export const createBookmark = async (bookmark: Omit<Bookmark, 'id' | 'created_at' | 'user_id'>) => {
  return post<Bookmark>('/bookmarks', bookmark);
};

/**
 * Update an existing bookmark
 */
export const updateBookmark = async (id: string, updates: Partial<Omit<Bookmark, 'id' | 'created_at' | 'user_id'>>) => {
  return put<Bookmark>(`/bookmarks/${id}`, updates);
};

/**
 * Delete a bookmark
 */
export const deleteBookmark = async (id: string) => {
  return del<{ success: boolean }>(`/bookmarks/${id}`);
};
