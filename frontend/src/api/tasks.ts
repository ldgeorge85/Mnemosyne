/**
 * Tasks API client
 * 
 * This module provides functions for task management operations.
 */
import { get, post, put, del } from './client-simple';

/**
 * Task enums
 */
export enum TaskStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
  ON_HOLD = 'on_hold'
}

export enum TaskPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent'
}

export enum QuestType {
  TUTORIAL = 'tutorial',
  DAILY = 'daily',
  SOLO = 'solo',
  PARTY = 'party',
  RAID = 'raid',
  EPIC = 'epic',
  CHALLENGE = 'challenge'
}

/**
 * Task interfaces
 */
export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  due_date?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  user_id: string;
  parent_task_id?: string;
  tags?: string[];
  metadata?: {
    source?: string;
    conversation_id?: string;
    extraction_confidence?: number;
    task_type?: string;
    is_recurring?: boolean;
    recurrence_pattern?: string;
    linked_memories?: Array<{
      memory_id: string;
      title: string;
      relevance: number;
    }>;
    [key: string]: any;
  };
  estimated_duration?: number;
  actual_duration?: number;
  // Game mechanics
  quest_type?: QuestType;
  difficulty?: number;
  experience_points?: number;
  reputation_impact?: Record<string, number>;
  value_impact?: Record<string, number>;
  skill_development?: Record<string, number>;
  started_at?: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string;
  parent_task_id?: string;
  tags?: string[];
  metadata?: Record<string, any>;
  estimated_duration?: number;
  // Game mechanics
  quest_type?: QuestType;
  difficulty?: number;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string;
  tags?: string[];
  metadata?: Record<string, any>;
  estimated_duration?: number;
  actual_duration?: number;
  is_active?: boolean;
}

export interface TaskLog {
  id: string;
  task_id: string;
  action: string;
  description?: string;
  created_at: string;
  user_id: string;
  metadata?: Record<string, any>;
}

export interface TaskLogCreate {
  task_id: string;
  action: string;
  description?: string;
  metadata?: Record<string, any>;
}

export interface TaskWithLogs extends Task {
  logs: TaskLog[];
  logs_count: number;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
  limit: number;
  offset: number;
}

export interface TaskSearchParams {
  query: string;
  limit?: number;
  offset?: number;
  include_inactive?: boolean;
  user_id?: string;
}

/**
 * List tasks for the current user
 */
export const listTasks = async (params?: {
  limit?: number;
  offset?: number;
  include_inactive?: boolean;
  status?: TaskStatus[];
  priority?: TaskPriority[];
  tags?: string[];
  due_date_start?: string;
  due_date_end?: string;
}) => {
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());
  if (params?.include_inactive) queryParams.append('include_inactive', params.include_inactive.toString());
  if (params?.status) params.status.forEach(s => queryParams.append('status', s));
  if (params?.priority) params.priority.forEach(p => queryParams.append('priority', p));
  if (params?.tags) params.tags.forEach(t => queryParams.append('tags', t));
  if (params?.due_date_start) queryParams.append('due_date_start', params.due_date_start);
  if (params?.due_date_end) queryParams.append('due_date_end', params.due_date_end);
  
  const url = `/tasks/${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  const response = await get<TaskListResponse>(url);
  return response.data;
};

/**
 * Get a specific task by ID
 */
export const getTask = async (taskId: string) => {
  return get<Task>(`/tasks/${taskId}`);
};

/**
 * Get a task with its logs
 */
export const getTaskWithLogs = async (taskId: string, params?: {
  limit?: number;
  offset?: number;
}) => {
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());
  
  const url = `/tasks/${taskId}/logs${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  return get<TaskWithLogs>(url);
};

/**
 * Create a new task
 */
export const createTask = async (taskData: TaskCreate) => {
  return post<Task>('/tasks/', taskData);
};

/**
 * Update an existing task
 */
export const updateTask = async (taskId: string, taskData: TaskUpdate) => {
  return put<Task>(`/tasks/${taskId}`, taskData);
};

/**
 * Delete a task
 */
export const deleteTask = async (taskId: string, hardDelete: boolean = false) => {
  const queryParams = hardDelete ? '?hard_delete=true' : '';
  return del(`/tasks/${taskId}${queryParams}`);
};

/**
 * Get subtasks for a task
 */
export const getSubtasks = async (taskId: string, params?: {
  limit?: number;
  offset?: number;
  include_inactive?: boolean;
}) => {
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());
  if (params?.include_inactive) queryParams.append('include_inactive', params.include_inactive.toString());
  
  const url = `/tasks/${taskId}/subtasks${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  return get<TaskListResponse>(url);
};

/**
 * Create a subtask
 */
export const createSubtask = async (parentTaskId: string, taskData: TaskCreate) => {
  return post<Task>(`/tasks/${parentTaskId}/subtasks`, taskData);
};

/**
 * Create a task log entry
 */
export const createTaskLog = async (taskId: string, logData: TaskLogCreate) => {
  return post<TaskLog>(`/tasks/${taskId}/logs`, logData);
};

/**
 * Get task logs
 */
export const getTaskLogs = async (taskId: string, params?: {
  limit?: number;
  offset?: number;
}) => {
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());
  
  const url = `/tasks/${taskId}/logs${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  return get<TaskLog[]>(url);
};

/**
 * Search tasks
 */
export const searchTasks = async (searchParams: TaskSearchParams) => {
  return post<Task[]>('/tasks/search', searchParams);
};

/**
 * Task Intelligence Types
 */
export interface TaskExtractionResult {
  conversation_id: string;
  extracted_count: number;
  created_count: number;
  tasks: Array<{
    id?: string;
    title: string;
    priority: string;
    due_date?: string;
    extracted_data: any;
  }>;
}

export interface TaskReminder {
  task_id: string;
  title: string;
  description?: string;
  priority: TaskPriority;
  due_date: string;
  hours_until_due: number;
  reminder_type: 'urgent' | 'soon' | 'today' | 'upcoming';
  context?: Array<{
    memory_id: string;
    title: string;
    relevance: number;
  }>;
}

export interface TaskSuggestion {
  type: 'recurring' | 'follow_up' | 'memory_based' | 'time_based';
  title: string;
  description: string;
  suggested_due_date: string;
  priority: TaskPriority;
  confidence: number;
  reason: string;
  parent_task_id?: string;
  memory_id?: string;
}

export interface DailySummary {
  date: string;
  tasks_today: number;
  tasks_completed_24h: number;
  tasks_overdue: number;
  today_breakdown: {
    high_priority: number;
    medium_priority: number;
    low_priority: number;
  };
  tasks: {
    today: Array<{
      id: string;
      title: string;
      priority: TaskPriority;
      due_time?: string;
      status: TaskStatus;
    }>;
    overdue: Array<{
      id: string;
      title: string;
      priority: TaskPriority;
      days_overdue: number;
    }>;
    completed_recently: Array<{
      id: string;
      title: string;
      completed_at: string;
    }>;
  };
  insights?: {
    patterns: string[];
    suggestions: string[];
  };
}

/**
 * Extract tasks from a conversation
 */
export const extractTasksFromConversation = async (conversationId: string, autoCreate: boolean = true) => {
  const queryParams = new URLSearchParams();
  queryParams.append('auto_create', autoCreate.toString());
  
  return post<TaskExtractionResult>(`/tasks/extract/${conversationId}?${queryParams.toString()}`, {});
};

/**
 * Get upcoming task reminders
 */
export const getUpcomingReminders = async (hoursAhead: number = 24) => {
  const queryParams = new URLSearchParams();
  queryParams.append('hours_ahead', hoursAhead.toString());
  
  return get<TaskReminder[]>(`/tasks/reminders?${queryParams.toString()}`);
};

/**
 * Get daily task summary
 */
export const getDailySummary = async (includeMemories: boolean = true) => {
  const queryParams = new URLSearchParams();
  queryParams.append('include_memories', includeMemories.toString());
  
  return get<DailySummary>(`/tasks/daily-summary?${queryParams.toString()}`);
};

/**
 * Get task suggestions
 */
export const getTaskSuggestions = async (includeContext: boolean = true) => {
  const queryParams = new URLSearchParams();
  queryParams.append('include_context', includeContext.toString());
  
  return get<TaskSuggestion[]>(`/tasks/suggestions?${queryParams.toString()}`);
};

/**
 * Start a task (mark as in-progress)
 */
export const startTask = async (taskId: string) => {
  return post<Task>(`/tasks/${taskId}/start`, {});
};

/**
 * Complete a task with XP calculation
 */
export interface TaskCompleteResponse {
  task: Task;
  experience_gained: number;
  reputation_changes: Record<string, number>;
  achievements_unlocked?: string[];
}

export const completeTask = async (taskId: string, actual_duration?: number) => {
  return post<TaskCompleteResponse>(`/tasks/${taskId}/complete`, { 
    actual_duration 
  });
};

export default {
  listTasks,
  getTask,
  getTaskWithLogs,
  createTask,
  updateTask,
  deleteTask,
  getSubtasks,
  createSubtask,
  createTaskLog,
  getTaskLogs,
  searchTasks,
  extractTasksFromConversation,
  getUpcomingReminders,
  getDailySummary,
  getTaskSuggestions,
  startTask,
  completeTask,
};
