import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import SimpleSidebar from './SimpleSidebar';
import { Button } from '@/components/ui/button';
import { Menu } from 'lucide-react';

/**
 * AppShell - Main application layout wrapper
 * Provides persistent sidebar navigation and content area
 */
const AppShell: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  return (
    <div className="h-screen flex bg-background">
      {/* Desktop Sidebar */}
      <div className={`hidden md:block ${sidebarOpen ? 'w-64' : 'w-16'} transition-all duration-200`}>
        <SimpleSidebar 
          isOpen={sidebarOpen} 
          onToggle={() => setSidebarOpen(!sidebarOpen)}
          onClose={() => setMobileSidebarOpen(false)}
        />
      </div>

      {/* Mobile Sidebar Overlay */}
      {mobileSidebarOpen && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          <div 
            className="fixed inset-0 bg-black/50" 
            onClick={() => setMobileSidebarOpen(false)}
          />
          <div className="relative w-64 bg-background">
            <SimpleSidebar 
              isOpen={true} 
              onToggle={() => {}}
              onClose={() => setMobileSidebarOpen(false)}
            />
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile Header */}
        <div className="md:hidden border-b p-4 flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setMobileSidebarOpen(!mobileSidebarOpen)}
          >
            <Menu className="h-5 w-5" />
          </Button>
          <h1 className="text-xl font-bold">Mnemosyne</h1>
        </div>

        {/* Page Content */}
        <main className="flex-1 overflow-hidden">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AppShell;