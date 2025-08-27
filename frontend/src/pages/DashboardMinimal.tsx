import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useNavigate } from 'react-router-dom';
import { listMemories } from '../api/memories';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [memoryCount, setMemoryCount] = useState<number | null>(null);

  useEffect(() => {
    // Fetch memory count
    listMemories({ limit: 1 })
      .then(memories => {
        setMemoryCount(memories.length);
      })
      .catch(err => {
        console.error('Failed to fetch memories:', err);
        setMemoryCount(0);
      });
  }, []);

  return (
    <div className="h-full overflow-auto bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader>
              <CardTitle>Tasks</CardTitle>
              <CardDescription>Quests and achievements</CardDescription>
            </CardHeader>
            <CardContent>
              <Button className="w-full" onClick={() => navigate('/tasks')}>
                View Tasks
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Memories</CardTitle>
              <CardDescription>Your stored memories and thoughts</CardDescription>
            </CardHeader>
            <CardContent>
              {memoryCount === null ? (
                <p className="text-sm text-muted-foreground">Loading...</p>
              ) : memoryCount === 0 ? (
                <p className="text-sm text-muted-foreground">No memories yet</p>
              ) : (
                <div className="space-y-2">
                  <p className="text-2xl font-bold">{memoryCount}</p>
                  <Button 
                    className="w-full" 
                    variant="outline"
                    onClick={() => navigate('/memories')}
                  >
                    View Memories
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Chat</CardTitle>
              <CardDescription>Interact with your AI assistant</CardDescription>
            </CardHeader>
            <CardContent>
              <Button className="w-full" onClick={() => navigate('/chat')}>
                Start Chat
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Agents</CardTitle>
              <CardDescription>Philosophical agents for reflection</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Coming soon</p>
            </CardContent>
          </Card>
        </div>

        <div className="mt-8">
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="flex gap-4">
              <Button variant="outline">Add Memory</Button>
              <Button variant="outline">Search</Button>
              <Button variant="outline">Settings</Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;