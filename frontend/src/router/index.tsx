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
  Route
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
import AppShell from '../layouts/AppShell';
import ProtectedRoute from '../components/auth/ProtectedRouteSimple';

// Page components
import DashboardPage from '../pages/DashboardMinimal';
import LoginPage from '../pages/Login';
import RegisterPage from '../pages/Register';
import ChatEnhanced from '../pages/ChatEnhanced';
import TasksPage from '../pages/Tasks';
import MemoriesPage from '../pages/Memories';
import ReceiptsPage from '../pages/ReceiptsSimple';


/**
 * Main router component that defines all application routes
 */
const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes (no AppShell) */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* Protected routes with AppShell */}
        <Route element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }>
          <Route path="/" element={<ChatEnhanced />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/chat" element={<ChatEnhanced />} />
          <Route path="/tasks" element={<TasksPage />} />
          <Route path="/memories" element={<MemoriesPage />} />
          <Route path="/receipts" element={<ReceiptsPage />} />
          <Route path="/settings" element={<DashboardPage />} />
        </Route>
        
        {/* 404 route */}
        <Route path="*" element={<LoginPage />} />
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;
