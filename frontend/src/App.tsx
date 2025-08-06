import React, { useEffect } from 'react';
import './App.css';
import { useColorMode } from '@chakra-ui/react';
import AppRouter from './router';
import { useUIStore } from './stores';
import { healthService } from './api';
import { AuthProvider } from './contexts/AuthContext';
import ErrorBoundary from './components/common/ErrorBoundary';

/**
 * Main application component with enhanced authentication and error handling
 */
function App() {
  // Get UI state from Zustand store
  const { colorMode: storeColorMode } = useUIStore();
  
  // Get Chakra UI's color mode controls
  const { colorMode, setColorMode } = useColorMode();
  
  // Sync color mode between Zustand store and Chakra UI
  useEffect(() => {
    if (storeColorMode !== colorMode) {
      setColorMode(storeColorMode);
    }
  }, [storeColorMode, colorMode, setColorMode]);
  
  // Check API health on application startup - SILENT implementation with no console output
  useEffect(() => {
    // Use a minimal implementation that will NEVER produce ANY console output
    const silentHealthCheck = () => {
      try {
        // Override console methods temporarily during the health check
        const originalConsoleLog = console.log;
        const originalConsoleWarn = console.warn;
        const originalConsoleError = console.error;
        const originalConsoleInfo = console.info;
        
        // Replace with no-op functions
        console.log = console.warn = console.error = console.info = () => {};
        
        // Simply get the health status - completely silent
        healthService.getStatus()
          .catch(() => {})
          .finally(() => {
            // Restore console methods after a delay to ensure all async operations complete
            setTimeout(() => {
              console.log = originalConsoleLog;
              console.warn = originalConsoleWarn;
              console.error = originalConsoleError;
              console.info = originalConsoleInfo;
            }, 500);
          });
      } catch (error) {
        // Silent error handling - no console output
      }
    };
    
    silentHealthCheck();
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
