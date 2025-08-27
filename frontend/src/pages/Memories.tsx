import React, { useState } from 'react';
import MemoryList from '../components/MemoryList';
import MemoryForm from '../components/MemoryForm';
import { Memory } from '../api/memories';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Brain } from 'lucide-react';
// Helper function to format relative time
const formatDistanceToNow = (date: Date, options?: { addSuffix?: boolean }) => {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  let result = '';
  if (days > 0) {
    result = `${days} day${days > 1 ? 's' : ''}`;
  } else if (hours > 0) {
    result = `${hours} hour${hours > 1 ? 's' : ''}`;
  } else if (minutes > 0) {
    result = `${minutes} minute${minutes > 1 ? 's' : ''}`;
  } else {
    result = 'just now';
  }
  
  return options?.addSuffix && result !== 'just now' ? `${result} ago` : result;
};

import { Badge } from '@/components/ui/badge';

type ViewMode = 'list' | 'create' | 'edit' | 'detail';

const Memories: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [selectedMemory, setSelectedMemory] = useState<Memory | null>(null);

  const handleCreateClick = () => {
    setSelectedMemory(null);
    setViewMode('create');
  };

  const handleEditClick = (memory: Memory) => {
    setSelectedMemory(memory);
    setViewMode('edit');
  };

  const handleMemoryClick = (memory: Memory) => {
    setSelectedMemory(memory);
    setViewMode('detail');
  };

  const handleFormSuccess = () => {
    setViewMode('list');
    setSelectedMemory(null);
  };

  const handleBack = () => {
    setViewMode('list');
    setSelectedMemory(null);
  };

  // Detail View Component
  const MemoryDetail = ({ memory }: { memory: Memory }) => (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-2xl">{memory.title}</CardTitle>
            <CardDescription className="mt-2">
              Created {formatDistanceToNow(new Date(memory.created_at), { addSuffix: true })}
              {memory.updated_at !== memory.created_at && (
                <span className="ml-2">
                  • Updated {formatDistanceToNow(new Date(memory.updated_at), { addSuffix: true })}
                </span>
              )}
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => handleEditClick(memory)}>
              Edit
            </Button>
            <Button variant="outline" onClick={handleBack}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <p className="whitespace-pre-wrap">{memory.content}</p>
        </div>

        {memory.tags && memory.tags.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold mb-2">Tags</h3>
            <div className="flex flex-wrap gap-2">
              {memory.tags.map(tag => (
                <Badge key={tag} variant="secondary">
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {memory.importance_score && (
          <div>
            <h3 className="text-sm font-semibold mb-2">Importance Score</h3>
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-secondary rounded-full h-2">
                <div 
                  className="bg-primary rounded-full h-2 transition-all"
                  style={{ width: `${memory.importance_score * 100}%` }}
                />
              </div>
              <span className="text-sm font-medium">
                {Math.round(memory.importance_score * 100)}%
              </span>
            </div>
          </div>
        )}

        {memory.metadata && (
          <div>
            <h3 className="text-sm font-semibold mb-2">Metadata</h3>
            <div className="space-y-1">
              {memory.metadata.source && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Source:</span>
                  <span>{memory.metadata.source}</span>
                </div>
              )}
              {memory.metadata.conversation_id && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Conversation ID:</span>
                  <span className="font-mono text-xs">
                    {memory.metadata.conversation_id}
                  </span>
                </div>
              )}
              {memory.metadata.confidence && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Confidence:</span>
                  <span>{Math.round(memory.metadata.confidence * 100)}%</span>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="pt-4 border-t">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Memory ID:</span>
              <p className="font-mono text-xs mt-1">{memory.id}</p>
            </div>
            <div>
              <span className="text-muted-foreground">Status:</span>
              <p className="mt-1">
                <Badge variant={memory.is_active ? 'default' : 'secondary'}>
                  {memory.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="h-full overflow-auto bg-background">
      <div className="container mx-auto px-4 py-8">
        {viewMode === 'list' && (
          <MemoryList
            onCreateClick={handleCreateClick}
            onMemoryClick={handleMemoryClick}
            onEditClick={handleEditClick}
          />
        )}
      
      {viewMode === 'create' && (
        <div className="space-y-4">
          <Button 
            variant="outline" 
            onClick={handleBack}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Memories
          </Button>
          <MemoryForm
            onSuccess={handleFormSuccess}
            onCancel={handleBack}
          />
        </div>
      )}
      
      {viewMode === 'edit' && selectedMemory && (
        <div className="space-y-4">
          <Button 
            variant="outline" 
            onClick={handleBack}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Memories
          </Button>
          <MemoryForm
            memory={selectedMemory}
            onSuccess={handleFormSuccess}
            onCancel={handleBack}
          />
        </div>
      )}
      
      {viewMode === 'detail' && selectedMemory && (
        <MemoryDetail memory={selectedMemory} />
      )}
      </div>
    </div>
  );
};

export default Memories;