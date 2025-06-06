/**
 * Application Router Configuration
 * 
 * This file configures React Router with all application routes
 * and implements route protection based on authentication status.
 */
import React from 'react';
import { 
  BrowserRouter, 
  Routes, 
  Route, 
  Navigate, 
  Outlet
} from 'react-router-dom';

// ENHANCED: Ensure React Router future flags are recognized
// This ensures the flags set in index.html are properly recognized by React Router
const ensureFutureFlags = () => {
  if (window.__reactRouterFutureFlags === undefined) {
    window.__reactRouterFutureFlags = {
      v7_startTransition: true,
      v7_relativeSplatPath: true
    };
  }
};

// Call the function immediately
ensureFutureFlags();

// Layout components
import MainLayout from '../components/layout/MainLayout';

// Page components
import HomePage from '../pages/Home';
import NotFoundPage from '../pages/NotFound';
import DashboardPage from '../pages/Dashboard';
import LoginPage from '../pages/Login';
import SettingsPage from '../pages/Settings';
import ConversationsPage from '../pages/Conversations';
import ConversationDetailPage from '../pages/ConversationDetail';
import ChatPage from '../pages/Chat';

/**
 * Protected Route component that requires authentication
 */
const ProtectedRoute: React.FC = () => {
  // Check if user is authenticated (simplified for now)
  const isAuthenticated = !!localStorage.getItem('token');
  
  // If not authenticated, redirect to login page
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  // Otherwise, render the child routes
  return <Outlet />;
};

/**
 * Main router component that defines all application routes
 */
const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<MainLayout />}>
          <Route index element={<HomePage />} />
          <Route path="login" element={<LoginPage />} />
          
          {/* Protected routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="conversations" element={<ConversationsPage />} />
            <Route path="conversations/:id" element={<ConversationDetailPage />} />
            <Route path="chat" element={<ChatPage />} />
          </Route>
          
          {/* 404 route */}
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;
