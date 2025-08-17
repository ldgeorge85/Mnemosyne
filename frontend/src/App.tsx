import React, { useEffect } from 'react';
import './App.css';
import AppRouter from './router';
import { useUIStore } from './stores';
import { healthService } from './api';
import { AuthProvider } from './contexts/AuthContextSimple';
import ErrorBoundary from './components/common/ErrorBoundarySimple';

/**
 * Main application component with enhanced authentication and error handling
 */
function App() {
  // Get UI state from Zustand store
  const { colorMode } = useUIStore();
  
  // Apply dark mode class to document
  useEffect(() => {
    if (colorMode === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [colorMode]);
  
  // Check API health on application startup
  useEffect(() => {
    // Temporarily disabled console silencing for debugging
    healthService.getStatus()
      .then(() => console.log('API health check: OK'))
      .catch(() => console.log('API health check: Failed'));
  }, []);

  return (
    <ErrorBoundary>
      <AuthProvider>
        <AppRouter />
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
