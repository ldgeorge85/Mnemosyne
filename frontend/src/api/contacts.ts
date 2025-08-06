/**
 * Contacts API client
 */
import { get, post, put, del } from './client-simple';

export interface Contact {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  role?: string;
  avatar?: string;
  tags: string[];
  notes?: string;
  last_contact: string;
  created_at: string;
}

export const listContacts = async () => {
  return get<Contact[]>('/contacts/');
};

export const createContact = async (data: Omit<Contact, 'id' | 'created_at' | 'last_contact'>) => {
  return post<Contact>('/contacts/', data);
};

export const updateContact = async (id: string, updates: Partial<Contact>) => {
  return put<Contact>(`/contacts/${id}`, updates);
};

export const deleteContact = async (id: string) => {
  return del<{ success: boolean }>(`/contacts/${id}`);
};
