import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Task, TaskStatus, QuestType, listTasks, startTask, completeTask, TaskCompleteResponse } from '../api/tasks';

interface TaskListProps {
  onCreateClick?: () => void;
}

const TaskList: React.FC<TaskListProps> = ({ onCreateClick }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [completedCount, setCompletedCount] = useState(0);
  const [totalXP, setTotalXP] = useState(0);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await listTasks({ limit: 20 });
      setTasks(response.tasks);
      // Count completed tasks
      const completed = response.tasks
        .filter(t => t.status === TaskStatus.COMPLETED).length;
      setCompletedCount(completed);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

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
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Tasks</h2>
          <p className="text-muted-foreground">Completed: {completedCount} tasks</p>
        </div>
        <Button onClick={onCreateClick}>Create Task</Button>
      </div>

      {tasks.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground">No tasks yet. Create your first task to get started.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {tasks.map(task => (
            <Card key={task.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="space-y-1">
                    <CardTitle className="text-lg">{task.title}</CardTitle>
                    {task.description && (
                      <CardDescription>{task.description}</CardDescription>
                    )}
                    <div className="flex gap-2 mt-2">
                      {task.quest_type && (
                        <Badge className={getQuestTypeBadgeColor(task.quest_type)}>
                          {task.quest_type}
                        </Badge>
                      )}
                      <Badge className={getStatusBadgeColor(task.status)}>
                        {task.status}
                      </Badge>
                      {task.difficulty && (
                        <Badge variant="outline">
                          Difficulty: {task.difficulty}/5
                        </Badge>
                      )}
                      {task.experience_points && task.status === TaskStatus.COMPLETED && (
                        <Badge variant="outline" className="bg-green-50">
                          {task.experience_points} pts
                        </Badge>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {task.status === TaskStatus.PENDING && (
                      <Button 
                        size="sm" 
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
              </CardHeader>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default TaskList;