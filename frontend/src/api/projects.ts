/**
 * Projects API client
 */
import { get, post, put, del } from './client-simple';

export interface Project {
  id: string;
  name: string;
  description: string;
  status: 'planning' | 'active' | 'on-hold' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  progress: number;
  start_date: string;
  due_date?: string;
  team_members: string[];
  tasks_count: number;
  completed_tasks: number;
  created_at: string;
}

export const listProjects = async () => {
  return get<Project[]>('/projects');
};

export const createProject = async (data: Omit<Project, 'id' | 'created_at' | 'progress' | 'tasks_count' | 'completed_tasks'>) => {
  return post<Project>('/projects', data);
};

export const updateProject = async (id: string, updates: Partial<Project>) => {
  return put<Project>(`/projects/${id}`, updates);
};

export const deleteProject = async (id: string) => {
  return del<{ success: boolean }>(`/projects/${id}`);
};
