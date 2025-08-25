import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { 
  Brain, 
  Search, 
  Plus, 
  Calendar, 
  Star,
  Tag,
  Edit,
  Trash2,
  ChevronRight
} from 'lucide-react';
import { Memory, listMemories, deleteMemory, searchMemories } from '../api/memories';
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

interface MemoryListProps {
  onCreateClick?: () => void;
  onMemoryClick?: (memory: Memory) => void;
  onEditClick?: (memory: Memory) => void;
}

const MemoryList: React.FC<MemoryListProps> = ({ 
  onCreateClick, 
  onMemoryClick,
  onEditClick 
}) => {
  const [memories, setMemories] = useState<Memory[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);

  const fetchMemories = async () => {
    try {
      setLoading(true);
      const response = await listMemories({ limit: 50 });
      if (response.data) {
        setMemories(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch memories:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchMemories();
      return;
    }

    try {
      setSearchLoading(true);
      const response = await searchMemories({ 
        query: searchQuery,
        limit: 50 
      });
      if (response.data) {
        setMemories(response.data);
      }
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleDelete = async (memoryId: string) => {
    if (!confirm('Are you sure you want to delete this memory?')) {
      return;
    }

    try {
      await deleteMemory(memoryId);
      setMemories(prev => prev.filter(m => m.id !== memoryId));
    } catch (error) {
      console.error('Failed to delete memory:', error);
    }
  };

  useEffect(() => {
    fetchMemories();
  }, []);

  const getImportanceColor = (score?: number) => {
    if (!score) return 'bg-gray-500';
    if (score >= 0.8) return 'bg-red-500';
    if (score >= 0.6) return 'bg-orange-500';
    if (score >= 0.4) return 'bg-yellow-500';
    return 'bg-gray-500';
  };

  if (loading) {
    return <div className="p-4">Loading memories...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Brain className="h-6 w-6" />
            Memories
          </h2>
          <p className="text-muted-foreground">
            {memories.length} memories stored
          </p>
        </div>
        <Button onClick={onCreateClick}>
          <Plus className="h-4 w-4 mr-2" />
          New Memory
        </Button>
      </div>

      {/* Search Bar */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search memories..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            className="pl-10"
          />
        </div>
        <Button 
          onClick={handleSearch}
          disabled={searchLoading}
        >
          {searchLoading ? 'Searching...' : 'Search'}
        </Button>
      </div>

      {/* Memory List */}
      {memories.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center">
            <Brain className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-muted-foreground">
              {searchQuery ? 'No memories found matching your search.' : 'No memories yet. Create your first memory!'}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {memories.map(memory => (
            <Card 
              key={memory.id} 
              className="hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => onMemoryClick?.(memory)}
            >
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <CardTitle className="text-lg flex items-center gap-2">
                      {memory.title}
                      {memory.similarity && (
                        <Badge variant="outline" className="ml-2">
                          {Math.round(memory.similarity * 100)}% match
                        </Badge>
                      )}
                    </CardTitle>
                    <CardDescription className="mt-2 line-clamp-2">
                      {memory.content}
                    </CardDescription>
                  </div>
                  <div className="flex gap-1">
                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={(e) => {
                        e.stopPropagation();
                        onEditClick?.(memory);
                      }}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(memory.id);
                      }}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {formatDistanceToNow(new Date(memory.created_at), { addSuffix: true })}
                  </div>
                  
                  {memory.importance_score && (
                    <div className="flex items-center gap-1">
                      <Star className="h-3 w-3" />
                      <Badge 
                        variant="outline" 
                        className={`${getImportanceColor(memory.importance_score)} text-white border-0`}
                      >
                        {Math.round(memory.importance_score * 100)}%
                      </Badge>
                    </div>
                  )}

                  {memory.tags && memory.tags.length > 0 && (
                    <div className="flex items-center gap-1">
                      <Tag className="h-3 w-3" />
                      <div className="flex gap-1">
                        {memory.tags.slice(0, 3).map(tag => (
                          <Badge key={tag} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                        {memory.tags.length > 3 && (
                          <Badge variant="secondary" className="text-xs">
                            +{memory.tags.length - 3}
                          </Badge>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {memory.metadata?.source && (
                  <div className="mt-2">
                    <Badge variant="outline" className="text-xs">
                      Source: {memory.metadata.source}
                    </Badge>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default MemoryList;