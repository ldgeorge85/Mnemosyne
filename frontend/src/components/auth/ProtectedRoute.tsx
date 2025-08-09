/**
 * Protected Route Component
 * 
 * Uses authentication context to check if user is authenticated
 */
import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

/**
 * Protected Route component that uses auth context
 */
const ProtectedRoute: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  // DEV MODE: Allow access without auth for development
  const DEV_MODE = true; // Toggle this for production
  
  if (DEV_MODE) {
    // In dev mode, always allow access
    return <Outlet />;
  }

  // Show loading state while checking authentication
  if (isLoading) {
    return <div>Loading...</div>;
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Render protected content
  return <Outlet />;
};

export { ProtectedRoute };
export default ProtectedRoute;
