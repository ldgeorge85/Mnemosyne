import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { X, Plus } from 'lucide-react';
import { 
  Memory, 
  MemoryCreate, 
  MemoryUpdate, 
  createMemory, 
  updateMemory 
} from '../api/memories';
import useAuthStore from '../stores/authStore';

interface MemoryFormProps {
  memory?: Memory | null;
  onSuccess?: () => void;
  onCancel?: () => void;
}

const MemoryForm: React.FC<MemoryFormProps> = ({ 
  memory, 
  onSuccess, 
  onCancel 
}) => {
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    tags: [] as string[],
    importance_score: 0.5,
    source: 'manual',
  });
  
  const [tagInput, setTagInput] = useState('');

  useEffect(() => {
    if (memory) {
      setFormData({
        title: memory.title || '',
        content: memory.content || '',
        tags: memory.tags || [],
        importance_score: memory.importance_score || 0.5,
        source: memory.metadata?.source || 'manual',
      });
    }
  }, [memory]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    if (!formData.title.trim()) {
      setError('Title is required');
      return;
    }
    
    if (!formData.content.trim()) {
      setError('Content is required');
      return;
    }

    try {
      setLoading(true);
      
      if (memory) {
        // Update existing memory
        const updateData: MemoryUpdate = {
          title: formData.title,
          content: formData.content,
          tags: formData.tags,
          metadata: {
            source: formData.source,
            importance_score: formData.importance_score,
          }
        };
        await updateMemory(memory.id, updateData);
      } else {
        // Create new memory
        if (!user?.id) {
          setError('User not authenticated');
          return;
        }
        
        const createData: MemoryCreate = {
          user_id: user.id,
          title: formData.title,
          content: formData.content,
          tags: formData.tags,
          metadata: {
            source: formData.source,
            importance_score: formData.importance_score,
          }
        };
        await createMemory(createData);
      }
      
      onSuccess?.();
    } catch (err) {
      setError('Failed to save memory');
      console.error('Save memory error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData({
        ...formData,
        tags: [...formData.tags, tagInput.trim()]
      });
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData({
      ...formData,
      tags: formData.tags.filter(tag => tag !== tagToRemove)
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          {memory ? 'Edit Memory' : 'Create New Memory'}
        </CardTitle>
        <CardDescription>
          {memory ? 'Update your existing memory' : 'Store a new memory for future reference'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="title">Title</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="Enter memory title..."
              required
            />
          </div>

          <div>
            <Label htmlFor="content">Content</Label>
            <textarea
              id="content"
              className="w-full min-h-[150px] px-3 py-2 text-sm rounded-md border border-input bg-background"
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              placeholder="Enter memory content..."
              required
            />
          </div>

          <div>
            <Label htmlFor="tags">Tags</Label>
            <div className="flex gap-2 mb-2">
              <Input
                id="tags"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddTag();
                  }
                }}
                placeholder="Add tags..."
              />
              <Button
                type="button"
                onClick={handleAddTag}
                size="icon"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.tags.map(tag => (
                <Badge key={tag} variant="secondary" className="gap-1">
                  {tag}
                  <button
                    type="button"
                    onClick={() => handleRemoveTag(tag)}
                    className="ml-1 hover:text-destructive"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
          </div>

          <div>
            <Label htmlFor="importance">
              Importance: {Math.round(formData.importance_score * 100)}%
            </Label>
            <input
              id="importance"
              type="range"
              min="0"
              max="100"
              value={formData.importance_score * 100}
              onChange={(e) => setFormData({ 
                ...formData, 
                importance_score: parseInt(e.target.value) / 100 
              })}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Low</span>
              <span>Medium</span>
              <span>High</span>
            </div>
          </div>

          <div>
            <Label htmlFor="source">Source Type</Label>
            <select
              id="source"
              className="w-full px-3 py-2 text-sm rounded-md border border-input bg-background"
              value={formData.source}
              onChange={(e) => setFormData({ ...formData, source: e.target.value })}
            >
              <option value="manual">Manual Entry</option>
              <option value="conversation">Conversation</option>
              <option value="document">Document</option>
              <option value="task">Task</option>
              <option value="note">Note</option>
              <option value="reflection">Reflection</option>
            </select>
          </div>

          {error && (
            <div className="text-red-500 text-sm">{error}</div>
          )}

          <div className="flex gap-2 justify-end">
            <Button type="button" variant="outline" onClick={onCancel}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Saving...' : memory ? 'Update Memory' : 'Create Memory'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

export default MemoryForm;