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
import MainLayout from '../components/layout/MainLayout';
import ProtectedRoute from '../components/auth/ProtectedRoute';

// Page components
import HomePage from '../pages/Home';
import NotFoundPage from '../pages/NotFound';
import DashboardPage from '../pages/Dashboard';
import LoginPage from '../pages/Login';
import RegisterPage from '../pages/Register';
import SettingsPage from '../pages/Settings';
import ConversationsPage from '../pages/Conversations';
import ConversationDetailPage from '../pages/ConversationDetail';
import ChatPage from '../pages/Chat';
import ChatEnhancedPage from '../pages/ChatEnhanced';
import TasksPage from '../pages/Tasks';
import MemoriesPage from '../pages/Memories';
import BookmarksPage from '../pages/Bookmarks';
import CalendarPage from '../pages/Calendar';
import ProjectsPage from '../pages/Projects';
import ContactsPage from '../pages/Contacts';
import ActivityPage from '../pages/Activity';

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
          <Route path="register" element={<RegisterPage />} />
          
          {/* Protected routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="conversations" element={<ConversationsPage />} />
            <Route path="conversations/:id" element={<ConversationDetailPage />} />
            <Route path="chat" element={<ChatPage />} />
            <Route path="chat-enhanced" element={<ChatEnhancedPage />} />
            <Route path="tasks" element={<TasksPage />} />
            <Route path="memories" element={<MemoriesPage />} />
            <Route path="bookmarks" element={<BookmarksPage />} />
            <Route path="calendar" element={<CalendarPage />} />
            <Route path="projects" element={<ProjectsPage />} />
            <Route path="contacts" element={<ContactsPage />} />
            <Route path="activity" element={<ActivityPage />} />
          </Route>
          
          {/* 404 route */}
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;
