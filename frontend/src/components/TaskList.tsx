import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Plus, Search, CheckCircle, Clock, Target } from 'lucide-react';
import { Task, TaskStatus, QuestType, listTasks, startTask, completeTask, TaskCompleteResponse } from '../api/tasks';

interface TaskListProps {
  onCreateClick?: () => void;
}

const TaskList: React.FC<TaskListProps> = ({ onCreateClick }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [completedCount, setCompletedCount] = useState(0);
  const [totalXP, setTotalXP] = useState(0);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [allTasks, setAllTasks] = useState<Task[]>([]);
  const LIMIT = 20;

  const fetchTasks = async (loadMore = false) => {
    try {
      if (loadMore) {
        setLoadingMore(true);
      } else {
        setLoading(true);
        setSearchQuery('');
      }
      const response = await listTasks({ limit: LIMIT, offset: loadMore ? offset : 0 });
      if (response && response.tasks) {
        if (loadMore) {
          const newTasks = [...allTasks, ...response.tasks];
          setAllTasks(newTasks);
          setTasks(newTasks);
          setOffset(prev => prev + LIMIT);
        } else {
          setAllTasks(response.tasks);
          setTasks(response.tasks);
          setOffset(LIMIT);
        }
        setHasMore(response.tasks.length === LIMIT);
        // Count completed tasks
        const completed = response.tasks
          .filter(t => t.status === TaskStatus.COMPLETED).length;
        setCompletedCount(completed);
      } else {
        console.error('Invalid response format:', response);
        setTasks([]);
        setAllTasks([]);
      }
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
      if (!loadMore) {
        setTasks([]);
        setAllTasks([]);
      }
      setHasMore(false);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  useEffect(() => {
    if (searchQuery) {
      const filtered = allTasks.filter(task => 
        task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (task.description && task.description.toLowerCase().includes(searchQuery.toLowerCase()))
      );
      setTasks(filtered);
    } else {
      setTasks(allTasks);
    }
  }, [searchQuery, allTasks]);

  const handleSearch = () => {
    // Search is handled by the useEffect above
  };

  const handleStartTask = async (taskId: string) => {
    try {
      const updatedTask = await startTask(taskId);
      setTasks(prev => prev.map(t => t.id === taskId ? updatedTask : t));
    } catch (error) {
      console.error('Failed to start task:', error);
    }
  };

  const handleCompleteTask = async (taskId: string) => {
    try {
      const response: TaskCompleteResponse = await completeTask(taskId);
      setTasks(prev => prev.map(t => t.id === taskId ? response.task : t));
      setTotalXP(prev => prev + response.experience_gained);
      
      // Show completion notification
      if (response.experience_gained > 0) {
        console.log(`Task completed: +${response.experience_gained} points`);
      }
    } catch (error) {
      console.error('Failed to complete task:', error);
    }
  };

  const getQuestTypeBadgeColor = (type?: QuestType) => {
    switch (type) {
      case QuestType.TUTORIAL: return 'bg-green-500';
      case QuestType.DAILY: return 'bg-blue-500';
      case QuestType.SOLO: return 'bg-purple-500';
      case QuestType.PARTY: return 'bg-yellow-500';
      case QuestType.RAID: return 'bg-red-500';
      case QuestType.EPIC: return 'bg-orange-500';
      case QuestType.CHALLENGE: return 'bg-pink-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusBadgeColor = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.PENDING: return 'bg-gray-400';
      case TaskStatus.IN_PROGRESS: return 'bg-blue-400';
      case TaskStatus.COMPLETED: return 'bg-green-400';
      default: return 'bg-gray-400';
    }
  };

  if (loading) {
    return <div className="p-4">Loading tasks...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header with stats */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold">Tasks</h2>
          <p className="text-muted-foreground mt-1">Manage your quests and objectives</p>
        </div>
        <Button onClick={onCreateClick}>
          <Plus className="h-4 w-4 mr-2" />
          Create Task
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Tasks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tasks.length}</div>
            <p className="text-xs text-muted-foreground">Active quests</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{completedCount}</div>
            <p className="text-xs text-muted-foreground">
              {tasks.length > 0 ? Math.round((completedCount / tasks.length) * 100) : 0}% success rate
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total XP</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalXP}</div>
            <p className="text-xs text-muted-foreground">Experience earned</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {tasks.filter(t => t.status === TaskStatus.IN_PROGRESS).length}
            </div>
            <p className="text-xs text-muted-foreground">Active now</p>
          </CardContent>
        </Card>
      </div>

      {/* Search Bar */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search tasks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            className="pl-10"
          />
        </div>
        <Button 
          variant="secondary"
          onClick={handleSearch}
          disabled={false}
        >
          Search
        </Button>
      </div>

      {tasks.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground">No tasks yet. Create your first task to get started.</p>
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="space-y-3">
            {tasks.map(task => (
              <Card key={task.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <Badge className={getQuestTypeBadgeColor(task.quest_type)}>
                          {task.quest_type || 'Task'}
                        </Badge>
                        <Badge className={getStatusBadgeColor(task.status)}>
                          {task.status}
                        </Badge>
                        {task.difficulty && (
                          <Badge variant="outline">
                            Difficulty: {task.difficulty}/5
                          </Badge>
                        )}
                      </div>
                      
                      <p className="font-medium mb-1">{task.title}</p>
                      
                      {task.description && (
                        <p className="text-sm text-muted-foreground mb-2">
                          {task.description}
                        </p>
                      )}
                      
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        {task.status === TaskStatus.COMPLETED && (
                          <div className="flex items-center gap-1">
                            <CheckCircle className="w-3 h-3" />
                            Completed
                          </div>
                        )}
                        {task.status === TaskStatus.IN_PROGRESS && (
                          <div className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            In Progress
                          </div>
                        )}
                        {task.status === TaskStatus.PENDING && (
                          <div className="flex items-center gap-1">
                            <Target className="w-3 h-3" />
                            Pending
                          </div>
                        )}
                        {task.experience_points && (
                          <span>
                            {task.experience_points} XP
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex gap-2">
                      {task.status === TaskStatus.PENDING && (
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => handleStartTask(task.id)}
                        >
                          Start
                        </Button>
                      )}
                      {task.status === TaskStatus.IN_PROGRESS && (
                        <Button 
                          size="sm" 
                          variant="default"
                          onClick={() => handleCompleteTask(task.id)}
                        >
                          Complete
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          {hasMore && !searchQuery && (
            <div className="flex justify-center mt-4">
              <Button 
                variant="outline" 
                onClick={() => fetchTasks(true)}
                disabled={loadingMore}
              >
                {loadingMore ? 'Loading...' : 'Load More'}
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default TaskList;