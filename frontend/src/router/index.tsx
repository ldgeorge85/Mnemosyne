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
// import MainLayout from '../components/layout/MainLayout';
import ProtectedRoute from '../components/auth/ProtectedRouteSimple';

// Page components
import DashboardPage from '../pages/DashboardMinimal';
import LoginPage from '../pages/Login';
import RegisterPage from '../pages/Register';
import ChatSimple from '../pages/ChatSimple';


/**
 * Main router component that defines all application routes
 */
const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<LoginPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* Protected routes */}
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        } />
        
        {/* Temporary redirects for other routes */}
        <Route path="/settings" element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        } />
        <Route path="/chat" element={
          <ProtectedRoute>
            <ChatSimple />
          </ProtectedRoute>
        } />
        <Route path="/memories" element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        } />
        
        {/* 404 route */}
        <Route path="*" element={<LoginPage />} />
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;
