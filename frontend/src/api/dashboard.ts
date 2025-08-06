/**
 * Dashboard API client
 * 
 * This module provides functions for fetching dashboard statistics and recent activity data.
 */
import { getConversations } from './conversations';
import { listMemories } from './memories';
import { listTasks } from './tasks';

/**
 * Dashboard statistics interface
 */
export interface DashboardStats {
  conversations: {
    total: number;
    recent: number;
    percentChange: number;
  };
  memories: {
    total: number;
    recent: number;
    percentChange: number;
  };
  tasks: {
    total: number;
    completed: number;
    pending: number;
    percentChange: number;
  };
}

/**
 * Recent activity item interface
 */
export interface ActivityItem {
  id: string;
  title: string;
  description?: string;
  type: 'conversation' | 'memory' | 'task' | 'completion';
  date: string;
  createdAt: string;
}

/**
 * Dashboard data interface
 */
export interface DashboardData {
  stats: DashboardStats;
  recentConversations: Array<{
    id: string;
    title: string;
    date: string;
  }>;
  importantMemories: Array<{
    id: string;
    title: string;
    date: string;
  }>;
  upcomingTasks: Array<{
    id: string;
    title: string;
    date: string;
  }>;
  recentActivity: ActivityItem[];
}

/**
 * Fetch dashboard statistics by aggregating data from various endpoints
 */
export const getDashboardStats = async (): Promise<DashboardStats> => {
  try {
    // Fetch data from all endpoints in parallel
    const [conversationsResponse, memoriesResponse, tasksResponse] = await Promise.all([
      getConversations(50, 0).catch(() => ({ success: false, data: { items: [], total: 0 } })),
      listMemories({ limit: 50, offset: 0 }).catch(() => ({ success: false, data: [] })),
      listTasks().catch(() => ({ success: false, data: { tasks: [], total: 0 } }))
    ]);

    // Calculate conversation stats
    const conversations = conversationsResponse.success ? conversationsResponse.data : { items: [], total: 0 };
    const recentConversations = conversations.items.filter((conv: any) => {
      const createdAt = new Date(conv.createdAt || conv.created_at);
      const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
      return createdAt > dayAgo;
    }).length;

    // Calculate memory stats
    const memories = memoriesResponse.success ? memoriesResponse.data : [];
    const recentMemories = memories.filter((memory: any) => {
      const createdAt = new Date(memory.createdAt || memory.created_at);
      const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
      return createdAt > dayAgo;
    }).length;

    // Calculate task stats
    const tasks = tasksResponse.success ? tasksResponse.data : { tasks: [], total: 0 };
    const completedTasks = tasks.tasks.filter((task: any) => 
      task.status === 'completed' || task.status === 'Completed'
    ).length;
    const pendingTasks = tasks.total - completedTasks;

    return {
      conversations: {
        total: conversations.total,
        recent: recentConversations,
        percentChange: Math.round((recentConversations / Math.max(conversations.total, 1)) * 100)
      },
      memories: {
        total: memories.length,
        recent: recentMemories,
        percentChange: Math.round((recentMemories / Math.max(memories.length, 1)) * 100)
      },
      tasks: {
        total: tasks.total,
        completed: completedTasks,
        pending: pendingTasks,
        percentChange: Math.round((completedTasks / Math.max(tasks.total, 1)) * 100)
      }
    };
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    // Return default stats on error
    return {
      conversations: { total: 0, recent: 0, percentChange: 0 },
      memories: { total: 0, recent: 0, percentChange: 0 },
      tasks: { total: 0, completed: 0, pending: 0, percentChange: 0 }
    };
  }
};

/**
 * Fetch recent conversations for dashboard
 */
export const getRecentConversations = async (limit = 3) => {
  try {
    const response = await getConversations(limit, 0);
    if (response.success && response.data.items) {
      return response.data.items.map((conv: any) => ({
        id: conv.id,
        title: conv.title || 'Untitled Conversation',
        date: formatRelativeDate(conv.createdAt || conv.created_at)
      }));
    }
    return [];
  } catch (error) {
    console.error('Error fetching recent conversations:', error);
    return [];
  }
};

/**
 * Fetch important memories for dashboard
 */
export const getImportantMemories = async (limit = 3) => {
  try {
    const response = await listMemories({ limit, offset: 0 });
    if (response.success && response.data) {
      return response.data
        .filter((memory: any) => memory.importance_score > 0.7) // Filter for important memories
        .slice(0, limit)
        .map((memory: any) => ({
          id: memory.id,
          title: memory.content.substring(0, 50) + (memory.content.length > 50 ? '...' : ''),
          date: formatRelativeDate(memory.createdAt || memory.created_at)
        }));
    }
    return [];
  } catch (error) {
    console.error('Error fetching important memories:', error);
    return [];
  }
};

/**
 * Fetch upcoming tasks for dashboard
 */
export const getUpcomingTasks = async (limit = 3) => {
  try {
    const response = await listTasks();
    if (response.success && response.data.tasks) {
      return response.data.tasks
        .filter((task: any) => {
          const status = task.status?.toLowerCase();
          return status !== 'completed' && status !== 'cancelled';
        })
        .sort((a: any, b: any) => {
          const dateA = new Date(a.due_date || a.createdAt || a.created_at);
          const dateB = new Date(b.due_date || b.createdAt || b.created_at);
          return dateA.getTime() - dateB.getTime();
        })
        .slice(0, limit)
        .map((task: any) => ({
          id: task.id,
          title: task.title || 'Untitled Task',
          date: task.due_date ? formatRelativeDate(task.due_date) : formatRelativeDate(task.createdAt || task.created_at)
        }));
    }
    return [];
  } catch (error) {
    console.error('Error fetching upcoming tasks:', error);
    return [];
  }
};

/**
 * Fetch recent activity across all services
 */
export const getRecentActivity = async (limit = 4): Promise<ActivityItem[]> => {
  try {
    const [conversations, memories, tasks] = await Promise.all([
      getConversations(5, 0).catch(() => ({ success: false, data: { items: [] } })),
      listMemories({ limit: 5, offset: 0 }).catch(() => ({ success: false, data: [] })),
      listTasks().catch(() => ({ success: false, data: { tasks: [] } }))
    ]);

    const activities: ActivityItem[] = [];

    // Add conversation activities
    if (conversations.success && conversations.data.items) {
      conversations.data.items.forEach((conv: any) => {
        activities.push({
          id: `conv-${conv.id}`,
          title: 'Started conversation',
          description: conv.title || 'Untitled Conversation',
          type: 'conversation',
          date: formatRelativeDate(conv.createdAt || conv.created_at),
          createdAt: conv.createdAt || conv.created_at
        });
      });
    }

    // Add memory activities
    if (memories.success && memories.data) {
      memories.data.forEach((memory: any) => {
        activities.push({
          id: `memory-${memory.id}`,
          title: 'Added memory',
          description: memory.content.substring(0, 50) + (memory.content.length > 50 ? '...' : ''),
          type: 'memory',
          date: formatRelativeDate(memory.createdAt || memory.created_at),
          createdAt: memory.createdAt || memory.created_at
        });
      });
    }

    // Add task activities
    if (tasks.success && tasks.data.tasks) {
      tasks.data.tasks.forEach((task: any) => {
        const isCompleted = task.status?.toLowerCase() === 'completed';
        activities.push({
          id: `task-${task.id}`,
          title: isCompleted ? 'Completed task' : 'Created task',
          description: task.title || 'Untitled Task',
          type: isCompleted ? 'completion' : 'task',
          date: formatRelativeDate(task.updatedAt || task.updated_at || task.createdAt || task.created_at),
          createdAt: task.updatedAt || task.updated_at || task.createdAt || task.created_at
        });
      });
    }

    // Sort by date (most recent first) and limit results
    return activities
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
      .slice(0, limit);

  } catch (error) {
    console.error('Error fetching recent activity:', error);
    return [];
  }
};

/**
 * Fetch complete dashboard data
 */
export const getDashboardData = async (): Promise<DashboardData> => {
  try {
    const [stats, recentConversations, importantMemories, upcomingTasks, recentActivity] = await Promise.all([
      getDashboardStats(),
      getRecentConversations(),
      getImportantMemories(),
      getUpcomingTasks(),
      getRecentActivity()
    ]);

    return {
      stats,
      recentConversations,
      importantMemories,
      upcomingTasks,
      recentActivity
    };
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    throw error;
  }
};

/**
 * Format a date as a relative time string
 */
const formatRelativeDate = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMinutes < 60) {
      return diffMinutes <= 1 ? 'Just now' : `${diffMinutes} minutes ago`;
    } else if (diffHours < 24) {
      return diffHours === 1 ? '1 hour ago' : `${diffHours} hours ago`;
    } else if (diffDays < 7) {
      return diffDays === 1 ? '1 day ago' : `${diffDays} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  } catch (error) {
    return 'Unknown';
  }
};

export default {
  getDashboardStats,
  getRecentConversations,
  getImportantMemories,
  getUpcomingTasks,
  getRecentActivity,
  getDashboardData
};
