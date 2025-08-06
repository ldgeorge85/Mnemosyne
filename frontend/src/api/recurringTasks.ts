/**
 * API service for recurring tasks functionality
 * 
 * This module provides functions to interact with the recurring tasks endpoints
 * including pattern validation, task series management, and instance creation.
 */
import { get, post, put, del } from './client-simple';

export interface RecurringTaskPattern {
  pattern: string;
  preview_dates?: string[];
  is_valid?: boolean;
  error_message?: string;
}

export interface RecurringTaskInstance {
  id: string;
  master_task_id: string;
  instance_date: string;
  title: string;
  description?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface RecurringTaskSeries {
  master_task_id: string;
  recurrence_pattern: string;
  start_date: string;
  end_date?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Validate a recurrence pattern and get preview dates
 */
export const validatePattern = async (pattern: string, previewCount: number = 5): Promise<RecurringTaskPattern> => {
  try {
    const response = await post('/recurring-tasks/validate-pattern', {
      pattern,
      preview_count: previewCount
    });
    
    return {
      pattern,
      preview_dates: response.data.preview_dates,
      is_valid: response.data.is_valid,
      error_message: response.data.error_message
    };
  } catch (error) {
    return {
      pattern,
      is_valid: false,
      error_message: 'Failed to validate pattern'
    };
  }
};

/**
 * Create recurring task instances for a task
 */
export const createRecurringInstances = async (
  taskId: string, 
  pattern: string, 
  startDate: string, 
  endDate?: string
): Promise<RecurringTaskInstance[]> => {
  try {
    const response = await post(`/recurring-tasks/${taskId}/instances`, {
      recurrence_pattern: pattern,
      start_date: startDate,
      end_date: endDate
    });
    
    return response.data.instances || [];
  } catch (error) {
    throw error;
  }
};

/**
 * Update a recurring task series
 */
export const updateRecurringSeries = async (
  masterTaskId: string, 
  pattern: string, 
  startDate: string, 
  endDate?: string
): Promise<RecurringTaskSeries> => {
  try {
    const response = await put(`/recurring-tasks/${masterTaskId}/series`, {
      recurrence_pattern: pattern,
      start_date: startDate,
      end_date: endDate
    });
    
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Delete a recurring task series
 */
export const deleteRecurringSeries = async (masterTaskId: string): Promise<void> => {
  try {
    await del(`/recurring-tasks/${masterTaskId}/series`);
  } catch (error) {
    throw error;
  }
};

/**
 * Get recurring task instances for a master task
 */
export const getRecurringInstances = async (masterTaskId: string): Promise<RecurringTaskInstance[]> => {
  try {
    const response = await get(`/recurring-tasks/${masterTaskId}/instances`);
    return response.data.instances || [];
  } catch (error) {
    return [];
  }
};

/**
 * Common recurrence patterns for UI selection
 */
export const COMMON_PATTERNS = [
  { label: 'Daily', value: 'daily' },
  { label: 'Weekly', value: 'weekly' },
  { label: 'Monthly', value: 'monthly' },
  { label: 'Yearly', value: 'yearly' },
  { label: 'Weekdays', value: 'weekdays' },
  { label: 'Weekends', value: 'weekends' },
  { label: 'Every 2 days', value: 'every 2 days' },
  { label: 'Every 2 weeks', value: 'every 2 weeks' },
  { label: 'Every 3 months', value: 'every 3 months' },
  { label: 'Monday, Wednesday, Friday', value: 'every monday,wednesday,friday' }
];
