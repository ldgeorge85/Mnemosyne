import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { createTask, TaskCreate, TaskPriority, QuestType } from '../api/tasks';

interface TaskFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

const TaskForm: React.FC<TaskFormProps> = ({ onSuccess, onCancel }) => {
  const [formData, setFormData] = useState<TaskCreate>({
    title: '',
    description: '',
    priority: TaskPriority.MEDIUM,
    quest_type: QuestType.SOLO,
    difficulty: 3,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    if (!formData.title.trim()) {
      setError('Title is required');
      return;
    }

    try {
      setLoading(true);
      await createTask(formData);
      setFormData({
        title: '',
        description: '',
        priority: TaskPriority.MEDIUM,
        quest_type: QuestType.SOLO,
        difficulty: 3,
      });
      onSuccess?.();
    } catch (err) {
      setError('Failed to create task');
      console.error('Create task error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Create New Task</CardTitle>
        <CardDescription>Add a new task to your list</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="title">Title</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="Enter task title..."
              required
            />
          </div>

          <div>
            <Label htmlFor="description">Description</Label>
            <textarea
              id="description"
              className="w-full min-h-[80px] px-3 py-2 text-sm rounded-md border border-input bg-background"
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Enter task description..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="priority">Priority</Label>
              <select
                id="priority"
                className="w-full px-3 py-2 text-sm rounded-md border border-input bg-background"
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value as TaskPriority })}
              >
                <option value={TaskPriority.LOW}>Low</option>
                <option value={TaskPriority.MEDIUM}>Medium</option>
                <option value={TaskPriority.HIGH}>High</option>
                <option value={TaskPriority.URGENT}>Urgent</option>
              </select>
            </div>

            <div>
              <Label htmlFor="quest_type">Type</Label>
              <select
                id="quest_type"
                className="w-full px-3 py-2 text-sm rounded-md border border-input bg-background"
                value={formData.quest_type}
                onChange={(e) => setFormData({ ...formData, quest_type: e.target.value as QuestType })}
              >
                <option value={QuestType.TUTORIAL}>Learning</option>
                <option value={QuestType.DAILY}>Daily</option>
                <option value={QuestType.SOLO}>Personal</option>
                <option value={QuestType.PARTY}>Team</option>
                <option value={QuestType.RAID}>Group</option>
                <option value={QuestType.EPIC}>Long-term</option>
                <option value={QuestType.CHALLENGE}>Challenge</option>
              </select>
            </div>
          </div>

          <div>
            <Label htmlFor="difficulty">Difficulty: {formData.difficulty}/5</Label>
            <input
              id="difficulty"
              type="range"
              min="1"
              max="5"
              value={formData.difficulty}
              onChange={(e) => setFormData({ ...formData, difficulty: parseInt(e.target.value) })}
              className="w-full"
            />
          </div>

          {error && (
            <div className="text-red-500 text-sm">{error}</div>
          )}

          <div className="flex gap-2 justify-end">
            <Button type="button" variant="outline" onClick={onCancel}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Task'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

export default TaskForm;