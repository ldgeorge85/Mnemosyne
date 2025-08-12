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

  // DEV MODE: Disabled - require authentication
  const DEV_MODE = false; // Authentication is now working!

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
