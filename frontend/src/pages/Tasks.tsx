import React, { useState } from 'react';
import TaskList from '../components/TaskList';
import TaskForm from '../components/TaskForm';

const TasksPage: React.FC = () => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleCreateSuccess = () => {
    setShowCreateForm(false);
    setRefreshKey(prev => prev + 1); // Force TaskList to refresh
  };

  return (
    <div className="h-full overflow-auto bg-background">
      <div className="container mx-auto px-4 py-8">
        {showCreateForm ? (
          <div className="max-w-2xl mx-auto">
            <TaskForm 
              onSuccess={handleCreateSuccess}
              onCancel={() => setShowCreateForm(false)}
            />
          </div>
        ) : (
          <TaskList 
            key={refreshKey}
            onCreateClick={() => setShowCreateForm(true)}
          />
        )}
      </div>
    </div>
  );
};

export default TasksPage;