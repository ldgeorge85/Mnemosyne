import React, { useEffect } from 'react';
import './App.css';
import { useColorMode } from '@chakra-ui/react';
import AppRouter from './router';
import { useUIStore } from './stores';
import { healthService } from './api';

/**
 * Main application component that sets up the app and syncs theme settings
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
  
  // Check API health on application startup
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await healthService.getHealthStatus();
        console.log('API Health Status:', response.data);
      } catch (error) {
        console.error('API Health Check Failed:', error);
      }
    };
    
    checkHealth();
  }, []);
  
  return <AppRouter />;
}

export default App;
